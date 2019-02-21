#!/usr/bin/python

import re
from Tkinter import *
from textwrap import wrap
import tkFileDialog
import math
MY_Node = "PARK"	  # Change your TX Node 
# [PhysicalValue] = ([RawValue] * [Factor]) + Offset
def SignAndNumOfBytes(Factor,Offset,RawNumOfBits):
	MinPhyVal = abs(Offset) -1 #getting the unsigned positive of negative signed number
	MaxPhyVal = ((pow(2,RawNumOfBits)-1)*Factor) + Offset
	if (Offset < 0):
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
	if((NumOfBytes ==1) and (signed == 0)):
		sigtype = "uint8"
	elif ((NumOfBytes ==1) and (signed == 1)):
		sigtype = "sint8"
	elif ((NumOfBytes ==2) and (signed == 0)):
		sigtype = "uint16"
	elif ((NumOfBytes ==2) and (signed == 1)):
		sigtype = "sint16"
	elif ((NumOfBytes > 2) and (signed == 0)):
		sigtype = "uint32"
	elif ((NumOfBytes >2) and (signed == 1)):
		sigtype = "sint32"
	else:
		sys.exit()
	return sigtype

#This function will define Enums as type of signals in the OutPutFile 
#and in signals_array hash as index and the message ID as value
def Get_Enums(DBCfileObject,OutPutFile,signals_array):
	with open(DBCfileObject) as openfileobject:
		for line in openfileobject:
			if line.startswith('VAL_ ') :  # this section will be used if you want to Enum from Value Table
				Signal_Enum = re.search(r'VAL_ +(\d*) (\w*) (.*) ;',line)
				enum = Signal_Enum.group(2)
				signals_array["MsgID"][enum] = Signal_Enum.group(1)
				#enum_values = Signal_Enum.group(3).split(' ')
				enum_values = re.findall(r'"[\w*\s*]+"|\-*\d+',Signal_Enum.group(3))
				enum_length = enum_values.__len__()
				message_output = "\n// Message ID = "+str(hex(int(Signal_Enum.group(1))))+"\n"
				if(signals_array["frac"].get(enum) != None):
					message_output += "//Note: this signal is multiplied by "+signals_array["frac"][enum] + " for resolution\n"
				message_output += "typedef enum " +enum+"_E"+ "\n{" +"\n"
				if(signals_array["factor"].get(enum) != None):
					factor = signals_array["factor"][enum]
					offset = signals_array["offset"][enum]
				else:
					factor = 1
					offset = 0
				for value in reversed(range(0,enum_length,2)):
					if(enum == signals_array["MsgName"].get(enum)):
						enumNewName = 'Sig_'
					else:
						enumNewName = ''
					newnumb = round(int(enum_values[value].strip(r'"'))*factor + offset,len(str(factor)) -2)
					if (factor<1):
						modnum = str(int(newnumb * pow(10,(len(str(factor)) -2)))) #number after adapting resolution
						signals_array["frac"][enum] = str(pow(10,(len(str(factor)) -2))) #the 10th multiplier
					else:
						modnum = str(int(newnumb))#str(int(newnumb * pow(10,(len(str(factor)) -2)))) #number after adapting resolution
					if(value == 0):
						message_output += "\tVAL_"+enum+'_'+enum_values[value + 1].strip('"').replace (" ", "_") + " = " + modnum +"\n}COMH_"+enumNewName+enum.upper()+"_T;\n\n"
					else:
						message_output += "\tVAL_"+enum+'_'+enum_values[value +1].strip('"').replace (" ", "_")+" = "+ modnum +",\n"
				OutPutFile.write(message_output)
			if line.startswith("CM_ SG_ ") :
				search_comm = re.search(r'CM_ SG_ (\d*)\s*(\w*|\d*)\s*"(.*)\"?;?',line)
				#signals_array["comment"][search_comm.group(2)] = search_comm.group(3)
	openfileobject.close()
	return;

