import tasks
import printscreen


################################ FUNCTIONS RELATED TO PATHS AND CIRCUITS ################################
def printAllPaths(start, end, path, all_paths):
    """
    Find all paths from the 'start' piece to the 'end' piece in a graph.

    Args:
    start (Piece): The starting piece.
    end (Piece): The ending piece.
    path (list): The current path being explored.
    all_paths (list): A list to store all found paths.

    Returns:
    list: A list of all paths from 'start' to 'end' in the graph.
    """
    # Append the current piece to the path
    path.append(start.name)
    # Check if the current piece is the end piece
    if start.name == end.name:
        # If it is, append the path to the list of all paths
        all_paths.append(path)
        # ~ print (path)
        # ~ return (path)
    else:
        # ~ print (start.name)
        # ~ print (start.out)
        # If not, explore all outgoing pieces from the current piece
        for v in start.out:
            # Check if the neighbor piece has not been visited in this path
            if v.name not in path:
                # ~ print ("in here")
                # Recursively explore the neighbor piece
                printAllPaths(v, end, path[:], all_paths)
    # ~ path.pop()
    return all_paths
    # ~ path.pop()

def all_circuits(start, end, path, all_paths):
    """
    Find all circuits from the 'start' piece to the 'end' piece in a graph.

    Args:
    start (Piece): The starting piece.
    end (Piece): The ending piece.
    path (list): The current path being explored.
    all_paths (list): A list to store all found circuits.

    Returns:
    list: A list of all circuits from 'start' to 'end' in the graph.
    """
    path.append(start.name)
    if (start.name == end.name):
        all_paths.append(path)
    else:
        for v in start.out:
            if (v.name not in path):
                all_circuits(v, end, path[:], all_paths)
    return all_paths

def detect_circuit(piece,all_pieces): # MAIN FUNCTION CALLED: find any route back to start
    """
    Detect circuits from a given 'piece' to itself in a graph.

    Args:
    piece (Piece): The starting piece for circuit detection.
    all_pieces (list): A list of all pieces in the graph.

    Returns:
    list: A list of all detected circuits from 'piece' to itself.
    """
    all_paths = []
    start = piece
	# ~ print (all_pieces)
	# ~ print (start.out)
    for p in start.out:
        all_paths = all_circuits(p, start, [], []) # if more than one out, the last one will overwrite the previous ones
    return all_paths

############################# FUNCTIONS RELATD TO FINDING WHETHER PIECES EXISTS ########################
def test_piece(piece_name, all_pieces):
    """
    Test if a piece with a given name exists in the list of 'all_pieces'.

    Args:
    piece_name (str): The name of the piece to be tested.
    all_pieces (list): A list of all pieces in the circuit.

    Returns:
    int: 1 if the piece exists, 0 if it does not.
    """
    found_piece = False
    for piece in all_pieces:
        if piece.type == piece_name:
            found_piece = True
    if found_piece:
        printscreen.printSkill("The following exists in the circuit:", ' ')
        printscreen.printSkill(piece_name)
        return 1
    else:
        printscreen.printSkill("The following is NOT in the circuit:", ' ')
        printscreen.printSkill(piece_name)
        return 0
        

def find_piece_in_list(all_pieces, piece_type):
    """
    Find a piece with a specific type in a list of 'all_pieces'.

    Args:
    all_pieces (list): A list of all pieces to search through.
    piece_type (str): The type of the piece to find.

    Returns:
    Node or None: The first piece found with the specified type, or None if not found.
    """
    for p in all_pieces:
        if p.type == piece_type:
            return p
    return None

# def test_connection_speaker_mc(start, end, path, all_paths):
#     path.append(start.name)
#     if start.name == end.name:
#         all_paths.append(path)
#     else:
#         for v in start.waves:
#             # ~ print (v.name)
#             if v.name not in path:
#                 printAllPaths(v, end, path, all_paths)
#     return all_paths

############################# FUNCTIONS RELATED TO TESTING MC ###########################################
def test_connection_mc(start, end, path, all_paths):
    path.append(start.name)
    if start.name == end.name:
        all_paths.append(path)
    else:
        for v in start.waves:
            # ~ print (v.name)
            if v.name not in path:
                printAllPaths(v, end, path, all_paths)
    return all_paths
			
def check_mc(all_pieces, circuits):
    mc = find_piece_in_list(all_pieces, "mc")
    if mc is None:
        printscreen.printSkill("MC was NOT present and therefore NOT connected correctly")
        return 0
    pieces_inp = []
    for piece in mc.inp:
        pieces_inp.append(piece.name)
        
    mc_ok = False
    for circuit in circuits:
        for p in circuit:
            if p in pieces_inp:
                mc_ok = True
    if mc_ok:
        printscreen.printSkill("MC was connected correctly")
        return 1
    else:
        printscreen.printSkill("MC was NOT connected correctly")
        return 0
    
