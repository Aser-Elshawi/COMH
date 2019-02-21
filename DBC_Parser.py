import re
from Tkinter import *
from textwrap import wrap
import tkFileDialog
import math
from CAN_DBC import *


class DBCParse:

	def __init__(self,file,Node):
		self.dbcFile = file
		self.Messages = {}
		self.ECU_Name = Node
		#RxMsgs = RxMessages
		self.readMessages()
		self.readSignals()
		
	def readMessages(self):
		self.prepareRead()
		self.lines = self.inputfile.readlines()
		for line in self.lines: 
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

		self.doneRead()
	def readSignals(self):
		self.prepareRead()
		self.lines = self.inputfile.readlines()
		for line in self.lines:
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
					self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].factor = searchSig.group(7)
					self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].offset = searchSig.group(8)
					self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].max = searchSig.group(10)
					self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].min = searchSig.group(9)
					self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].len = searchSig.group(4)
					if searchSig.group(2): #in case message is multiplexed
						self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].Muxed = searchSig.group(8)
					self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].Signal_Type = "Intel" if searchSig.group(5) else "Motorola"
					if searchSig.group(5):
						self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].Start_Bit = searchSig.group(3)
					else: #if motorla the sart bit will be calculated differently in this case
						self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].Start_Bit = str(int(searchSig.group(3)) + 1 + int(searchSig.group(4)))
					self.Messages[searchMsg.group(2)].signals[searchSig.group(1)].unit = searchSig.group(11)
					#print('Signal Found')
		self.doneRead()
	def printdbc(self):
		for message in self.Messages:
			print("\n\n"+"Message name:  "+message)
			for signal in self.Messages[message].signals:
				print("Signal "+signal+"StartBit: "+self.Messages[message].signals[signal].Start_Bit)
		
	def prepareRead(self):
		self.inputfile  = open(self.dbcFile,'r')
		self.Number_Of_Lines = len(self.inputfile.readlines())  # Know how many lines inside the DBC file
		self.inputfile.seek(0,0)  # rest cursor at the beggining of the input file
	def doneRead(self):
		self.inputfile.close()


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
