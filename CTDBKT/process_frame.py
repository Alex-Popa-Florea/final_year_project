import cv2
import numpy as np
import pieces_location
import virtual_board_all

# crop frame to focus on board
def crop_frame_general(frame, crop_size=450, crop_hand_size=600, x_offeset = 0, y_offset = 0): #800 
    x, y, _ = frame.shape
    crop_x = (x - crop_size) // 2 + x_offeset
    crop_y = (y - crop_size) // 2 + y_offset
    frame_for_veri = frame[crop_x:crop_x + crop_size, crop_y:crop_y + crop_size]
    
    crop_x_hands = (x - crop_hand_size) // 2 + x_offeset
    crop_y_hands = (y - crop_hand_size) // 2 + y_offset

    frame_for_hand = frame[crop_x_hands:crop_x_hands + crop_hand_size, crop_y_hands:crop_y_hands + crop_hand_size] 
    
    rotated_frame = cv2.rotate(frame_for_veri, cv2.ROTATE_90_CLOCKWISE)
    
    return rotated_frame, frame_for_hand

# Process a frame using YOLO object detection, returning the pieces and their location
def yolo_process_frame(frame_tilt, model, matrixcoor_to_realcoor, peg_size):

    results = model.predict(frame_tilt, show=True, conf=0.3, verbose=False)

    for result in results:
        boxes = result.boxes
        output = np.hstack([boxes.xyxy, boxes.cls[:, np.newaxis]])

    output = np.array(sorted(output, key=lambda x: x[-1]))

    if len(output) != 0:
        output = output[output[:, -1] != 1]

    data = pieces_location.piece_on_each_location(output, matrixcoor_to_realcoor, peg_size)
        
    return data, output