def check_signal(all_pieces, circuits):
    mc = find_piece_in_list(all_pieces, "mc")  # Calls a function find_piece_in_list() to find the "mc" piece
    
    if mc is None:
        # MC piece was not found, signal was not connected correctly
        return 0
    
    pieces_waves = []
    for piece in mc.waves:
        pieces_waves.append(piece.name)
    
    mc_ok = False
    for circuit in circuits:
        for p in circuit:
            if p in pieces_waves:
                mc_ok = True  # If any piece in the circuit matches a piece in mc.waves, set mc_ok to True
    
    if mc_ok:
        # MC was connected correctly to create a wave signal
        return 1
    else:
        # MC was NOT connected correctly to create a wave signal
        return 0

def check_hold(all_pieces, piece):
    conn_hold = False
    
    if piece == "switch":
        p = "s"
    else:
        p = "u"
    
    start = find_piece_in_list(all_pieces, "battery")
    end = find_piece_in_list(all_pieces, "mc")
    
    pieces_hold = []
    for piece in end.hold:
        pieces_hold.append(piece.name)
    
    paths = printAllPaths(start, end, [], [])
    for path in paths:
        if path[-2] in pieces_hold:
            for el in path:
                if el[0] == p:
                    conn_hold = True
    
    if conn_hold:
        # Proper piece attached to hold found
        return 1
    else:
        # Hold was not done correctly
        return 0

def check_trigger(all_pieces, p1, p2, p3="motor"):
    conn_trig = False
    conn_inp = False

    start = find_piece_in_list(all_pieces, "battery")
    end = find_piece_in_list(all_pieces, "mc")

    pieces_trigger = []
    for piece in end.trigger:
        pieces_trigger.append(piece.name)

    pieces_inp = []
    for piece in end.inp:
        pieces_inp.append(piece.name)

    paths = []
    if start is not None and end is not None:
        paths = printAllPaths(start, end, [], [])

    for path in paths:
        if path[-2] in pieces_trigger:
            # Check if motor in path:
            for el in path:
                if el[0] == "m":
                    conn_trig = True
        if path[-2] in pieces_inp:
            for el in path:
                if el[0] == "m":
                    conn_inp = True

    if conn_trig and (not conn_inp):
        # Proper Motor placement to Trigger found
        return 1
    else:
        # Motor was NOT correctly placed to Trigger
        return 0
    
def test_mc_skill(all_pieces, circuits, port, piece):
    obs = 0
    mc = find_piece_in_list(all_pieces, "mc")
    
    if mc is None:
        # MC was NOT present and therefore the MC skill was incorrect
        return 0
    
    if port == "trigger" and piece == "motor":
        motor = find_piece_in_list(all_pieces, "motor")
        if motor:
            # Check if motor is in path of trigger on mc, but not in path of inp on mc
            obs = check_trigger(all_pieces, "mc", "battery")
        else:
            pass
            # There is no motor in the circuit
    
    if port == "hold":
        obs = check_hold(all_pieces, piece)
    if port == "power":
        obs = check_mc(all_pieces, circuits)
    if port == "signal":
        obs = check_signal(all_pieces, circuits)
    
    return obs

################################### TESTS FOR CONNECTIONS ###############################################
def test_connection(p1, p2, all_pieces):
    start = find_piece_in_list(all_pieces, p1)
    end = find_piece_in_list(all_pieces, p2)
    
    # ~ print ("testing connecting between ")
    # ~ print (p1)
    # ~ print (p2)
    
    # ~ if start is None:
    #     printscreen.printSkill(p1, ' ')
    #     printscreen.printSkill("was not placed on board")
    # ~ if end is None:
    #     printscreen.printSkill(p2, ' ')
    #     printscreen.printSkill("was not placed on board")
    if start is None or end is None:
        return 2
    
    if p1 in ["speaker",'buzzer','led'] and p2 == "mc":
        path1 = test_connection_mc(end, start, [], [])
        path2 = []
        # ~ print (path1)
    else:
        path1 = printAllPaths(start, end, [], [])
        path2 = printAllPaths(end, start, [], [])
    
    # if p1 == "speaker" and p2 == "mc":
    #     path1 = test_connection_speaker_mc(end, start, [], [])
    #     path2 = []
    #     # ~ print (path1)
    # else:
    #     path1 = printAllPaths(start, end, [], [])
    #     path2 = printAllPaths(end, start, [], [])
    if path1 != [] or path2 != []:
        printscreen.printSkill("found a path between", " ")
        printscreen.printSkill(p1, " ")
        printscreen.printSkill("and", " ")
        printscreen.printSkill(p2)
        return 1
    else:
        printscreen.printSkill("did NOT find path between", " ")
        printscreen.printSkill(p1, " ")
        printscreen.printSkill("and", " ")
        # ~ print (p2)
        return 0

