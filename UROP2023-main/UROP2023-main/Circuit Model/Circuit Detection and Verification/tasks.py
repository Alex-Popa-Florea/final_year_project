class Skill():
	def __init__(self,name, skill_type):
		self.name = name
		self.skill_type = skill_type
	
class PieceSkill(Skill):	
	def __init__(self,name,skill_type,piece):
		Skill.__init__(self,name, skill_type)
		self.piece = piece

class ConnectionSkill(Skill):	
	def __init__(self,name,skill_type,piece1,piece2):
		Skill.__init__(self,name, skill_type)
		self.piece1 = piece1
		self.piece2 = piece2

class ClosingSkill(Skill):	
	def __init__(self,name,skill_type):
		Skill.__init__(self,name, skill_type)
		
class MCSkill(Skill):	
	def __init__(self,name, skill_type,port,piece):
		Skill.__init__(self,name, skill_type)
		self.port = port
		self.piece = piece

class FMSkill(Skill):	
	def __init__(self,name, skill_type,port,piece):
		Skill.__init__(self,name, skill_type)
		self.port = port
		self.piece = piece
		
class DirectionSkill(Skill):
	def __init__(self, name, skill_type):
		Skill.__init__(self, name, skill_type)
		
class ConnectPieces(Skill):
	def __init__(self, name, skill_type):
		Skill.__init__(self, name, skill_type)

class GateSkill(Skill):	
	def __init__(self,name, skill_type,gate):
		Skill.__init__(self,name, skill_type)
		self.gate = gate

class Task():
	def __init__(self, task_id, name, pieces, skills, action = [], instruction = ""):
		self.id = task_id
		self.name = name
		self.pieces = pieces
		self.skills = skills
		self.action = action
		self.obs = []
		self.instruction = instruction




#------------------------------------------------------------------
## Piece Picking Skills

# * (Skill 1) When a LED should be used
sk_led = PieceSkill("led","piece","led") 

# * (Skill 2) When a FM Radio receiver should be used
sk_FM = PieceSkill("fm", "piece","fm")

# * (Skill 3) A buzzer should be used
sk_buzzer = PieceSkill("buzzer", "piece", "buzzer")

# * (Skill 4) A Switch should be used
sk_switch = PieceSkill("switch", "piece", "switch")

# * (Skill 5) A Reed Switch should be used
sk_reed = PieceSkill("reed", "piece", "reed")

# * (Skill 6) A Push Button Switch should be used
sk_button = PieceSkill("push button","piece","button")

# * (Skill 7) A Lamp should be used
sk_lamp = PieceSkill("lamp", "piece", "lamp")

# * (Skill 8) A Battery should be used
sk_battery = PieceSkill("battery", "piece", "battery")

# * (Skill 9) A Speaker should be used
sk_speaker = PieceSkill("speaker","piece","speaker") 

# * (Skill 10) A IC-Music should be used
sk_music = PieceSkill("mc","piece","mc") 

# * (Skill 11) A Motor should be used
sk_motor = PieceSkill("motor","piece","motor") 

#------------------------------------------------------------------
## Piece connecting skills

# * (skill 12) How to Connect two pieces together
sk_cp = ConnectPieces("connect", "connect_pieces")

#------------------------------------------------------------------
## LED direction skills

# * (skill 13) The correct directionality of an LED
sk_dir_led = DirectionSkill("led_direc", "led")

#------------------------------------------------------------------
## High level skills

# * (skill 14) How to power an MC
power_mc = MCSkill("power", "mc", "power", "wire")

# * (skill 15) Check signal of an MC
signal_mc = MCSkill("signal", "mc", "signal", "wire")

# * (skill 16) How to power an FM
power_fm = FMSkill("power", "fm", "power", "wire")

# * (skill 17) Check Signal of an FM
signal_fm = FMSkill("signal", "fm", "signal", "wire")

#------------------------------------------------------------------
## Closing skills

# * (skill 18) That the circuit should be a circuit
closed_circuit = ClosingSkill("simple_closed", "closing")

#------------------------------------------------------------------
## Gate skills

# * (skill 19) How to create an AND gate
and_gate = GateSkill("and_gate", "gate", "and")

# * (skill 120) How to create an OR gate
or_gate = GateSkill("or_gate", "gate", "or")

# * (skill 21) How to create an NOT gate
not_gate = GateSkill("not_gate", "gate", "not")

all_skills = [sk_led, 
			  sk_FM, 
			  sk_buzzer, 
			  sk_switch, 
			  sk_reed, 
			  sk_button,
			  sk_lamp, 
			  sk_battery, 
			  sk_speaker, 
			  sk_music, 
			  sk_motor, 
			  sk_cp, 
			  sk_dir_led, 
			  power_mc, 
			  signal_mc, 
			  power_fm, 
			  signal_fm, 
			  closed_circuit, 
			  and_gate, 
			  or_gate, 
			  not_gate]

################################################


