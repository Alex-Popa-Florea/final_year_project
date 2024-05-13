import printscreen
import pieces
import connections
import pieces_location
import cv2
import numpy as np
import collections

def correct_size(w):
    """
    Correct the size of a piece, such as a wire, to ensure accurate representation, 
    especially when overlapping with other pieces.

    Args:
        w (Piece): The piece to be corrected in terms of size.
    """
    if w.type == 'speaker' and (w.y1+1==w.y2):
        w.y1 += 1
    # to-do: check speaker in another direction
    elif w.type == 'wire':
        if w.x1 == w.x2:
            if w.y1 % 2 != 0:
                w.y1 -= 1
            if w.y2 % 2 != 0:
                w.y2 += 1
        else:
            if w.x1 % 2 != 0:
                w.x1 -= 1
            if w.x2 % 2 != 0:
                w.x2 += 1

def getContours(img,imgContour,in_area=5,show=False):
    """
    Used to find the location of tape on FM,MC and LED (used to checking their direction)
    
    """
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        print("LOOOOOL")
        
        area = cv2.contourArea(cnt)
        print(area)
        #areaMin = cv2.getTrackbarPos("Area", "Parameters")
        #print(areaMin)
        if area > in_area:
            print("AHHHGGGG")
            print(imgContour)
            cv2.drawContours(imgContour, cnt, -1, (255, 0, 255), 7)
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            x , y , w, h = cv2.boundingRect(approx)
            if show:
                cv2.rectangle(imgContour, (x , y ), (x + w , y + h ), (0, 255, 0), 2)
                cv2.imshow('contour',imgContour)
                cv2.waitKey(1)
            return x , y , w, h

def get_mask(color,imgHSV):
    lower = np.array(color[:3])  
    upper = np.array(color[3:]) 
    mask = cv2.inRange(imgHSV, lower, upper)
    return mask