def test_closed(all_pieces,show=True):
    # ~ print ("testing if circuit closed")
    # ~ b = self.find_battery()
    b = find_piece_in_list(all_pieces, "battery")
    # ~ print b.name
    # circuit.spread_power(b, [])
    closed_circuits = []
    if b:
        closed_circuits = detect_circuit(b, all_pieces)
    if closed_circuits != []:
        if show:
            printscreen.printSkill("Circuit closed")
        return 1, closed_circuits
    else:
        if show:
            printscreen.printSkill("Circuit NOT closed")
        return 0, []

def test_connect_pieces(all_pieces):
    pieces_connected = 0
    pieces_not_connected = 0
    
    for piece in all_pieces:
        if (piece.inp == []) and (piece.out == []):
            pieces_not_connected += 1
        else:
            pieces_connected = 1
            
    if pieces_connected > (pieces_not_connected / 3.0):
        printscreen.printSkill("There were several pieces that were connected to other pieces")
        return 1
    else:
        printscreen.printSkill("Too many pieces were not connected to any others")
        return 0

################################ TEST FOR DIRECTIONALITY OF LED #########################################
def test_directionality(o, p, all_pieces):
    inp_ok = False
    out_ok = False

    is_circuit, circuits = test_closed(all_pieces,show=False)
    if o == 0 or is_circuit == 0:  # if the circuit does not have an LED, we can't test whether direction is right or wrong.
        return 2
    else:
        # first check if there is a way from the battery to the inp
        bat = find_piece_in_list(all_pieces, "battery")
        led = find_piece_in_list(all_pieces, "led")
        pieces_inp = []
        for piece in led.inp2:
            pieces_inp.append(piece.name)
        paths = []
        if bat and led:
            paths = printAllPaths(bat, led, [], [])
        #print(pieces_inp)
        for path in paths:
            if inp_ok:
                break
            for piece in pieces_inp:
                if piece in path:
                    #print(path)
                    inp_ok = True
                    break
        # print()
        pieces_out = []
        for piece in led.out:
            pieces_out.append(piece.name)
        paths = []
        if bat and led:
            paths = printAllPaths(led, bat, [], [])
        #print(pieces_out)
        for path in paths:
            if out_ok:
                break
            for piece in pieces_out:
                if piece in path:
                    #print(path)
                    out_ok = True
                    break
    #print(inp_ok,out_ok)
    if inp_ok and out_ok:
        printscreen.printSkill("LED directionality is correct")
        return 1
    else:
        printscreen.printSkill("LED directionality is NOT correct")
        return 0

################################# FUNCTIONS RELATED TO TESTING FM ########################################
def check_fm(all_pieces, circuits):
    fm = find_piece_in_list(all_pieces, "fm")
    if fm is None:
        printscreen.printSkill("FM was NOT present and therefore NOT connected correctly")
        return 0
    pieces_inp = []
    for piece in fm.inp:
        pieces_inp.append(piece.name)
        
    fm_ok = False
    for circuit in circuits:
        for p in circuit:
            if p in pieces_inp:
                fm_ok = True
    if fm_ok:
        printscreen.printSkill("FM was connected correctly")
        return 1
    else:
        printscreen.printSkill("FM was NOT connected correctly")
        return 0
    
def check_signal_fm(all_pieces, circuits):
    fm = find_piece_in_list(all_pieces, "fm")  # Calls a function find_piece_in_list() to find the "fm" piece
    
    if fm is None:
        # FM piece was not found, signal was not connected correctly
        return 0
    
    pieces_waves = []
    for piece in fm.waves:
        pieces_waves.append(piece.name)
    fm_ok = False
    #print(pieces_waves)
    for circuit in circuits:
        #print(circuit)
        for p in circuit:
            if p in pieces_waves:
                fm_ok = True  # If any piece in the circuit matches a piece in fm.waves, set fm_ok to True

    if fm_ok:
        # FM was connected correctly to create a wave signal
        return 1
    else:
        # FM was NOT connected correctly to create a wave signal
        return 0

def test_fm_skill(all_pieces, circuits, port, piece):
    obs = 0
    fm = find_piece_in_list(all_pieces, "fm")
    
    if fm is None:
        # FM was NOT present and therefore the FM skill was incorrect
        return 0
    
    if port == "power":
        obs = check_fm(all_pieces, circuits)
    if port == "signal":
        obs = check_signal_fm(all_pieces, circuits)
    
    return obs