def GetEnumTypes(DBCfileObject,OutPutFile,signals_array):
	with open(DBCfileObject) as openfileobject:
		for line in openfileobject:
			if line.startswith('VAL_ ') :  # this section will be used if you want to Enum from Value Table
				Signal_Enum = re.search(r'VAL_ +(\d*) (\w*) (.*) ;',line)
				enum = Signal_Enum.group(2)
				enum_values = Signal_Enum.group(3).split(' ')
				signals_array["MsgID"][enum] = Signal_Enum.group(1)
				enum_length = enum_values.__len__()
				if(signals_array["factor"].get(enum) != None):
					factor = signals_array["factor"][enum]
					offset = signals_array["offset"][enum]
				else:
					factor = 1;
					offset = 0;
						
			if line.startswith("CM_ SG_ ") :
				search_comm = re.search(r'CM_ SG_ (\d*)\s*(\w*|\d*)\s*"([^"]*)(\"?;?)',line)
				if(search_comm != None):
					signals_array["comment"][search_comm.group(2)] = search_comm.group(3)
	openfileobject.close()
def GetGlobValues(DBCfileObject,signals_array):
	with open(DBCfileObject) as openfileobject:
		for line in openfileobject:
			if line.startswith('BO_ ') :  # this section will be used if you want to Enum from Value Table
				SR = re.search(r'BO_ +(\d*) (\w*): \d* (\w*)',line)
				if SR != None:
					Tx_Node = SR.group(3)
					Message_Name = SR.group(2)
					Message_ID = SR.group(1)
					if (Tx_Node == MY_Node):
						msgs_array["TxMSG"][Message_Name] = Message_ID
			if line.startswith(" SG_ ") :
				RS = re.search( r'\sSG_\s+(\w*)\s+(\w*\d*)\s*:\s*(\-*\d+\.*\d*)\|(\-*\d+\.*\d*)\@(\-*\d+\.*\d*)([+-])\s*\((\-*\d+\.*\d*)\,(\-*\d+\.*\d*)\)\s*\[(\-*\d+\.*\d*)\|(\-*\d+\.*\d*)\]\s*(.*)\n', line)
				Signal_Name = RS.group(1)
				factor = float(RS.group(7))
				offset = float(RS.group(8))
				RawNumOfBits = int(RS.group(4))
				Rx_Node=RS.group(11)
				maxval = RS.group(10)
				minval = RS.group(9)
				#initval = RS.group()
				Pysicalsignaltype = SignAndNumOfBytes(factor,offset,RawNumOfBits)
				signals_array["factor"][Signal_Name] = factor
				signals_array["offset"][Signal_Name] = offset
				signals_array["MsgName"][Signal_Name] = Message_Name
				signals_array["max"][Signal_Name] = maxval
				signals_array["min"][Signal_Name] = minval
				if(factor<1):
					signals_array["frac"][Signal_Name] = str(pow(10,(len(str(factor)) -2))) #the 10th multiplier
				if MY_Node in Rx_Node or MY_Node in Tx_Node:
					inits["str"][Message_Name]= '\tCOMH_' + Message_Name.upper() + '_T '+Message_Name
					signals_array["RawNumOfBits"][Signal_Name] = RawNumOfBits
					if MY_Node in Rx_Node :
						msgs_array["RxMSG"][Message_Name] = Message_ID
					else: # MY_Node in Tx_Node 
						msgs_array["TxMSG"][Message_Name] = Message_ID
					
	openfileobject.close()
	return;
# Selecting DBC file ------------------------------------------------------------------
root = Tk()
root.withdraw()
root.fileName = tkFileDialog.askopenfilename(filetypes=[("Dataset files","*.dbc")  ],
								  title='Choose a Database file (.dbc format)')
if root.fileName == None:
	sys.exit()
#---------------------------------------------------------------------------------------
#Golbal variables

