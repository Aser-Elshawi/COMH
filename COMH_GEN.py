import re
from Tkinter import *
from textwrap import wrap
import tkFileDialog
import math
from DBC_Parser import DBCParse
from prettytable import PrettyTable

class COMH_GEN:
	def __init__(self,DBCObj):
		self.Messages = DBCObj.Messages
	
	def GenCFile(self,filename):
		#Create Source File
		SF = open(filename,'w')
		self.GenRxProcessMsgs(SF)
		self.GenTxProcessMsgs(SF)
		
	def GenHFile(self):
		#Create Header File
		HeaderFile = open('COMH.h','w')
	def GenRxProcessMsgs(self,SF):
		for message in self.Messages:
			if self.Messages[message].Type == 'Rx':
				SF.write('\n\n// The cyclic time of '+message+' Rx message is '+str(self.Messages[message].cyclicTime) +'\n')
				SF.write('static FUNC(void,RTE_COMH_APPL_CODE) Process_'+message+'_MSG(void)\n{\n\n')
				SF.write('\tstatic COMH_'+message.upper()+'_T '+message+'_MSG = {')
				values = []
				for signal in self.Messages[message].signals:
					values.append(str(self.Messages[message].signal(signal).initValue))
				for value in values[0:-1]:
					SF.write(value+',')
				SF.write(values[-1]+'}\n')
				SF.write('\tStd_ReturnType ret=E_NOT_OK;\n\n')
				#loop on signals
				for signal in self.Messages[message].signals:
					SF.write('\tret = Rte_Read_P_'+message+'_DE_'+signal+'((DT_'+signal+' *) &'+message+'_MSG.'+signal+\
					');\n\tif(ret == E_OK)\n\t{\n')
					if (self.Messages[message].signal(signal).factor == 1):
						multiplier = '1'
					else:
						multiplier = str(pow(10,(len(str(self.Messages[message].signal(signal).factor)) -2)))
					SF.write('\t\t'+message+'_MSG.'+signal + ' = ('+self.Messages[message].signal(signal).c_type+\
					')evalRawToPhyApp('+message+'_MSG.'+signal+' ,'+str(self.Messages[message].signal(signal).factor)+
					' ,'+str(float(self.Messages[message].signal(signal).offset))+' ,'+\
					multiplier +');\n')
					SF.write('\t\t'+message+'_ValidityStructure.'+signal+' = SIGNAL_VALID;\n')
					SF.write('\t}\n\telse\n\t{\n'+\
					'\t\t'+message+'_ValidityStructure.'+signal+' = SIGNAL_INVALID;\n\t}\n')
					
				SF.write('\t// Write values to RTE:\n')
				#loop on signals
				for signal in self.Messages[message].signals:
					if(self.Messages[message].signal(signal).comment != ""):
						SF.write('\t//'+self.Messages[message].signal(signal).comment+'\n')
					SF.write('\tRte_Write_P_'+message+'_DE_'+signal+'((DT_'+signal+') '+message+'_MSG.'+signal+');\n')
				SF.write('}')
				
	def GenTxProcessMsgs(self,SF):
		for message in self.Messages:
			if self.Messages[message].Type == 'Tx':
				SF.write('\n\n// The cyclic time of '+message+' Tx Message is '+str(self.Messages[message].cyclicTime) +'\n')
				SF.write('static FUNC(void,RTE_COMH_APPL_CODE) Process_'+message+'_MSG(void)\n{\n\n')
				SF.write('\tstatic COMH_'+message.upper()+'_T '+message+'_MSG = {')
				values = []
				for signal in self.Messages[message].signals:
					values.append(str(self.Messages[message].signal(signal).initValue))
				for value in values[0:-1]:
					SF.write(value+',')
				SF.write(values[-1]+'}\n')
				SF.write('\tStd_ReturnType ret=E_NOT_OK;\n\n')
				#loop on signals
				for signal in self.Messages[message].signals:
					SF.write('\tret = Rte_Read_P_'+message+'_DE_'+signal+'((DT_'+signal+' *) &'+message+'_MSG.'+signal+\
					');\n\tif(ret == E_OK)\n\t{\n')
					if (self.Messages[message].signal(signal).factor == 1):
						multiplier = '1'
					else:
						multiplier = str(pow(10,(len(str(self.Messages[message].signal(signal).factor)) -2)))
					SF.write('\t\t'+message+'_MSG.'+signal + ' = ('+self.Messages[message].signal(signal).c_type+\
					')evalPhyToRawApp('+message+'_MSG.'+signal+' ,'+str(self.Messages[message].signal(signal).factor)+
					' ,'+str(float(self.Messages[message].signal(signal).offset))+' ,'+\
					multiplier +');\n')
					SF.write('\t\t'+message+'_ValidityStructure.'+signal+' = SIGNAL_VALID;\n')
					SF.write('\t}\n\telse\n\t{\n'+\
					'\t\t'+message+'_ValidityStructure.'+signal+' = SIGNAL_INVALID;\n\t}\n')
					
				SF.write('\t// Write values to RTE:\n')
				#loop on signals
				for signal in self.Messages[message].signals:
					if(self.Messages[message].signal(signal).comment != ""):
						SF.write('\t//'+self.Messages[message].signal(signal).comment+'\n')
					SF.write('\tRte_Write_P_'+message+'_DE_'+signal+'((DT_'+signal+') '+message+'_MSG.'+signal+');\n')
				SF.write('}')
				
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

	DBCParsObj = DBCParse(DBC_Name,'PARK')
	#DBCParsObj.printdbc()
	Generator = COMH_GEN(DBCParsObj)
	Generator.GenCFile('COMH.c')