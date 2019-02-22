import re
from Tkinter import *
from textwrap import wrap
import tkFileDialog
import math
from CAN_DBC import *
from prettytable import PrettyTable

class DBCParse:

	def __init__(self,file,Node):
		self.dbcFilePath = file
		self.Messages = {}
		self.ECU_Name = Node
		#RxMsgs = RxMessages
		self.readMessages()
		self.readSignals()
		self.readSignalsValTable()
		
	def readMessages(self):
		inputfile, lines = self.prepareRead()
		for line in lines: 
			if 'BO_ ' in line :  
				searchMsg = re.search(r'BO_ +(\d*) (\w*): \d* (\w*)',line)
				if searchMsg != None:
					#print line #interpretation of the line
					#1- Message ID
					#2- Message Name
					#3- Message Tx Node
					MessageID = searchMsg.group(1)
					MessageName = searchMsg.group(2)
					MessageTxNode = searchMsg.group(3)
					#parse messages here:
					#execlude Vector message because the ID will be 3221225472 which has Vector independent signal message
					if int(MessageID) < 500000:
						self.Messages[MessageName] = Message(MessageName,MessageID)
						self.Messages[MessageName].Tx_Node = MessageTxNode
						if(MessageTxNode == self.ECU_Name):
							self.Messages[MessageName].Type = "Tx"
						else:
							self.Messages[MessageName].Type = "Rx"

		inputfile.close()
	def readSignals(self):
		inputfile, lines = self.prepareRead()
		for line in lines:
			if 'BO_ ' in line:  #Message start
				searchMsg = re.search(r'BO_ +(\d*) (\w*): \d* (\w*)',line)
			elif line.startswith(' SG_ ') :
				#print('signal line found')
				if int(searchMsg.group(1)) > 500000:
					continue
				searchSig = re.search( r'\sSG_\s+(\w*)\s+(\w*\d*)\s*:\s*(\-*\d+\.*\d*)\|(\-*\d+\.*\d*)\@(\-*\d+\.*\d*)([+-])\s*\((\-*\d+\.*\d*)\,(\-*\d+\.*\d*)\)\s*\[(\-*\d+\.*\d*)\|(\-*\d+\.*\d*)\]\s*(.*)\n', line)
				if searchSig:
					#print line #interpretation of the line
					#1- signal name
					#2- Mux (M = multiplexor , m0 first mux, m1 second mux ..etc)
					#3- number: if intel (start-bit directly) if motorola (number+1-length)(1) 
					#4- number: lenthBits(2) 
					#5- number: Intel if 1 Motorola if 0
					#6- signed if -  unsigned if +
					#7- Number: factor
					#8- number: offset
					#9- number: min
					#10- number: max 
					#11- "unit symbol" : (,,,) receivers
					#parse signals here:
					self.Messages[searchMsg.group(2)].AddSig(searchSig.group(1))
					self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].signalInMessage = searchMsg.group(2)
					self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].factor = float(searchSig.group(7))
					self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].offset = int(searchSig.group(8))
					self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].max = float(searchSig.group(10))
					self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].min = float(searchSig.group(9))
					self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].len = int(searchSig.group(4))
					if searchSig.group(2): #in case message is multiplexed
						self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].Muxed = searchSig.group(8)
					self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].Signal_Type = "Intel" if int(searchSig.group(5)) else "Motorola"
					if int(searchSig.group(5)):
						self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].Start_Bit = searchSig.group(3)
					else: #if motorla the sart bit will be calculated differently in this case
						self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].Start_Bit = str(-int(searchSig.group(3)) - 1 + int(searchSig.group(4)))
					self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].unit = searchSig.group(11)
					self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].c_type = self.SignAndNumOfBytes(float(searchSig.group(7)),float(searchSig.group(8)),float(searchSig.group(4)),searchSig.group(6))
					#print('Signal Found')
		inputfile.close()
