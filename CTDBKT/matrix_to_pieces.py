import pieces
import cv2
import numpy as np
import pieces_location

def initialise_board(board_direction):
    board = pieces.Board(board_direction)
    return board

def bounding_box_shape_and_origin(coordinates):
    if not coordinates:
        return None

    min_row = min(coordinates, key=lambda coord: coord[0])[0]
    max_row = max(coordinates, key=lambda coord: coord[0])[0]
    min_col = min(coordinates, key=lambda coord: coord[1])[1]
    max_col = max(coordinates, key=lambda coord: coord[1])[1]

    rows = max_row - min_row + 1
    cols = max_col - min_col + 1

    return rows, cols, (min_row, min_col)

def get_contours(img, imgContour, in_area=5, show=False):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > in_area:
            cv2.drawContours(imgContour, cnt, -1, (255, 0, 255), 7)
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            x , y , w, h = cv2.boundingRect(approx)
            if show:
                cv2.rectangle(imgContour, (x , y), (x + w , y + h), (0, 255, 0), 2)
                cv2.imshow('contour',imgContour)
                cv2.waitKey(1)
            return x , y , w, h

def get_mask(color,imgHSV):
    lower = np.array(color[:3])  
    upper = np.array(color[3:]) 
    mask = cv2.inRange(imgHSV, lower, upper)
    return mask

