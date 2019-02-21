

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
		#Multiplexed: if M (it's the multiplexor), m1 is first mux, m2 second ...etc
		self.Muxed = "0"
		self.Start_Bit = 0
		self.unit = ""

class Message:
	def __init__(self,MessageName,MessageID):
		self.signals = {}
		self.ID = MessageID
		self.name = MessageName
		self.Tx_Node = ""
		self.Type = ""
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