#This interface reads the value table for signals within messages associated with a certain value table
	def readSignalsValTable(self):
		inputfile , lines = self.prepareRead()
		for line in lines:
			if line.startswith('VAL_ ') :  # this section will be used if you want to Enum from Value Table
				lineSearch = re.search(r'VAL_ +(\d*) (\w*) (.*) ;',line)
				#1 Message ID
				Message_ID = lineSearch.group(1)
				#2 Signal Name
				Signal_Name = lineSearch.group(2)
				#3 Descending Enum values and thier textual representation
				ValueTable = re.findall(r'"[\w*\s*]+"|\-*\d+',lineSearch.group(3))
				for message in self.Messages: #loop on all Messages
					if self.Messages[message].ID == lineSearch.group(1): #find the message of the signal
						if self.Messages[message].signals.get(Signal_Name): #check if signal with valuetable exists in the crossponding message
							self.Messages[message].signals[Signal_Name].isValTable = ValueTable.__len__()/2 #mark it as signal with value Table
							for idx,value in zip(*[iter(ValueTable)]*2):
								self.Messages[message].signals[Signal_Name].valTable[idx] = value
								
							
				#print(ValueTable)
		inputfile.close()
#print function for debugging and insure proper DBC interpretation		
	def printdbc(self):
		for message in self.Messages:
			print("\n\n"+"Message name:  "+message+"\n")
			#prepare the table for the signals
			t = PrettyTable(['Signal Name', 'StartBit','Type','ValueTable'])
			for signal in self.Messages[message].signals:
				if self.Messages[message].signals[signal].isValTable:
					valTable = ""
					for value in sorted(self.Messages[message].signals[signal].valTable):
						valTable += str(value)+"->"+self.Messages[message].signals[signal].valTable[value]+"  "
				else:
					valTable = "None"
				t.add_row([signal, self.Messages[message].signals[signal].Start_Bit,\
				self.Messages[message].signals[signal].c_type,\
				valTable])
			print t
#support functions
	def prepareRead(self):
		inputfile  = open(self.dbcFilePath,'r')
		#Number_Of_Lines = len(self.inputfile.readlines())  # Know how many lines inside the DBC file
		inputfile.seek(0,0)  # rest cursor at the beggining of the input file
		lines = inputfile.readlines() #read all lines in file sarting from 0,0 position
		return inputfile ,lines
	def SignAndNumOfBytes(self,Factor,Offset,RawNumOfBits,sign):
		MinPhyVal = abs(Offset) -1 #getting the unsigned positive of negative signed number
		MaxPhyVal = ((pow(2,RawNumOfBits)-1)*Factor) + Offset
		if (sign == '-'):
			signed = 1
		else:
			signed = 0
		if ((MinPhyVal) > MaxPhyVal):
			PysNumBits = int(math.ceil(math.log((MinPhyVal+1),2)+signed))
		else:
			PysNumBits = int(math.ceil(math.log((MaxPhyVal+1),2)+signed))
		mod = PysNumBits%8
		incbytes = PysNumBits/8
		NumOfBytes = incbytes if mod == 0 else incbytes+1
		if((NumOfBytes <=1) and (signed == 0)):
			sigtype = "uint8"
		elif ((NumOfBytes <=1) and (signed == 1)):
			sigtype = "sint8"
		elif ((NumOfBytes <=2) and (signed == 0)):
			sigtype = "uint16"
		elif ((NumOfBytes <=2) and (signed == 1)):
			sigtype = "sint16"
		elif ((NumOfBytes <= 4) and (signed == 0)):
			sigtype = "uint32"
		elif ((NumOfBytes <= 4) and (signed == 1)):
			sigtype = "sint32"
		elif ((NumOfBytes <= 8) and (signed == 0)):
			sigtype = "uint64"
		elif ((NumOfBytes <= 8) and (signed == 1)):
			sigtype = "sint64"
		else:
			print "Error occured while interpreting the DBC"
			sys.exit()
		return sigtype

if __name__== "__main__":
#Selecting DBC file ------------------------------------------------------------------
	root = Tk()
	root.withdraw()
	# root.fileName = tkFileDialog.askopenfilename(filetypes=[("Dataset files","*.dbc")  ],
									# title='Choose a Database file (.dbc format)')
	root.fileName = 'RIV_ADAS_Mule1_v8.dbc'
	if root.fileName == None:
		sys.exit()
#---------------------------------------------------------------------------------------
	DBC_Name = root.fileName 
#	Create Header File
	HeaderFile = open('COMH.h','w')
#	Create Source File
	SourceFile = open('COMH.c','w')
	DBCParsObj = DBCParse(DBC_Name,'PARK')
	DBCParsObj.printdbc()