def de_tilt(rotated, angle):
    (h, w) = rotated.shape[:2]
    center = (w // 2, h // 2)
    
    # Calculate the matrix to de-rotate the image
    M = cv2.getRotationMatrix2D(center, -angle, 1.0)
    
    # Apply the de-rotation transformation
    de_rotated = cv2.warpAffine(rotated, M, (w, h),
                                 flags=cv2.INTER_CUBIC,
                                 borderMode=cv2.BORDER_REPLICATE)

    return de_rotated

def get_ports_location(data_item, direct, output, frame_tilt, angle):
    # crop the piece out
    y1, x1, y2, x2 = [o[:-1] for o in output if o[-1] == pieces_location.class_id_mapping_reverse[data_item["type"]]][0]
    frame_focus = frame_tilt[int(x1):int(x2),int(y1):int(y2)]
    cv2.imshow('frame_focus', frame_focus)
    width_focus, height_focus = int(y2-y1), int(x2-x1) # horizontal length, vertical length of frame   
    cv2.waitKey(1)
    
    # apply masking on tape for directionality
    imgHSV = cv2.cvtColor(frame_focus, cv2.COLOR_BGR2HSV)

    if data_item["type"] == 'fm':
        mask = get_mask([0, 147, 106, 179, 255, 187], imgHSV)
        cv2.imshow('mask', mask)
        cv2.waitKey(1)
        result = cv2.bitwise_and(frame_focus, frame_focus, mask=mask) 
        contours_out = get_contours(mask,result, in_area=24, show=True) # in_area to be tuned (depending on distance between camera and board)
        
        if direct == "left_right":  
            direction = 0
        else:
            direction = 90

        if contours_out:
            x, y, _, _ = contours_out
            if direct == "left_right":
                if x > width_focus // 2 and y < height_focus // 2:
                    direction = 0
                elif x < width_focus // 2 and y > height_focus // 2:
                    direction = 180
            elif direct == "up_down":
                if x > width_focus // 2 and y > height_focus // 2:
                    direction = 90
                elif x < width_focus // 2 and y < height_focus // 2:
                    direction = 240
        
        return direction
    
    if data_item["type"] == 'mc':
        imgHSV = de_tilt(imgHSV, angle)
        mask = get_mask([8, 57, 33, 88, 182, 168], imgHSV)
        cv2.imshow('mask', mask)
        cv2.waitKey(1)
        result = cv2.bitwise_and(frame_focus, frame_focus, mask=mask)
        contours_out = get_contours(mask,result, in_area=24, show=True) # in_area to be tuned (depending on distance between camera and board)
        
        if direct == "left_right":  
            direction = 0
        else:
            direction = 90

        if contours_out:
            x, y, _, _ = contours_out
            if direct == "left_right":
                if x < width_focus // 2 and y < height_focus // 2:
                    direction = 0
                elif x > width_focus // 2 and y > height_focus // 2:
                    direction = 180
            elif direct == "up_down":
                if x > width_focus // 2 and y < height_focus // 2:
                    direction = 90
                elif x < width_focus // 2 and y > height_focus // 2:
                    direction = 240
        
        return direction
    
    if data_item["type"] == 'led':
        mask = get_mask([0, 0, 95, 91, 124, 209], imgHSV)
        cv2.imshow('mask', mask)
        cv2.waitKey(1)
        result = cv2.bitwise_and(frame_focus, frame_focus, mask=mask)
        contours_out = get_contours(mask,result, in_area=50, show=True) # in_area should be tuned

        if direct == "left_right":  
            direction = 0
        else:
            direction = 90
        if contours_out:
            x, y, _, _ = contours_out
            if direct == "left_right":
                if x < width_focus // 2:
                    direction = 0
                elif x > width_focus // 2:
                    direction = 180
            elif direct == "up_down":
                if y > height_focus // 2: 
                    direction = 90
                elif y < height_focus // 2:
                    direction = 240
        
        return direction

def data_to_board(board, data, output, frame_tilt, angle, contribution={}):

    present_pieces = []

    for data_item in data:
        rows, cols, origin = bounding_box_shape_and_origin(data_item["pegs_kept"])
        if data_item["type"] == "wire":
            
            ident = pieces.Wire.w_id
            pieces.Wire.w_id += 1

            if rows == 1:
                present_pieces.append(pieces.Wire(f"w{ident}", origin, 0, cols))
            elif cols == 1:
                present_pieces.append(pieces.Wire(f"w{ident}", origin, 90, rows))
            else:
                pass

        if data_item["type"] == "fm":
            
            ident = pieces.FM.fm_id
            pieces.FM.fm_id += 1

            if rows == 2 and cols == 3:
                direct = "left_right"
                direction = get_ports_location(data_item, direct, output, frame_tilt, angle)
                present_pieces.append(pieces.FM(f"fm{ident}", origin, direction))
            elif rows == 3 and cols == 2:
                direct = "up_down"
                direction = get_ports_location(data_item, direct, output, frame_tilt, angle)
                present_pieces.append(pieces.FM(f"fm{ident}", origin, direction))
            else:
                pass
            
        if data_item["type"] == "buzzer":
            
            ident = pieces.Buzzer.buz_id
            pieces.Buzzer.buz_id += 1

            if rows == 1:
                present_pieces.append(pieces.Buzzer(f"buz{ident}", origin, 0))
            elif cols == 1:
                present_pieces.append(pieces.Buzzer(f"buz{ident}", origin, 90))
            else:
                pass
            
        if data_item["type"] == "reed_switch":
            
            ident = pieces.ReedSwitch.rsw_id
            pieces.ReedSwitch.rsw_id += 1

            if rows == 1:
                present_pieces.append(pieces.ReedSwitch(f"rsw{ident}", origin, 0))
            elif cols == 1:
                present_pieces.append(pieces.ReedSwitch(f"rsw{ident}", origin, 90))
            else:
                pass
            
        if data_item["type"] == "button_switch":
            
            ident = pieces.ButtonSwitch.bsw_id
            pieces.ButtonSwitch.bsw_id += 1

            if rows == 1:
                present_pieces.append(pieces.ButtonSwitch(f"bsw{ident}", origin, 0))
            elif cols == 1:
                present_pieces.append(pieces.ButtonSwitch(f"bsw{ident}", origin, 90))
            else:
                pass
            
        if data_item["type"] == "switch":

            ident = pieces.Switch.sw_id
            pieces.Switch.sw_id += 1

            if rows == 1:
                present_pieces.append(pieces.Switch(f"sw{ident}", origin, 0))
            elif cols == 1:
                present_pieces.append(pieces.Switch(f"sw{ident}", origin, 90))
            else:
                pass

        if data_item["type"] == "cds":
            
            ident = pieces.Cds.c_id
            pieces.Cds.c_id += 1

            if rows == 1:
                present_pieces.append(pieces.Cds(f"c{ident}", origin, 0))
            elif cols == 1:
                present_pieces.append(pieces.Cds(f"c{ident}", origin, 90))
            else:
                pass

        if data_item["type"] == "led":
            
            ident = pieces.Led.led_id
            pieces.Led.led_id += 1

            if rows == 1:
                direct = "left_right"
                direction = get_ports_location(data_item, direct, output, frame_tilt, angle)
                present_pieces.append(pieces.Led(f"led{ident}", origin, direction))
            elif cols == 1:
                direct = "up_down"
                direction = get_ports_location(data_item, direct, output, frame_tilt, angle)
                present_pieces.append(pieces.Led(f"led{ident}", origin, direction))
            else:
                pass
            
        if data_item["type"] == "lamp":
            
            ident = pieces.Lamp.la_id
            pieces.Lamp.la_id += 1

            if rows == 1:
                present_pieces.append(pieces.Lamp(f"la{ident}", origin, 0))
            elif cols == 1:
                present_pieces.append(pieces.Lamp(f"la{ident}", origin, 90))
            else:
                pass
        
        if data_item["type"] == "battery":

            ident = pieces.Battery.b_id
            pieces.Battery.b_id += 1

            if rows == 3 and cols == 2:
                removed_pegs = list(data_item["pegs_removed"].keys())
                if len(removed_pegs) != 0:
                    if removed_pegs[0][1] == origin[1] + 2:
                        direction = 0
                    elif removed_pegs[0][1] == origin[1] - 1:
                        direction = 180
                elif origin[1] > board.cols / 2:
                    direction = 0
                else:
                    direction = 180
                
                present_pieces.append(pieces.Battery(f"b{ident}", origin, direction))

            elif rows == 2 and cols == 3:
                removed_pegs = list(data_item["pegs_removed"].keys())
                if len(removed_pegs) != 0:
                    if removed_pegs[0][0] == origin[0] + 2:
                        direction = 90
                    elif removed_pegs[0][0] == origin[0] - 1:
                        direction = 240
                elif origin[0] > board.rows / 2:
                    direction = 90
                else:
                    direction = 240
            
                present_pieces.append(pieces.Battery(f"b{ident}", origin, direction))

            else:
                pass

        if data_item["type"] == "speaker":
            
            ident = pieces.Speaker.sp_id
            pieces.Speaker.sp_id += 1

            if rows == 1:
                present_pieces.append(pieces.Speaker(f"sp{ident}", origin, 0))
            elif cols == 1:
                present_pieces.append(pieces.Speaker(f"sp{ident}", origin, 90))
            else:
                pass

        if data_item["type"] == "mc":
            
            ident = pieces.MC.mc_id
            pieces.MC.mc_id += 1

            if rows == 2 and cols == 3:
                direct = "left_right"
                direction = get_ports_location(data_item, direct, output, frame_tilt, angle)
                present_pieces.append(pieces.MC(f"mc{ident}", origin, direction))
            elif rows == 3 and cols == 2:
                direct = "up_down"
                direction = get_ports_location(data_item, direct, output, frame_tilt, angle)
                present_pieces.append(pieces.MC(f"mc{ident}", origin, direction))
            else:
                pass
        
        if data_item["type"] == "motor":
            
            ident = pieces.Motor.mo_id
            pieces.Motor.mo_id += 1

            if rows == 1:
                present_pieces.append(pieces.Motor(f"mo{ident}", origin, 0))
            elif cols == 1:
                present_pieces.append(pieces.Motor(f"mo{ident}", origin, 90))
            else:
                pass

    changes = board.swap_pieces(present_pieces, contribution)
    return board, changes