############################# FUNCTIONS RELATED TO TESTING GATES ###########################################
def test_gate_skill(circuits, gate): 
    if gate == "and":
        # must contain a circuit that has both the switch and the button
        sw = False
        bu = False
        for circuit in circuits:
            for piece in circuit:
                if piece[0] == "s":
                    sw = True
                if piece[:2] == "bu":
                    bu = True
            # print(sw, bu,circuit)
            if sw and bu:
                printscreen.printSkill("The AND gate was applied correctly in the circuit")
                return 1
            else:
                printscreen.printSkill("The AND gate was NOT applied correctly in the circuit")
                return 0
    elif gate == "or":
        # must contain 2 circuits, each containing only the switch or the button
        only_sw = False
        only_bu = False
        print(circuits)
        for circuit in circuits:
            sw = False
            bu = False
            for piece in circuit:
                if piece[0] == "s":
                    sw = True
                if piece[:2] == "bu":
                    bu = True
            if sw and not bu:
                only_sw = True
            if bu and not sw:
                only_bu = True
        if only_sw and only_bu:
            printscreen.printSkill("The OR gate was applied correctly in the circuit")
            return 1
        else:
            printscreen.printSkill("The OR gate was NOT applied correctly in the circuit")
            return 0

############################# FINAL FUNCTION FOR OBSERVATION VECTOR #####################################
def update_skills(task, all_pieces):
    obs = []
    
    # Map task number to the corresponding task from tasks module
    task_mapping = {
    1: tasks.task1,
    2: tasks.task2,
    3: tasks.task3,
    4: tasks.task4,
    5: tasks.task5,
    6: tasks.task6,
    7: tasks.task7,
    8: tasks.task8,
    9: tasks.task9,
    10: tasks.task10,
    11: tasks.task11,
    12: tasks.task12,
    13: tasks.task13,
    14: tasks.task14,
    15: tasks.task15,
    16: tasks.task16,
    17: tasks.task17,
    18: tasks.task18,
    19: tasks.task19,
    20: tasks.task20,
    21: tasks.task21,
    22: tasks.task22,
    23: tasks.task23,
    24: tasks.task24,
    25: tasks.task25,
    26: tasks.task26,
    27: tasks.task27,
    28: tasks.task28,
    29: tasks.task29,
    # 30: tasks.task30,
    # 31: tasks.task31,
    # 32: tasks.task32,
    # 33: tasks.task33,
    # 34: tasks.task34
}
    
    task = task_mapping.get(task, None)
    if task is None:
        return  # Task not found
    
    ind = 0
    _, circuits = test_closed(all_pieces,show=False)
    for i in task.action:
        sk = tasks.all_skills[ind]  # The skill this position in the observation vector is related to
        
        if i == 0:  # If we don't need this skill
            # if isinstance(sk, tasks.PieceSkill):
            #     o = test_piece(sk.name, all_pieces)
            #     if o == 1:
            #         if ind != 3 and ind != 2:
            #             obs.append(3)  # Resistor related?
            #         elif task.action[2] == 0 and task.action[3] == 0:
            #             obs.append(3)
            #         else:
            #             obs.append(2)
            #     else:
            #         obs.append(2)
            # else:
            obs.append(2)
        if i == 1:
            # print(i,ind)
            if isinstance(sk, tasks.ClosingSkill):
                o, circuits = test_closed(all_pieces)
                #print('test_closed:', 'o:',o)
            if isinstance(sk, tasks.PieceSkill):
                o = test_piece(sk.name, all_pieces)
                #print('PieceSkill:', sk.name, 'o:', o)
            if isinstance(sk, tasks.ConnectionSkill):
                o = test_connection(sk.piece1, sk.piece2, all_pieces)
                #print('ConnectionSkill:', sk.piece1, sk.piece2, 'o:', o)
            if isinstance(sk, tasks.DirectionSkill):
                o = test_directionality(obs[0], sk.name, all_pieces)
                #print('test_directionality:', sk.name, 'o:', o)
            if isinstance(sk, tasks.MCSkill):
                o = test_mc_skill(all_pieces, circuits, sk.port, sk.piece)
                #print('MCSkill:', 'port:',sk.port, 'piece',sk.piece, 'o:', o)
            if isinstance(sk, tasks.FMSkill):
                o = test_fm_skill(all_pieces, circuits, sk.port, sk.piece)
                #print('FMSkill:', 'port:',sk.port, 'piece',sk.piece, 'o:', o)
            if isinstance(sk, tasks.GateSkill):
                o = test_gate_skill(circuits, sk.gate)
                #print('test_gate_skill:',sk.gate,'o:',o)
            if isinstance(sk, tasks.ConnectPieces):
                o = test_connect_pieces(all_pieces)
                #print('ConnectPieces:', 'o:', o)
            obs.append(o)
        ind += 1
        
    return obs