Message_Name_only = ""
signals_array = {} #contains signals with enum typedef only
signals_array["MsgID"] = {}
signals_array["MsgName"] = {}
signals_array["comment"] = {}
signals_array["factor"] ={}
signals_array["offset"] ={}
signals_array["RawNumOfBits"] ={}
signals_array["Signal_Type"] = {}
signals_array["frac"] = {}
signals_array["max"] = {}
signals_array["min"] = {}

inits = {}
inits["str"] = {}
inits["setgetfun"] = {}
inits["WRfun"] = {}
MyNode_msg_to_signals = {}
msgs_array = {}
msgs_array["TxMSG"] = {}
msgs_array["RxMSG"] ={}
msgs_array["MsgID"] = {}

#signals_array["MsgID"][signalname] = message id
#signals_array["MsgName"][signalname] = message name
#signals_array["comment"][signalname] = signal comment
DBC_Name = root.fileName   # Change the dbc name  
#---------------------------------------------------------------------------------------
OutPutFile = open('ComhGen.h','w')
#This function will write the signals_array hash as index and the message ID as value
GetGlobValues(DBC_Name,signals_array)
GetEnumTypes(DBC_Name,OutPutFile,signals_array)
inputfile  = open(DBC_Name,'r')
Number_Of_Lines = len(inputfile.readlines())  # Know how many lines inside the DBC file
inputfile.seek(0,0)  # rest cursor at the beggining of the input file

temp = inputfile.readline() 
temp_old = temp
	#print (value)
	#OutPutFile.write(value)

