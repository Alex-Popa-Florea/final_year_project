def directional_connect(piece1, piece2, port1 = 'out', port2 = 'inp'):
    	# ~ print (piece1.name)
	# ~ print (port1)
	# ~ print (piece2.name)
	# ~ print (port2)
	# ~ print ("----")
	if (port1 == 'out'):
		if (port2 == 'inp'):
			piece1.addOut(piece2)
			piece2.addInp(piece1)
		if (port2 == 'trigger'): 
			piece1.addOut(piece2)
			piece2.addTrigger(piece1)
		if (port2 == 'hold'):
			piece1.addOut(piece2)
			piece2.addHold(piece1)
		if (port2 == 'waves'):
			piece1.addOut(piece2)
			piece2.addWaves(piece1)
	if (port1 == 'waves'):
		if (port2 == 'out'):
			piece1.addWaves(piece2)
			piece2.addOut(piece1)
	if (port1 == 'inp'):
		if (port2 == 'out'):
			piece1.addInp(piece2)
			piece2.addOut(piece1)
	if (port1 == 'trigger'):
		if (port2 == 'out'):
			piece1.addTrigger(piece2)
			piece2.addOut(piece1)
	if (port1 == 'hold'):
		if (port2 == 'out'):
			piece1.addHold(piece2)
			piece2.addOut(piece1)
	#Special cases for the LED to test directionality
	if (port1 == 'inp2'):
		if (port2 == 'out'):
			piece1.addInp2(piece2)
			#piece2.addOut(piece1)
	if (port1 == 'out'):
		if (port2 == 'inp2'):
			#piece1.addHold(piece2)
			piece2.addInp2(piece1)
	# ~ if (port1 == 'out'):
		# ~ if (port2 == 'inp'):
			# ~ piece1.addOut(piece2)
			# ~ piece2.addInp(piece1)
		# ~ if (port2 == 'trigger'):
			# ~ piece1.addOut(piece2)
			# ~ piece2.addTrigger(piece1)
	# ~ if (port1 == 'waves'):
		# ~ if (port2 == 'inp'):
			# ~ piece1.addOut(piece2)
			# ~ piece2.addInp(piece1)
		# ~ if (port2 == 'trigger'):
			# ~ piece1.addOutput(piece2)
			# ~ piece2.addTrigger(piece1)
	# ~ if (port1 == 'inp'):
		# ~ if (port2 == 'out'):
			# ~ piece1.addInp(piece2)
			# ~ piece2.addOut(piece1)
		# ~ if (port2 == 'waves'):
			# ~ piece1.addInp(piece2)
			# ~ piece2.addWaves(piece1)
	# ~ if (port1 == 'trigger'):
		# ~ if (port2 == 'out'):
			# ~ piece1.addTrigger(piece2)
			# ~ piece2.addOut(piece1)
		# ~ if (port2 == 'waves'):
			# ~ piece1.addTrigger(piece2)
			# ~ piece2.addOut(piece1)

# y: row, x: column
def add_connection(b,piece, y, x, port): #port can be dual, inp, out, trigger, output
	#connect with all pieces already on the board with the appropriate possible ports
	for el in b.pos[y][x]: #element will be composed of a list of tuples of pieces and ports
		# ~ print el[0].name
		if (el[0] == piece):
			pass
		elif port == "dual":
			if el[1] == "inp":
				directional_connect(piece,el[0],'out','inp')
			if el[1] == "inp2":
				directional_connect(piece,el[0],'out','inp2')
			if el[1] == "out":
				directional_connect(piece,el[0],'inp','out')
			if el[1] == "trigger":
				directional_connect(piece,el[0],'out','trigger')
			if el[1] == "hold":
				directional_connect(piece,el[0],'out','hold')
			if el[1] == "waves":
				directional_connect(piece,el[0],'out','waves')
		elif port == "inp":
			if el[1] == "out":
				directional_connect(piece,el[0],'inp','out')
		elif port == "trigger":
			if el[1] == "out":
				directional_connect(piece,el[0],'trigger','out')
		elif port == "waves": 
			if el[1] == "out":
				directional_connect(piece,el[0],'waves','out')
		elif port == "hold": 
			if el[1] == "out":
				directional_connect(piece,el[0],'hold','out')
		elif port == "out": 
			if el[1] == "inp":
				directional_connect(piece,el[0],'out','inp')
			if el[1] == "trigger":
				directional_connect(piece,el[0],'out','trigger')
			if el[1] == "hold":
				directional_connect(piece,el[0],'out','hold')
			if el[1] == "waves":
				directional_connect(piece,el[0],'out','waves')
		elif port == "inp2":
			if el[1] == "out":
				directional_connect(piece,el[0],'inp2','out')
    #Add the piece to the board to future things added can connect to it
	if port == "dual":
		i = (piece, "inp")
		b.pos[y][x].append(i)
		o = (piece, "out")
		b.pos[y][x].append(o)
	else:
		t = (piece, port)
		b.pos[y][x].append(t)
