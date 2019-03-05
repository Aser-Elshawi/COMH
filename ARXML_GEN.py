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
	LowerLimit.text = MIN
	UpperLimit = ET.SubElement(intType,'UPPER-LIMIT')
	UpperLimit.attrib = {'INTERVAL-TYPE':'CLOSED'}
	UpperLimit.text = MAX
	
def AddTextTable (DataTypeSemanticsElementsRoot,name,dictofValues):
	pass
	
	

	
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

for AR_Packs in topLevelPacks:
	for AR_Pack in AR_Packs:
		if 'SHORT-NAME' in AR_Pack.tag:
			if AR_Pack.text == 'DataType':
				#print 'Datatype found' 	
				#print AR_Packs[1].tag
				DataType_SUB_PACKAGES_root = AR_Packs[2]
				
for AR_Package in DataType_SUB_PACKAGES_root:
	if(AR_Package.find('SHORT-NAME').text == 'DataTypeSemantics'):
		DataTypeSemanticsElementsRoot = AR_Package.find('ELEMENTS')
# for Element in DataType_Elements:
	# print Element.tag

AddBool('DT_Raziur',DataType_Elements)

for message in DBCParsObj.Messages:
	if message == 'Misc_Report':
		AddStruct(DBCParsObj.Messages[message],DataType_Elements)
	
	

	
tree.write('new.xml')