for line in range(1,Number_Of_Lines): 
	value = "" 
	#if 'BA_ ' in temp :
	 #value = "Transmission_Type_Line_Is_Removed\n"
	 #OutPutFile.write(value)
	if 'BO_ ' in temp :  
		Message_Name = re.search(r'BO_ +(\d*) (\w*): \d* (\w*)',temp)
		if Message_Name != None:
			Tx_Node = Message_Name.group(3)
			Message_Name_only = Message_Name.group(2)
			Message_ID = Message_Name.group(1)
			msgs_array["MsgID"][Message_Name_only] = Message_ID
			print ("/*********************************************************************/")
			print ("/*																   */")
			print ("/*					  Message_Name:%s						  */"%Message_Name_only)
			print ("/*					  Tx_Node:%s											 */"%Tx_Node)
			print ("/*********************************************************************/\n")
			value = "typedef struct " +Message_Name_only+"_S"+ "\n{" +"\n"
			OutPutFile.write(value)
	elif temp.startswith(' SG_ ') :
	  RS = re.search( r'\sSG_\s+(\w*)\s+(\w*\d*)\s*:\s*(\-*\d+\.*\d*)\|(\-*\d+\.*\d*)\@(\-*\d+\.*\d*)([+-])\s*\((\-*\d+\.*\d*)\,(\-*\d+\.*\d*)\)\s*\[(\-*\d+\.*\d*)\|(\-*\d+\.*\d*)\]\s*(.*)\n', temp)
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
	  Signal_Name = RS.group(1)
	  factor = float(RS.group(7))
	  offset = float(RS.group(8))
	  RawNumOfBits = int(RS.group(4))
	  Rx_Node=RS.group(11)
	  Pysicalsignaltype = SignAndNumOfBytes(factor,offset,RawNumOfBits)
	  if(Signal_Name == signals_array["MsgName"].get(Signal_Name)):
			enumNewName = 'Sig_'
	  else:
			enumNewName = ''
	  if MY_Node in Rx_Node or MY_Node in Tx_Node:
		  inits["str"][Message_Name_only]= '\tCOMH_' + Message_Name_only.upper() + '_T '+Message_Name_only
		  if(signals_array["comment"].get(Signal_Name) != None):
		   x = signals_array["comment"].get(Signal_Name)
		   value = "\t"+'/*\n\t *\t'+ '\n \t *\t'.join(wrap(x, width=50))+"\n\t */\n"
		  try:
		   if (signals_array["MsgID"].get(Signal_Name) != None):
			value += "\tCOMH_"+enumNewName+Signal_Name.upper()+ "_T " +Signal_Name +  " ;\n"
			Signal_Type = Signal_Name.upper() + "_T"
		   else:
			value += "\t"+ Pysicalsignaltype + " " + Signal_Name +  " ;\n"
			Signal_Type = Pysicalsignaltype #TO be used by the comh setter and getter
		  except:
		   sys.exit(os.EX_SOFTWARE)
		  Signal_Type = Signal_Type if (Signal_Type in ('uint8','sint8','sint16','uint16','uint32','sint32')) else 'COMH_' + Signal_Type
		  signals_array["Signal_Type"][Signal_Name] = Signal_Type
	  if MY_Node in Rx_Node :
	   if(signals_array["comment"].get(Signal_Name) != None):
			x = signals_array["comment"].get(Signal_Name)
			if(signals_array["frac"].get(Signal_Name) != None):
				x += "Please note that this signal is multiplied by "+signals_array["frac"][Signal_Name] + " for resolution"
			ComH_Function = "\t"+'/*\n\t *\t'+ '\n \t *\t'.join(wrap(x, width=50))+"\n\t */\n"
	   else:
			if(signals_array["frac"].get(Signal_Name) != None):
				x = "//Please note that this signal is multiplied by "+signals_array["frac"][Signal_Name] + " for resolution\n"
			else:
				x = ""
			ComH_Function = x
	   if(RawNumOfBits == 1):
		ComH_Function += "FUNC(Std_ReturnType, RTE_COMH_APPL_CODE)" + " COMH_Is" + Signal_Name +"("+Signal_Type+" *value)\n" +"{\n\t"
	   else:
	    ComH_Function += "FUNC(Std_ReturnType, RTE_COMH_APPL_CODE)" + " COMH_Get" + Signal_Name +"("+Signal_Type+" *value)\n" +"{\n"
	   #The Get function
	   ComH_Function += '\tStd_ReturnType data_state = E_NOT_OK;\n'
	   ComH_Function += '\tif(value != NULL_PTR){\n'
	   ComH_Function += '\t\tif ('+Message_Name_only+'_ValidityStructure.'+Signal_Name+' == SIGNAL_VALID)\n'
	   ComH_Function += '\t\t{\n'
	   ComH_Function += '\t\t\tdata_state = E_OK;\n'
	   ComH_Function += '\t\t\t*value = '+Message_Name_only +"_MSG."+ Signal_Name+';\n'
	   ComH_Function += '\t\t}\n'
	   ComH_Function += '\t}\n'
	   ComH_Function += "\treturn data_state;\n}\n" # Create Getter For Signal
	   if(Message_Name_only in MyNode_msg_to_signals):
	    MyNode_msg_to_signals[Message_Name_only] += ','+Signal_Name
	   else:                                       
	    MyNode_msg_to_signals[Message_Name_only] = Signal_Name 
	   print(ComH_Function)
	  elif MY_Node in Tx_Node :
	   ComH_Function = ""
	   #if(signals_array["frac"].get(Signal_Name) != None):
	   if(signals_array["comment"].get(Signal_Name) != None):
			x = signals_array["comment"].get(Signal_Name)
			if(signals_array["frac"].get(Signal_Name) != None):
				x += "Please note that this signal is multiplied by "+signals_array["frac"][Signal_Name] + " for resolution"
			ComH_Function = "\t"+'/*\n\t *\t'+ '\n \t *\t'.join(wrap(x, width=50))+"\n\t */\n"
	   else:
			if(signals_array["frac"].get(Signal_Name) != None):
				ComH_Function = "//Please note that this signal is multiplied by "+signals_array["frac"][Signal_Name] + " for resolution\n"
	   #The Set function
	   ComH_Function += "FUNC(Std_ReturnType, RTE_COMH_APPL_CODE)"+ " COMH_Set" + Signal_Name + "("+Signal_Type+" New_"+Signal_Name+")\n" 
	   ComH_Function += "{\n"
	   ComH_Function += "\tStd_ReturnType data_state = E_NOT_OK;\n"
	   ComH_Function += "\tif((New_"+Signal_Name+" <= "+Signal_Name+"_MaxVal) && (New_"+Signal_Name+" >= "+Signal_Name+"_MinVal))\n"
	   ComH_Function += "\t{\n"
	   ComH_Function += "\t\tdata_state = E_OK;\n"
	   ComH_Function += "\t\t" + Message_Name_only +"_MSG." + Signal_Name + " = New_"+Signal_Name + ";\n"
	   ComH_Function += "\t}\n"
	   ComH_Function += "\treturn data_state;\n"
	   ComH_Function += "}\n" # Create Setter for Signal
	   if(Message_Name_only in MyNode_msg_to_signals):
	    MyNode_msg_to_signals[Message_Name_only] += ','+Signal_Name
	   else:
	    MyNode_msg_to_signals[Message_Name_only] = Signal_Name 
	   print(ComH_Function)
	  else :
	   ComH_Function = ""
	  OutPutFile.write(value)
	elif temp_old.startswith(' SG_ ') :
	 if temp == "\n" :
	  value = "}" +"COMH_"+Message_Name_only.upper() +"_T"+";" +"\n\n"
	  OutPutFile.write(value)
	temp_old=temp  
	temp = inputfile.readline()  