def de_tilt(rotated, angle):
    """
    Corrects image tilt caused by rotation, which may lead to issues when determining directions of MC and FM signals.

    Args:
        rotated (numpy.ndarray): The rotated image to be corrected.
        angle (float): The angle of rotation applied to the image in degrees.

    Returns:
        numpy.ndarray: The de-tilted image after applying the correction.
    """
    (h, w) = rotated.shape[:2]
    center = (w // 2, h // 2)
    
    # Calculate the matrix to de-rotate the image
    M = cv2.getRotationMatrix2D(center, -angle, 1.0)
    
    # Apply the de-rotation transformation
    de_rotated = cv2.warpAffine(rotated, M, (w, h),
                                 flags=cv2.INTER_CUBIC,
                                 borderMode=cv2.BORDER_REPLICATE)

    return de_rotated
        
def get_ports_location(piece,output,frame_tilt,angle,show=False):
    """
    Get the port locations of FM and MC, and the direction of LED.

    Args:
        piece (Piece): the piece to be determined the ports location or direction
        output (numpy.ndarray): the matrix with information of piece location and piece id
        frame_tilt (numpy.ndarray): tilted frame to be used
        angle (float): angle use to tilt the frame
        show (bool, optional): whether to show the images. Defaults to False.

    Returns:
        _type_: _description_
    """
    # crop the piece out
    y1,x1,y2,x2 = [o[:-1] for o in output if o[-1]== pieces_location.class_id_mapping_reverse[piece.type]][0]
    frame_focus = frame_tilt[int(x1):int(x2),int(y1):int(y2)]
    cv2.imshow('frame_focus',frame_focus)
    #frame_focus = de_tilt(frame_focus, angle)
    #cv2.imshow('frame_focus',frame_focus)
    width_focus, height_focus = int(y2-y1), int(x2-x1) # horizontal length, vertical length of frame   
    cv2.waitKey(1)
    
    # apply masking on tape for directionality
    imgHSV = cv2.cvtColor(frame_focus, cv2.COLOR_BGR2HSV)

    if piece.type == 'fm':
        mask = get_mask([0,147,106,179,255,187],imgHSV) # masking to be tuned
        cv2.imshow('mask',mask)
        cv2.waitKey(1)
        result = cv2.bitwise_and(frame_focus, frame_focus, mask=mask) 
        contours_out = getContours(mask,result,in_area=24,show=True) # in_area to be tuned (depending on distance between camera and board)
        
        if contours_out:
            y,x,_,_ = contours_out
            if width_focus > height_focus and x>height_focus//2 and y<width_focus//2: 
                print('fm is right')
                inp, waves, out = (piece.x1,piece.y2), (piece.x1+2,piece.y2), (piece.x2,piece.y2) 
            elif width_focus > height_focus and x<height_focus//2 and y>width_focus//2: 
                print('fm is left')
                inp, waves, out = (piece.x1,piece.y1), (piece.x1+2,piece.y1), (piece.x2,piece.y1)
            elif width_focus < height_focus and x>height_focus//2 and y>width_focus//2: 
                print('fm is up')
                inp, waves, out = (piece.x1,piece.y1), (piece.x1,piece.y1+2), (piece.x1,piece.y2)
            elif width_focus < height_focus and x<height_focus//2 and y<width_focus//2:
                print('fm is down')
                inp, waves, out = (piece.x2,piece.y1), (piece.x2,piece.y1+2), (piece.x2,piece.y2)
            return (inp, waves, out) 
    if piece.type == 'mc':
        imgHSV = de_tilt(imgHSV,angle)
        mask = get_mask([8,57,33,88,182,168],imgHSV) # masking to be tuned
        cv2.imshow('mask',mask)
        cv2.waitKey(1)
        result = cv2.bitwise_and(frame_focus, frame_focus, mask=mask)
        contours_out = getContours(mask,result,in_area=24,show=True) # in_area to be tuned (depending on distance between camera and board)
        
        if contours_out:
            y,x,_,_ = contours_out
            if width_focus > height_focus and x > height_focus//2 :
                print('mc is left')
                trigger, inp, hold, waves, out = (piece.x1,piece.y1),(piece.x1+2,piece.y1),(piece.x2,piece.y1),(piece.x1,piece.y2),(piece.x2,piece.y2)
            elif width_focus > height_focus and x<height_focus//2 :
                print('mc is right')
                trigger, inp, hold, waves, out = (piece.x2,piece.y2),(piece.x1+2,piece.y2),(piece.x1,piece.y2),(piece.x2,piece.y1),(piece.x1,piece.y1)
            elif width_focus < height_focus and y>width_focus//2: # change to  edge_y1>width_focus//2 different color masking (now for prevent masking color from other components)
                print('mc is down')
                trigger, inp, hold, waves, out = (piece.x2,piece.y1),(piece.x2,piece.y1+2),(piece.x2,piece.y2),(piece.x1,piece.y1),(piece.x1,piece.y2)
            elif width_focus < height_focus and y<width_focus//2:
                print('mc is up')
                trigger, inp, hold, waves, out = (piece.x1,piece.y2),(piece.x1,piece.y1+2),(piece.x1,piece.y1),(piece.x2,piece.y2),(piece.x2,piece.y1)
            return (trigger, inp, hold, waves, out) 
    if piece.type == 'led':
        mask = get_mask([0,0,95,91,124,209],imgHSV) # masking to be tuned
        result = cv2.bitwise_and(frame_focus, frame_focus, mask=mask)
        contours_out = getContours(mask,result,in_area=50,show=True) # in_area should be tuned
        
        if contours_out:
            y,x,h,w = contours_out
            if width_focus < height_focus: # LED is horizontal
                if x+w > height_focus//2:
                    print('LED is horizontal and positive on right')
                    inp, out = (piece.x1,piece.y2), (piece.x1,piece.y1)
                elif x < height_focus//2:
                    print('LED is horizontal and positive on left')
                    inp, out = (piece.x1,piece.y1), (piece.x1,piece.y2)
            if width_focus > height_focus: # LED is vertical
                if y > width_focus//2:
                    print('LED is vertical and positive on top')
                    inp, out = (piece.x1,piece.y1), (piece.x2,piece.y1)
                else:
                    print('LED is vertical and positive on bottom')
                    inp, out = (piece.x2,piece.y1), (piece.x1,piece.y1)
            return (inp, out)

def add_new_piece(data,output,frame_tilt,angle,board,all_pieces):
    """Add new piece locations and connection to classes

    Args:
        data (class, dict for now): the message from previous step, it stores location (start, end, width, height), type <-- to be determined 
        (depends on the output from pieceOnEachLocation or write another function to combine the results we want)
    """
    # for now, we use dict, can be changed to class afterwards
    if data['type'] == 'wire':
        printscreen.printPiece("added wire")
        name = 'w' + str(pieces.Wire.w_id)
        pieces.Wire.w_id = pieces.Wire.w_id+1
        w = pieces.Wire(name,data['x1'], data['x2'], data['y1'],data['y2'])
        correct_size(w)
        # add connection
        for i in range(w.x1, w.x2+1): 
            for j in range(w.y1, w.y2+1):
                connections.add_connection(board,w,i,j,"dual") 
        print('location',(w.x1,w.y1),( w.x2, w.y2))
        all_pieces.append(w)
        
    elif data['type'] == "switch":
        printscreen.printPiece("added switch")
        name = 's' + str(pieces.Switch.s_id)
        pieces.Switch.s_id = pieces.Switch.s_id+1
        s = pieces.Switch(name,data['x1'], data['x2'], data['y1'],data['y2']) # data.start.y, data.start.x, data.end.y, data.end.x
        correct_size(s)
        # add connection
        connections.add_connection(board,s,s.x1, s.y1, "dual")
        connections.add_connection(board,s, s.x2, s.y2, "dual")
        all_pieces.append(s)
        
    elif (data['type'] == "reed"):  # data.type
        printscreen.printPiece("added reed")
        name = 'r' + str(pieces.Reed.reed_id)
        pieces.Reed.reed_id = pieces.Reed.reed_id+1
        r = pieces.Reed(name,data['x1'], data['x2'], data['y1'],data['y2']) # data.start.y, data.start.x, data.end.y, data.end.x
        correct_size(r)
        # add connection
        connections.add_connection(board,r, r.x1, r.y1, "dual")
        connections.add_connection(board,r, r.x2, r.y2, "dual")
        all_pieces.append(r)
    
    elif (data['type'] == "push button"):  # data.type
        printscreen.printPiece("added button")
        name = 'bu' + str(pieces.Button.bu_id)
        pieces.Button.bu_id = pieces.Button.bu_id+1
        bu = pieces.Button(name,data['x1'], data['x2'], data['y1'],data['y2']) # data.start.y, data.start.x, data.end.y, data.end.x
        correct_size(bu)
        # add connection
        connections.add_connection(board,bu, bu.x1, bu.y1, "dual")
        connections.add_connection(board,bu, bu.x2, bu.y2, "dual")
        all_pieces.append(bu)
    
    elif (data['type'] == "led"):
        printscreen.printPiece("added LED")
        name = 'l' + str(pieces.Led.l_id)
        pieces.Led.l_id = pieces.Led.l_id+1
        l = pieces.Led(name,data['x1'], data['x2'], data['y1'],data['y2']) # data.start.y, data.start.x, data.end.y, data.end.x
        correct_size(l)
        # add connection
        inp_out = get_ports_location(l,output,frame_tilt,angle)

        if inp_out:
            inp, out = inp_out
            print('inp',inp,'out',out)
            connections.add_connection(board,l, inp[0], inp[1], "dual")
            connections.add_connection(board,l, inp[0], inp[1], "inp2")
            connections.add_connection(board,l, out[0], out[1], "dual")

        all_pieces.append(l)
    
    elif (data['type'] == "lamp"):
        printscreen.printPiece("added Lamp")
        name = 'la' + str(pieces.Lamp.lamp_id)
        pieces.Lamp.lamp_id = pieces.Lamp.lamp_id+1
        la = pieces.Lamp(name,data['x1'], data['x2'], data['y1'],data['y2']) # data.start.y, data.start.x, data.end.y, data.end.x
        correct_size(la)
        # add connection
        connections.add_connection(board,la, la.x1, la.y1, "dual")
        connections.add_connection(board,la, la.x2, la.y2, "dual")
        all_pieces.append(la)
    
    elif (data['type'] == "speaker"):
        printscreen.printPiece("added Speaker")
        name = 'sp' + str(pieces.Speaker.sp_id)
        pieces.Speaker.sp_id = pieces.Speaker.sp_id + 1
        sp = pieces.Speaker(name,data['x1'], data['x2'], data['y1'],data['y2']) # data.start.y, data.start.x, data.end.y, data.end.x
        correct_size(sp) # to check!!
        # add connection
        connections.add_connection(board,sp, sp.x1, sp.y1, "dual")
        connections.add_connection(board,sp, sp.x2, sp.y2, "dual")
        all_pieces.append(sp)
        
    elif (data['type'] == "buzzer"):
        printscreen.printPiece("added buzzer")
        name = 'buz' + str(pieces.Buzzer.buz_id)
        pieces.Buzzer.buz_id = pieces.Buzzer.buz_id + 1
        buz = pieces.Buzzer(name,data['x1'], data['x2'], data['y1'],data['y2']) # data.start.y, data.start.x, data.end.y, data.end.x
        correct_size(buz)
        # add connection !! occupied two columns, need to be solved (same as speaker)
        connections.add_connection(board,buz, buz.x1, buz.y1, "dual")
        connections.add_connection(board,buz, buz.x2, buz.y2, "dual")
        all_pieces.append(buz)
    
    elif (data['type'] == "motor"):
        printscreen.printPiece("added motor")
        name = 'm' + str(pieces.Motor.m_id)
        pieces.Motor.m_id = pieces.Motor.m_id + 1
        m = pieces.Motor(name,data['x1'], data['x2'], data['y1'],data['y2']) # data.start.y, data.start.x, data.end.y, data.end.x
        correct_size(m)
        # add connection
        connections.add_connection(board,m, m.x1, m.y1, "dual")
        connections.add_connection(board,m, m.x2, m.y2, "dual")
        all_pieces.append(m)
    
    elif (data['type'] == "battery"):
        printscreen.printPiece("added battery")
        name = 'b' + str(pieces.Battery.b_id)
        pieces.Battery.b_id = pieces.Battery.b_id+1
        b = pieces.Battery(name,data['x1'], data['x2'], data['y1'],data['y2']) # data.start.y, data.start.x, data.end.y, data.end.x
        if abs(b.x1-b.x2)>abs(b.y1-b.y2):
            if b.y1<6: # horizontal and left
                connections.add_connection(board, b, b.x1, b.y2, "out") # position of pos port
                connections.add_connection(board, b, b.x2, b.y2, "inp") # position of neg port
            else: # horizontal and right
                connections.add_connection(board, b, b.x1, b.y1, "out") # position of pos port
                connections.add_connection(board, b, b.x2, b.y1, "inp") # position of neg port
        else:
            if b.x2<6: # vertial and top
                connections.add_connection(board, b, b.x2, b.y1, "out") # position of pos port
                connections.add_connection(board, b, b.x2, b.y2, "inp") # position of neg port
            else:
                connections.add_connection(board, b, b.x1, b.y2, "out") # position of pos port
                connections.add_connection(board, b, b.x1, b.y1, "inp") # position of neg port
        all_pieces.append(b)
    
    elif (data['type'] == "mc"):
        printscreen.printPiece("added music circuit")
        name = 'mc' + str(pieces.Music_Circuit.mc_id)
        pieces.Music_Circuit.mc_id = pieces.Music_Circuit.mc_id+1
        mc = pieces.Music_Circuit(name,data['x1'], data['x2'], data['y1'],data['y2']) # data.start.y, data.start.x, data.end.y, data.end.x
        trigger, inp, hold, waves, out = get_ports_location(mc,output,frame_tilt,angle)
        print(trigger, inp, hold, waves, out)
        connections.add_connection(board, mc, trigger[0], trigger[1], "trigger")
        connections.add_connection(board, mc, inp[0], inp[1], "inp")
        connections.add_connection(board, mc, hold[0], hold[1], "hold")
        connections.add_connection(board, mc, waves[0], waves[1], "waves")
        connections.add_connection(board, mc, out[0], out[1], "out")
        all_pieces.append(mc)
    
    elif (data['type'] == "fm"):
        printscreen.printPiece("added fm")
        name = 'fm' + str(pieces.FM.fm_id)
        pieces.FM.fm_id = pieces.FM.fm_id+1
        fm = pieces.FM(name,data['x1'], data['x2'], data['y1'],data['y2']) # data.start.y, data.start.x, data.end.y, data.end.x
        # to-do: add port
        inp, waves, out = get_ports_location(fm,output,frame_tilt,angle)
        connections.add_connection(board, fm, inp[0], inp[1], "inp")
        connections.add_connection(board, fm, waves[0], waves[1], "waves")
        connections.add_connection(board, fm, out[0], out[1], "out")
        all_pieces.append(fm)
    return board,all_pieces

def initialize_board():
    
    board = pieces.Board("b1", 13, 15)
    all_pieces = []
    previous_data = []
    hand_history = collections.defaultdict(list)
    output_get_pegs = None
    person_id = None

    return board, all_pieces, previous_data, hand_history, output_get_pegs, person_id

def display_attributes(in_class):
    """
    Display all attributes of the Piece
    """
    attributes = dir(in_class)
    for attribute in attributes:
        if not attribute.startswith('__'):
            value = getattr(in_class, attribute)
            print(f"{attribute}: {value}")

def check_changes(previous_data,data,output):   
    """   
    Check for added pieces in the current frame compared to the previous frame.

    Args:
        previous_data (list): The data from the previous frame.
        data (list): The data from the current frame.
        output (numpy.ndarray): the matrix with information of piece location and piece id

    Returns:
        tuple: A tuple containing two lists - 'added' and 'removed'.
               'added' contains items present in 'data' but not in 'previous_data'.
               'removed' contains items present in 'previous_data' but not in 'data'.
    """     
    added = [(item,o) for item,o in zip(data,output) if item not in previous_data]
    removed = [item for item in previous_data if item not in data]
    return added,removed

def find_person_id(hand_history, output_add):
    person_id = None
    center_piece = ((output_add[2]+output_add[0])//2,(output_add[3]+output_add[1])//2)

    if hand_history.get('ID: 1') or hand_history.get('ID: 0'):
        for hand_center in hand_history.get('ID: 1', []):
            if (hand_center[0] - center_piece[0] < 5 and hand_center[1] - center_piece[1] < 20) or \
               (hand_center[0] - center_piece[0] < 20 and hand_center[1] - center_piece[1] < 5):
                person_id = 'ID: 1'
                break
        
        if not person_id:
            for hand_center in hand_history.get('ID: 0', []):
                if (hand_center[0] - center_piece[0] < 5 and hand_center[1] - center_piece[1] < 20) or \
                   (hand_center[0] - center_piece[0] < 20 and hand_center[1] - center_piece[1] < 5):
                    person_id = 'ID: 0'
                    break

        return person_id