import re
from Tkinter import *
from textwrap import wrap
import tkFileDialog
import math
from DBC_Parser import DBCParse
from prettytable import PrettyTable
import xml.etree.ElementTree as ET

# Functions:
def AddBool(name,DataTypeElementsRoot):
	boolType = ET.SubElement(DataTypeElementsRoot,'BOOLEAN-TYPE')
	shortName = ET.SubElement(boolType,'SHORT-NAME')
	shortName.text = name
	
def AddStruct(message,DataTypeElementsRoot):
	recordType = ET.SubElement(DataTypeElementsRoot,'RECORD-TYPE')
	shortName = ET.SubElement(recordType,'SHORT-NAME')
	shortName.text = message.name + '_GEN_S'
	Elements = ET.SubElement(recordType,'ELEMENTS')
	for signal in message.signals:
		recordElement = ET.SubElement(Elements,'RECORD-ELEMENT')
		shortName = ET.SubElement(recordElement,'SHORT-NAME')
		shortName.text = signal
		typeRef = ET.SubElement(recordElement,'TYPE-TREF')
		typeRef.attrib = {'DEST':'BOOLEAN-TYPE'}
		typeRef.text = '/DataType/DT_'+signal
		
def AddValidityStruct(message,DataTypeElementsRoot):
	for signal in message.signals:
		recordType = ET.SubElement(DataTypeElementsRoot,'RECORD-TYPE')
		shortName = ET.SubElement(recordType,'SHORT-NAME')
		shortName.text = 'DT_'+signal + '_S'
		Elements = ET.SubElement(recordType,'ELEMENTS')
		FirstRecordElement = ET.SubElement(Elements,'RECORD-ELEMENT')
		shortName = ET.SubElement(FirstRecordElement,'SHORT-NAME')
		shortName.text = signal
		typeRef = ET.SubElement(FirstRecordElement,'TYPE-TREF')
		if (message.signals[signal].len == 1):
			typeRef.attrib = {'DEST':'BOOLEAN-TYPE'}
		else:
			typeRef.attrib = {'DEST':'INTEGER-TYPE'}
		typeRef.text = '/DataType/DT_'+signal
		SecondRecordElement = ET.SubElement(Elements,'RECORD-ELEMENT')
		shortName = ET.SubElement(SecondRecordElement,'SHORT-NAME')
		shortName.text = 'SignalValidity'
		typeRef = ET.SubElement(SecondRecordElement,'TYPE-TREF')
		typeRef.attrib = {'DEST':'INTEGER-TYPE'}
		typeRef.text = '/DataType/DT_SignalValidity'
		ThirdRecordElement = ET.SubElement(Elements,'RECORD-ELEMENT')
		shortName = ET.SubElement(ThirdRecordElement,'SHORT-NAME')
		shortName.text = 'timestmp'
		typeRef = ET.SubElement(ThirdRecordElement,'TYPE-TREF')
		typeRef.attrib = {'DEST':'INTEGER-TYPE'}
		typeRef.text = '/DataType/UInt16'
		
		
def AddEnum(signal,DataTypeElementsRoot,TextTableName,MAX,MIN):
	''' Before Calling this interface the Text Table needs to be
	declared under DataTypeSemantics'''
	intType = ET.SubElement(DataTypeElementsRoot,'INTEGER-TYPE')
	shortName = ET.SubElement(intType,'SHORT-NAME')
	shortName.text = 'DT_'+signal+'Validity'
	data_def_props = ET.SubElement(intType,'SW-DATA-DEF-PROPS')
	compu_method_ref = ET.SubElement(data_def_props,'COMPU-METHOD-REF')
	compu_method_ref.attrib = {'DEST':'COMPU-METHOD'}
	compu_method_ref.text = '/DataType/DataTypeSemantics/'+TextTableName
	LowerLimit = ET.SubElement(intType,'LOWER-LIMIT')
	LowerLimit.attrib = {'INTERVAL-TYPE':'CLOSED'}
	LowerLimit.text = str(MIN)
	UpperLimit = ET.SubElement(intType,'UPPER-LIMIT')
	UpperLimit.attrib = {'INTERVAL-TYPE':'CLOSED'}
	UpperLimit.text = str(MAX)
	