inputfile.close();
	#print (value)
	#OutPutFile.write(value)
#-------------------------   Generate Enum types                      -------------------------------------------------------
Get_Enums(DBC_Name,OutPutFile,signals_array)
#-------------------------   Generate Message RTE reader & Writers    -------------------------------------------------------
for MSG_NM in msgs_array["RxMSG"]:
	print r'STATIC FUNC(void,RTE_COMH_APPL_CODE) Read_'+MSG_NM+'_MSG_FROM_RTE(void)\n{\n'
	print '\tSTATIC COMH_' + MSG_NM.upper() + '_T ' + MSG_NM + '_MSG_TEMP;\n'
	print '\tStd_ReturnType ret=E_NOT_OK;\n'
	for signal_in_msg in MyNode_msg_to_signals[MSG_NM].split(','):
		print '\tret = Rte_Read_P_'+MSG_NM + '_DE_' + signal_in_msg + '((DT_'+signal_in_msg+' *) &'+MSG_NM+'_MSG_TEMP.'+signal_in_msg+');'
		print '\tif(ret == E_OK)\n\t{'
		#print '\t\t'+MSG_NM+'_MSG.'+signal_in_msg + ' = '+MSG_NM+'_MSG_TEMP.'+signal_in_msg+' * '+str(signals_array["factor"][signal_in_msg])+' + '+str(signals_array["offset"][signal_in_msg])+';'
		if (signals_array["factor"][signal_in_msg]<1):
			mul = signals_array["frac"][signal_in_msg]
		else:
			mul = '1'
		print '\t\t'+MSG_NM+'_MSG.'+signal_in_msg + ' = ('+signals_array["Signal_Type"][signal_in_msg]+')evalRawToPhyApp('+MSG_NM+'_MSG_TEMP.'+signal_in_msg+' ,'+str(signals_array["factor"][signal_in_msg])+' ,'+str(signals_array["offset"][signal_in_msg])+' ,'+mul+');'
		print '\t\t'+MSG_NM+'_ValidityStructure.'+signal_in_msg+' = SIGNAL_VALID;'
		print '\t}\n\telse\n\t{\n'
		print '\t\t'+MSG_NM+'_ValidityStructure.'+signal_in_msg+' = SIGNAL_INVALID;'
		print '\t}'
	print '}\n'