task1 = Task(1,"sw_la", ["switch", "lamp"], [], 
		[0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
		"Build a circuit that you can turn a light on and off using a switch")

task2 = Task(2,"bu_la", ["push button", "lamp"], [],
		[0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0 ],
		"Build a circuit that you can turn a light on and off using a button")

task3 = Task(3,"re_la", ["reed", "lamp"], [],
		[0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0 ],
		"Build a circuit that you can turn a light on and off using a reed switch")

task4 = Task(4,"sw_mo", ["switch", "motor"], [],
		[0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0 ],
		"Build a circuit that you can turn a motor on and off using a switch")

task5 = Task(5,"bu_mo", ["push button", "motor"], [],
		[0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0 ],
		"Build a circuit that you can turn a motor on and off using a button")

task6 = Task(6,"re_mo", ["reed", "motor"], [],
		[0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0 ],
		"Build a circuit that you can turn a motor on and off using a reed switch")

task7 = Task(7,"mo", ["motor"], [],
		[0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0 ],
		"Build a circuit that constantly will have a motor spinning")

task8 = Task(8,"sw_le", ["switch", "led"], [],
		[1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0 ],
		"Build a circuit that you can turn a LED on and off using a switch")

task9 = Task(9,"le", ["led"], [],
		[1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0 ],
		"Build a circuit that has a constant LED on")

task10 = Task(10,"mc_sp", ["mc", "speaker"], [],
	    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0 ],
		"Build a circuit that plays music")

task11 = Task(11,"mc_sp_sw", ["mc", "speaker", "switch"], [],
		[0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0 ],
		"Build a circuit that plays music when a switch is turned on")

task12 = Task(12,"mc_sp_bu", ["mc", "speaker", "push button"], [],
		[0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0 ],
		"Build a circuit that plays music when a button is pressed")

task13 = Task(13,"mc_sp_re", ["mc", "speaker", "reed"], [],
		[0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0 ],
		"Build a circuit that plays music when a reed switch is turned on")

task14 = Task(14,"mc_le", ["mc", "led"], [],
		[1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0 ],
		"Build a circuit that blinks a light in a rythm of a song")

task15 = Task(15,"mc_le_sw", ["mc", "led", "switch"], [],
		[1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0 ],
		"Build a circuit that blinks a light in the rythm of a song when a switch is turned on")

task16= Task(16,"mc_le_bu", ["mc", "led", "push button"], [], 
		[1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0],
		"Build a circuit that blinks a light in the rythm of a song when a button is pressed")

task17 = Task(17,"mc_le_re", ["mc", "led", "reed"], [],
		[1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0 ],
		"Build a circuit that blinks a light in the rythm of a song when a reed switch is turned on")


#--------------
task18 = Task(18,"fm_sp", ["fm", "speaker"], [],
	    [0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0 ],
		"Build a circuit that that you can listen to the FM radio via the Speaker")
task19 = Task(19,"fm_sp_sw", ["fm", "speaker","switch"], [],
	    [0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0 ],
		"Build a circuit that that you can listen to the FM radio via the Speaker when a switch is turned on")
task20 = Task(20,"fm_sp_bu", ["fm", "speaker","push button"], [],
	    [0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0 ],
		"Build a circuit that that you can listen to the FM radio via the Speaker when a button is pressed")
task21 = Task(21,"fm_buz", ["fm", "buzzer"], [],
	    [0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0 ],
		"Build a circuit that that you can listen to the FM radio via the buzzer")
#--------------
task22 = Task(22,"fm_buz_sw", ["fm", "buzzer","switch"], [],
	    [0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0 ],
		"Build a circuit that that you can listen to the FM radio via the buzzer when a switch is turned on")
task23 = Task(23,"fm_buz_bu", ["fm", "buzzer","push button"], [],
	    [0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0 ],
		"Build a circuit that that you can listen to the FM radio via the buzzer when a button is pressed")

#--------------
# AND
task24 = Task(24,"sw_bu_le", ["switch","push button","led"], [],
		[1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0 ],
		"Build a circuit that that the led lights only when both switch and push button switch is closed")

# OR
task25 = Task(25,"sw_bu_le", ["switch","push button","led"], [],
		[1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0 ],
		"Build a circuit that that the led lights only when either switch or push button switch is closed")

# NOT
task26 = Task(26,"sw_not_le", ["switch","led"], [],
		[1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1 ],
		"Build a circuit that that the led lights when the switch is not closed but not light when the switch is closed")

# AND
task27 = Task(27,"sw_bu_la", ["switch","push button","lamp"], [],
		[0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0 ],
		"Build a circuit that that the lamp lights only when both switch and push button switch is closed")

# OR
task28 = Task(28,"sw_bu_la", ["switch","push button","lamp"], [],
		[0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0 ],
		"Build a circuit that that the lamp lights only when either switch or push button switch is closed")

# NOT
task29 = Task(29,"sw_not_la", ["switch","lamp"], [],
		[0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1 ],
		"Build a circuit that that the lamp lights when the switch is not closed but not light when the switch is closed")