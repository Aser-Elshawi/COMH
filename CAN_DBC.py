

class Signal:
	def __init__(self,SignalName):
		#add the object of every new signal in AllSignals dictionary for tracking
		self.name = SignalName
		self.signalInMessage = ""
		self.factor = 0
		self.offset = 0
		self.comment = ""
		self.rawNumOfBits = 0
		self.len = 0
		self.Signal_Type = "" # 1 for intel or 0 for Motorola
		self.frac = 0
		self.max = 0
		self.min = 0
		#Multiplexed: if M (it's the multiplexor signal), m1 signal is in first mux, m2 means signal is in second mux ...etc
		self.Muxed = "0"
		self.Start_Bit = 0
		self.unit = ""
		self.isValTable = 0
		self.valTable = {}
		self.c_type = "" #type in C code ex. uint8, sint8
		self.comment = ""
		self.initValue = 0 # raw init value of the signal

class Message:
	def __init__(self,MessageName,MessageID):
		self.signals = {}
		self.ID = MessageID
		self.name = MessageName
		self.Tx_Node = ""
		self.Type = "" #Tx or Rx
		self.cyclicTime = 0
	def AddSig(self,SignalName):
		if SignalName in self.signals:
			#signal is already added
			pass
		else:
			self.signals[SignalName]=Signal(SignalName)
	def PrintSignals(self):
		for signal in self.signals:
			print signal
	def signal(self,signalName):
		if signalName in self.signals:
			return self.signals[signalName]
		else:
			return None