#------------------------    RTE Write functions   -------------------------------------------------------
for MSG_NM in msgs_array["TxMSG"]:
	ChSumMsg = False
	for signal_in_msg in MyNode_msg_to_signals[MSG_NM].split(','):
		if 'Checksum' in signal_in_msg:
			ChSumMsg = True
	if ChSumMsg == 1:
		print r'STATIC FUNC(void,RTE_COMH_APPL_CODE) Write_'+MSG_NM+'_MSG_TO_RTE(void)\n{\n'
		print '\t'+MSG_NM+r'_U txBuffer = {0};'
		print '\tstatic u8 counter = 0;\n'
		print '\t////////// for checksum & counter calculations //////////////////////\n'
		print '\tCOYOTE_MESSAGE_COUNTER(counter);\n'
		for signal_in_msg in MyNode_msg_to_signals[MSG_NM].split(','):
			if 'Counter' in signal_in_msg:
				print '\ttxBuffer.'+MSG_NM+'.'+signal_in_msg[5:]+' = counter;' 
			elif 'Checksum' in signal_in_msg:
				print '\ttxBuffer.'+MSG_NM+'.'+signal_in_msg[5:]+' = COYOTE_CHECKSUM_CALC(txBuffer.data, 0x'+msgs_array["MsgID"].get(MSG_NM)+');'
			else:
				print '\ttxBuffer.'+MSG_NM+'.'+signal_in_msg[5:]+' = '+'evalPhyAppToRaw('+MSG_NM+'_MSG.'+signal_in_msg+' ,'+str(1/signals_array["factor"][signal_in_msg])+' ,'+str(signals_array["offset"][signal_in_msg])+' ,'+mul+');'
		print '\n////////////////////////////////////////////////////////////////////////////////\n'		
		for signal_in_msg in MyNode_msg_to_signals[MSG_NM].split(','):
			if (signals_array["factor"][signal_in_msg]<1):
				mul = signals_array["frac"][signal_in_msg]
			else:
				mul = '1'
			#print '\t(void)Rte_Write_P_'+MSG_NM + '_DE_' + signal_in_msg + '((DT_'+signal_in_msg+') (('+MSG_NM+'_MSG.'+signal_in_msg+' - '+str(signals_array["offset"][signal_in_msg])+') * '+str(1/signals_array["factor"][signal_in_msg])+'));'
			#print '\t(void)Rte_Write_P_'+MSG_NM + '_DE_' + signal_in_msg + '((DT_'+signal_in_msg+') evalPhyAppToRaw('+MSG_NM+'_MSG.'+signal_in_msg+' ,'+str(1/signals_array["factor"][signal_in_msg])+' ,'+str(signals_array["offset"][signal_in_msg])+' ,'+mul+'));'
			print '\t(void)Rte_Write_P_'+MSG_NM + '_DE_' + signal_in_msg + '((DT_'+signal_in_msg+') txBuffer.'+MSG_NM+'.'+signal_in_msg[5:]+');'
		print '}\n'
	else:
		print r'STATIC FUNC(void,RTE_COMH_APPL_CODE) Write_'+MSG_NM+'_MSG_TO_RTE(void)\n{\n'
		for signal_in_msg in MyNode_msg_to_signals[MSG_NM].split(','):
			if (signals_array["factor"][signal_in_msg]<1):
				mul = signals_array["frac"][signal_in_msg]
			else:
				mul = '1'
			#print '\t(void)Rte_Write_P_'+MSG_NM + '_DE_' + signal_in_msg + '((DT_'+signal_in_msg+') (('+MSG_NM+'_MSG.'+signal_in_msg+' - '+str(signals_array["offset"][signal_in_msg])+') * '+str(1/signals_array["factor"][signal_in_msg])+'));'
			print '\t(void)Rte_Write_P_'+MSG_NM + '_DE_' + signal_in_msg + '((DT_'+signal_in_msg+') evalPhyAppToRaw('+MSG_NM+'_MSG.'+signal_in_msg+' ,'+str(1/signals_array["factor"][signal_in_msg])+' ,'+str(signals_array["offset"][signal_in_msg])+' ,'+mul+'));'
		print '}\n'
