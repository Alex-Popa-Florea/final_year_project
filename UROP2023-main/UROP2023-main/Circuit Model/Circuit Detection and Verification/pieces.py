import numpy as np

class Board:
    def __init__(self, name, height, length):
        self.name = name
        self.pos = np.empty([height, length], dtype=list)
        for j in range(0, height):
            for i in range(0, length):
                self.pos[j][i] = []

class Battery:
    b_id = 1
    def __init__(self, name, x1, x2, y1, y2, inp=[], out=[]):
        self.type = "battery"
        # self.width = 3
        # self.height = 3
        self.name = name
        self.inp = []
        self.out = []
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.power = True
    
    def addInp(self, inp):
        self.inp.append(inp)
    def removeInp(self, inp):
        self.inp.remove(inp)
    def addOut(self, out):
        self.out.append(out)
    def removeOut(self, out):
        self.out.remove(out)
    def setInp(self, inp):  # allows assignment
        self.inp = inp
    def setOut(self, out):
        self.out = out


class Wire:
	#TODO - we are not separating each wire, what to do?
	w_id = 1
	
	def __init__(self, name, x1, x2, y1, y2, inp = [], out = []):
		self.name = name
		self.type = "wire"
		#self.width = size # between 1 and 7, or 0 for jumper wire
		#self.height = 1
		self.inp = []
		self.out = []
		self.x1 = x1
		self.x2 = x2
		self.y1 = y1
		self.y2 = y2
		self.power = False

	def addInp(self,inp):
		self.inp.append(inp)
	def removeInp(self,inp):
		self.inp.remove(inp)
	def addOut(self,out):
		self.out.append(out)
	def removeOut(self,out):
		self.out.remove(out)
	def setInp(self,inp):
		self.inp = inp
	def setOut(self,out):
		self.out = out

class Switch:
	s_id = 1
	def __init__(self, name, x1, x2, y1, y2, inp = [], out = []):
		self.type = "switch"
		#self.width = 3
		#self.height = 1
		#self.s_type = s_type #press or slide switch
		self.name = name
		self.inp = []
		self.out = []
		self.x1 = x1
		self.x2 = x2
		self.y1 = y1
		self.y2 = y2
		self.power = False
		self.pressed = False
		#self.connected = []
	
	def PressSwitch(self):
		self.pressed = True
		self.outPower = True
	
	def UnpressSwitch(self):
		self.pressed = False
		self.outPower = False
	
	def addInp(self,inp):
		self.inp.append(inp)
	def removeInp(self,inp):
		self.inp.remove(inp)
	def addOut(self,out):
		self.out.append(out)
	def removeOut(self,out):
		self.out.remove(out)
	def setInp(self,inp):
		self.inp = inp
	def setOut(self,out):
		self.out = out
	
class Button:
	bu_id = 1
	def __init__(self, name, x1, x2, y1, y2, inp = [], out = []):
		self.type = "push button"
		#self.width = 3
		#self.height = 1
		#self.s_type = s_type #press or slide switch
		self.name = name
		self.inp = []
		self.out = []
		self.x1 = x1
		self.x2 = x2
		self.y1 = y1
		self.y2 = y2
		self.power = False
		self.pressed = False
		#self.connected = []
	
	def PressButton(self):
		self.pressed = True
		self.outPower = True
	
	def UnpressButton(self):
		self.pressed = False
		self.outPower = False
	
	def addInp(self,inp):
		self.inp.append(inp)
	def removeInp(self,inp):
		self.inp.remove(inp)
	def addOut(self,out):
		self.out.append(out)
	def removeOut(self,out):
		self.out.remove(out)
	def setInp(self,inp):
		self.inp = inp
	def setOut(self,out):
		self.out = out

class Reed:
    reed_id = 1
    def __init__(self, name, x1, x2, y1, y2, inp=[], out=[]):
        self.type = "reed"
        # self.width = 3
        # self.height = 1
        # self.s_type = s_type #press or slide switch
        self.name = name
        self.inp = []
        self.out = []
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.power = False
        self.pressed = False
        # self.connected = []

    def PressReed(self):
        self.pressed = True
        self.outPower = True

    def UnpressReed(self):
        self.pressed = False
        self.outPower = False

    def addInp(self, inp):
        self.inp.append(inp)
    def removeInp(self, inp):
        self.inp.remove(inp)
    def addOut(self, out):
        self.out.append(out)
    def removeOut(self, out):
        self.out.remove(out)
    def setInp(self, inp):
        self.inp = inp
    def setOut(self, out):
        self.out = out


class Led:  # Led that only allows current in one direction
    l_id = 1

    def __init__(self, name, x1, x2, y1, y2, inp=[], out=[]):
        self.type = "led"
        # self.width = 3
        # self.height = 1
        self.name = name
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.inp = []
        self.out = []
        self.power = False
        self.inp2 = []

    def addInp(self, inp):
        self.inp.append(inp)
    def addInp2(self,inp2):
        self.inp2.append(inp2)
        # if not self.inp2:
        #     	self.inp2.append(inp2)
        # else:
        #     self.inp2[0] = inp2
    def removeInp(self, inp):
        self.inp.remove(inp)
    def addOut(self, out):
        self.out.append(out)
    def removeOut(self, out):
        self.out.remove(out)
    def setInp(self, inp):
        self.inp = inp
    def setOut(self, out):
        self.out = out