def AddTextTable (DataTypeSemanticsElementsRoot,name,dictofValues):
	COMPU_Meth = ET.SubElement(DataTypeSemanticsElementsRoot,'COMPU-METHOD')
	shortName = ET.SubElement(COMPU_Meth,'SHORT-NAME')
	shortName.text = name
	category = ET.SubElement(COMPU_Meth,'CATEGORY')
	category.text = 'TEXTTABLE'
	COMPU_Int_Phys = ET.SubElement(COMPU_Meth ,'COMPU-INTERNAL-TO-PHYS')
	COMPU_Scales = ET.SubElement(COMPU_Int_Phys,'COMPU-SCALES')
	for value in dictofValues:
		COMPU_Scale = ET.SubElement(COMPU_Scales,'COMPU-SCALE')
		DESC = ET.SubElement(COMPU_Scale,'DESC')
		L2 = ET.SubElement(DESC,'L-2')
		L2.attrib = {'L':'FOR-ALL'}
		L2.text = dictofValues[value]
		LL = ET.SubElement(COMPU_Scale,'LOWER-LIMIT')
		LL.text = str(value)
		UL = ET.SubElement(COMPU_Scale,'UPPER-LIMIT')
		UL.text = str(value)
		CC = ET.SubElement(COMPU_Scale,'COMPU-CONST')
		VT = ET.SubElement(CC,'VT')
		VT.text = str(hex(int(value))).upper().replace('0X','Cx')+'_'+str(dictofValues[value])
	
	

	
ET.register_namespace('', "http://autosar.org/3.2.2")
tree = ET.parse('COMH_Try_swc.arxml')
#----------------------------   Read DBC File --------------------------------------------------------
fileName = 'RIV_ADAS_Mule1_v8.dbc'
if fileName == None:
	sys.exit()

DBC_Name = fileName 

DBCParsObj = DBCParse(DBC_Name,'PARK')
#DBCParsObj.printdbc()
#----------------------------   Read DBC File --------------------------------------------------------

root = tree.getroot()

topLevelPacks = root[0]

# for AR_Packs in topLevelPacks:
	# for AR_Pack in AR_Packs:
		# if 'SHORT-NAME' in AR_Pack.tag:
			# print AR_Pack.text

for AR_Packs in topLevelPacks:
	for AR_Pack in AR_Packs:
		if 'SHORT-NAME' in AR_Pack.tag:
			if AR_Pack.text == 'DataType':
				#print 'Datatype found' 	
				#print AR_Packs[1].tag
				DataType_Elements = AR_Packs[1]

AddEnum('Signal',DataType_Elements,'VT_SignalValidity',4,0)
for AR_Packs in topLevelPacks:
	for AR_Pack in AR_Packs:
		if 'SHORT-NAME' in AR_Pack.tag:
			if AR_Pack.text == 'DataType':
				#print 'Datatype found' 	
				#print AR_Packs[1].tag
				if(len(AR_Packs)>2):
					DataType_SUB_PACKAGES_root = AR_Packs[2]
				else:
					SUB_Packages = ET.SubElement(AR_Packs,'SUB-PACKAGES')
					DataType_SUB_PACKAGES_root = SUB_Packages
					AR_Package = ET.SubElement(SUB_Packages,'AR-PACKAGE')
					shortName = ET.SubElement(AR_Package,'SHORT-NAME')
					shortName.text = 'DataTypeSemantics'
					Elements = ET.SubElement(AR_Package,'ELEMENTS')
				
for AR_Package in DataType_SUB_PACKAGES_root:
	if(AR_Package.find('SHORT-NAME').text == 'DataTypeSemantics'):
		DataTypeSemanticsElementsRoot = AR_Package.find('ELEMENTS')
		signalname = 'VT_SignalValidity'
		dictofValues = {'0':'Valid','1':'InValid','3':'NotReceived','4':'NeverReceived'}
		AddTextTable (DataTypeSemanticsElementsRoot,signalname,dictofValues)


AddBool('DT_Raziur',DataType_Elements)




for message in DBCParsObj.Messages:
	msg = DBCParsObj.Messages[message]
	if msg.Type == 'Rx':
		AddValidityStruct(msg,DataType_Elements)
	
	

	
tree.write('new.xml')