#-------------------------   Generate prototypes and variables    -------------------------------------------------------
#variable declarations
for MSG_NM in dict(msgs_array["RxMSG"].items()+ msgs_array["TxMSG"].items()):
	OutPutFile.write('STATIC ')
	OutPutFile.write(inits["str"][MSG_NM]+'_MSG;\n')
	for signal_in_msg in MyNode_msg_to_signals[MSG_NM].split(','):
		OutPutFile.write("")
#--------------    Prototypes for Get functions -----------------------------------
for MSG_NM in msgs_array["RxMSG"]:
	for signal_in_msg in MyNode_msg_to_signals[MSG_NM].split(','):
		typp = signals_array["Signal_Type"][signal_in_msg]
		if(signals_array["RawNumOfBits"][signal_in_msg] == 1):
			ComH_Function = "\tEXTERN FUNC(Std_ReturnType, RTE_COMH_APPL_CODE)" + " COMH_Is" + signal_in_msg +'('+typp+" *value);\n"
		else:
			ComH_Function = "\tEXTERN FUNC(Std_ReturnType, RTE_COMH_APPL_CODE)" + " COMH_Get" + signal_in_msg +'('+typp+" *value);\n"
		OutPutFile.write(ComH_Function)
		
#--------------    Prototypes for Set functions -----------------------------------
for MSG_NM in msgs_array["TxMSG"]:
	for signal_in_msg in MyNode_msg_to_signals[MSG_NM].split(','):
		typp = signals_array["Signal_Type"][signal_in_msg]
		ComH_Function = "\tEXTERN FUNC(void, RTE_COMH_APPL_CODE)"+ " COMH_Set" + signal_in_msg + "("+typp+" New_"+signal_in_msg+");\n"
		OutPutFile.write(ComH_Function)
#--------------    Prototypes for write / read from RTE -----------------------------------
for MSG_NM in msgs_array["TxMSG"]:
		ComH_Function = '\tSTATIC FUNC(void,RTE_COMH_APPL_CODE) Write_'+MSG_NM+'_MSG_TO_RTE(void);\n'
		OutPutFile.write(ComH_Function)
for MSG_NM in msgs_array["RxMSG"]:
		ComH_Function = '\tSTATIC FUNC(void,RTE_COMH_APPL_CODE) Read_'+MSG_NM+'_MSG_FROM_RTE(void);\n'
		OutPutFile.write(ComH_Function)
#-------------		Definition of validity struct ------------------------------------------
for MSG_NM in msgs_array["RxMSG"]:
	val = "typedef struct "+MSG_NM+"_Validity_S\n"
	val+= "{\n"
	for signal_in_msg in MyNode_msg_to_signals[MSG_NM].split(','):
		x = "\tbitfield "+signal_in_msg
		val+= x+" "*(40-len(x))+':1;\n'
	val+= "}"+MSG_NM.upper()+"_VALIDITY_T;\n" 
	OutPutFile.write(val)
for MSG_NM in msgs_array["RxMSG"]:
	val = "STATIC "+MSG_NM.upper()+"_VALIDITY_T  "+MSG_NM+"_ValidityStructure;\n"
	OutPutFile.write(val)
#-------------  Generating Max and Min const values #defines -------------------------------
for MSG_NM in msgs_array["TxMSG"]:
	for signal_in_msg in MyNode_msg_to_signals[MSG_NM].split(','):
		if (signals_array["factor"][signal_in_msg]<1):
			mul = signals_array["frac"][signal_in_msg]
		else:
			mul = '1'
		max = str(int(int(mul)*float(signals_array["max"][signal_in_msg])))
		min = str(int(float(signals_array["min"][signal_in_msg])*int(mul)))
		#max = signals_array["max"][signal_in_msg]
		if(not float(max)):
			max = str(int(mul)*(pow(2,int(signals_array["RawNumOfBits"][signal_in_msg]))-1))
		val = '#define '+signal_in_msg+'_MaxVal\t' +max+'\n'
		val+= '#define '+signal_in_msg+'_MinVal\t' +min+'\n'
		OutPutFile.write(val)