class Lamp:  # Led that only allows current in one direction
    lamp_id = 1

    def __init__(self, name, x1, x2, y1, y2, inp=[], out=[]):
        self.type = "lamp"
        # self.width = 3
        # self.height = 1
        self.name = name
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.inp = []
        self.out = []
        self.power = False

    def addInp(self, inp):
        self.inp.append(inp)
    def removeInp(self, inp):
        self.inp.remove(inp)
    def addOut(self, out):
        self.out.append(out)
    def removeOut(self, out):
        self.out.remove(out)
    def setInp(self, inp):
        self.inp = inp
    def setOut(self, out):
        self.out = out

class Speaker:
	sp_id = 1
	def __init__(self, name, x1, x2, y1, y2, inp = [], out = []):
		self.type = "speaker"
		# self.width = 3
		# self.height = 1
		self.name = name
		self.inp = []
		self.out = [] 
		self.x1 = x1
		self.x2 = x2
		self.y1 = y1
		self.y2 = y2
		self.power = False
		
	def addInp(self,inp):
		self.inp.append(inp)
	def removeInp(self,inp):
		self.inp.remove(inp)
	def addOut(self,out):
		self.out.append(out)
	def removeOut(self,out):
		self.out.remove(out)
	def setInp(self,inp):
		self.inp = inp
	def setOut(self,out):
		self.out = out

class Buzzer:
    buz_id = 1
    def __init__(self, name, x1, x2, y1, y2, inp=[], out=[]):
        self.type = "buzzer"
        # self.width = 3
        # self.height = 1
        self.name = name
        self.inp = []
        self.out = []
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.power = False

    def addInp(self, inp):
        self.inp.append(inp)
    def removeInp(self, inp):
        self.inp.remove(inp)
    def addOut(self, out):
        self.out.append(out)
    def removeOut(self, out):
        self.out.remove(out)
    def setInp(self, inp):
        self.inp = inp
    def setOut(self, out):
        self.out = out

class Motor:
    m_id = 1
    
    def __init__(self, name, x1, x2, y1, y2, inp=None, out=None):
        self.type = "motor"
        self.name = name
        self.inp = []
        self.out = []
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.power = False
        
    def addInp(self, inp):
        self.inp.append(inp)
    def removeInp(self, inp):
        self.inp.remove(inp)
    def addOut(self, out):
        self.out.append(out)
    def removeOut(self, out):
        self.out.remove(out)
    def setInp(self, inp):
        self.inp = inp
    def setOut(self, out):
        self.out = out



class Music_Circuit:
    # TO-DO: check trigger? waves?
	mc_id = 1
	def __init__(self, name, x1, x2, y1, y2, inp = [], out = [], trigger = [], waves = [], hold = []): 
		self.type = "mc"
		# self.width = 3
		# self.height = 2
		self.name = name
		self.inp = []
		self.out = [] 
		self.trigger = []
		self.hold = []
		self.waves = []
		self.x1 = x1
		self.x2 = x2
		self.y1 = y1
		self.y2 = y2
		self.power = False
		self.powerInp = False
		self.powerTrigger = False
	
	def addInp(self,inp):
		self.inp.append(inp)
	def removeInp(self,inp):
		self.inp.remove(inp)
	def addHold(self,hold):
		self.hold.append(hold)
	def removeHold(self,hold):
		self.hold.remove(hold)
	def addOut(self,out):
		self.out.append(out)
	def removeOut(self,out):
		self.out.remove(out)
	def addWaves(self,waves):
		self.waves.append(waves)
	def removeWaves(self,waves):
		self.waves.remove(waves)
	def setInp(self,inp):
		self.inp = inp
	def setOut(self,out):
		self.out = out
	def addTrigger(self,trig):
		self.trigger.append(trig)
		self.Power = True
	def removeTrigger(self,trig):
		self.trigger.remove(trig)
	def setPowerTrigger(self,on):
		if on == True:
			self.powerTrigger = True
		else:
			self.powerTrigger = False
		if (self.powerTrigger and self.powerInp):
			self.power = True

	def setPowerInp(self,on):
		if on == True:
			self.powerInp = True
		else:
			self.powerInp = False
		# ~ if (self.powerTrigger and self.powerInp):
			# ~ self.power = True
		if (self.powerInp):
			self.power = True
	def setTrigger(self,trigger):
		self.trigger = trigger
	def setWaves(self,waves):
		self.waves = waves
	def setHold(self,hold):
		self.hold = hold
	def setInp(self,inp):
		self.hold = inp

class FM:
	fm_id = 1
	def __init__(self, name, x1, x2, y1, y2, inp = [], out = [], trigger = [], waves = [], hold = []): 
		self.type = "fm"
		# self.width = 3
		# self.height = 2
		self.name = name
		self.inp = []
		self.out = [] 
		self.waves = []
		self.x1 = x1
		self.x2 = x2
		self.y1 = y1
		self.y2 = y2
		self.power = False
		self.powerInp = False
		self.powerTrigger = False
	
	def addInp(self,inp):
		self.inp.append(inp)
	def removeInp(self,inp):
		self.inp.remove(inp)
	def addOut(self,out):
		self.out.append(out)
	def removeOut(self,out):
		self.out.remove(out)
	def addWaves(self,waves):
		self.waves.append(waves)
	def removeWaves(self,waves):
		self.waves.remove(waves)
	def setInp(self,inp):
		self.inp = inp
	def setOut(self,out):
		self.out = out
	def setPowerInp(self,on):
		if on == True:
			self.powerInp = True
		else:
			self.powerInp = False
		# ~ if (self.powerTrigger and self.powerInp):
			# ~ self.power = True
		if (self.powerInp):
			self.power = True
	def setWaves(self,waves):
		self.waves = waves
	def setInp(self,inp):
		self.hold = inp
