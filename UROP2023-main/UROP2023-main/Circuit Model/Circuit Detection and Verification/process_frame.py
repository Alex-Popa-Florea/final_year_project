import cv2
import numpy as np
import pieces_location
import virtual_board_all

# crop frame to focus on board
def crop_frame(frame, crop_x=760, crop_y=250, crop_width=450, crop_height=500):
    frame_for_veri = frame[crop_y:crop_y + crop_height, crop_x:crop_x + crop_width]
    frame_for_hand = frame[crop_y:crop_y + crop_height, crop_x:crop_x + crop_width + 150]
    rotated_frame = cv2.rotate(frame_for_veri, cv2.ROTATE_90_CLOCKWISE)
    
    return rotated_frame, frame_for_hand

# # crop frame to focus on board
# def crop_frame_home(frame, crop_x=350, crop_y=200, crop_width=1000, crop_height=800):
#     frame_for_veri = frame[crop_y:crop_y + crop_height, crop_x:crop_x + crop_width]
#     # frame_for_hand = frame[crop_y - 100:crop_y + crop_height + 100, crop_x - 100:crop_x + crop_width + 10]
#     frame_for_hand = frame[crop_y - 100:crop_y + crop_height + 100, crop_x - 100:crop_x + crop_width + 10]
#     rotated_frame = cv2.rotate(frame_for_veri, cv2.ROTATE_90_CLOCKWISE)
    
#     return rotated_frame, frame_for_hand

# crop frame to focus on board
def crop_frame_home(frame, crop_x=580, crop_y=100, crop_width=720, crop_height=1000): #crop_x=40, crop_y=600, crop_width=720, crop_height=1000
    frame_for_veri = frame[crop_y:crop_y + crop_height, crop_x:crop_x + crop_width]
    # frame_for_hand = frame[crop_y - 100:crop_y + crop_height + 100, crop_x - 100:crop_x + crop_width + 10]
    frame_for_hand = frame #[crop_y - 100:crop_y + crop_height + 100, crop_x - 100:crop_x + crop_width + 100]
    #print(frame_for_veri.shape)
    #print(frame_for_hand.shape)
    rotated_frame = cv2.rotate(frame_for_veri, cv2.ROTATE_90_CLOCKWISE)
    #print(rotated_frame.shape)
    return rotated_frame, frame_for_hand

# crop frame to focus on board
def crop_frame_general(frame, crop_size=520): #800 
    x, y, _ = frame.shape
    crop_x = (x - crop_size) // 2
    crop_y = (y - crop_size) // 2
    #print(x)
    #print(y)
    #print(crop_x)
    #print(crop_y)
    frame_for_veri = frame[crop_x:crop_x + crop_size, crop_y:crop_y + crop_size]
    
    frame_for_hand = frame 
    
    rotated_frame = cv2.rotate(frame_for_veri, cv2.ROTATE_90_CLOCKWISE)
    
    return rotated_frame, frame_for_hand

def process_frame_with_yolo(frame_tilt, model, matrixcoor_to_realcoor, show=True):
    """
    Process a frame using YOLO object detection, draw the virtual board, and display it.

    Args:
        frame_tilt (numpy.ndarray): The input frame.
        model: The YOLO object detection model.
        matrixcoor_to_realcoor: A mapping between matrix coordinates and real-world coordinates.
        show (bool, optional): Whether to display the results (default is True).

    Returns:
        tuple: A tuple containing the following elements:
            - matrix (numpy.ndarray): Mapping between matrix entries and classes.
            - data (list): Data related to detected objects.
    """

    #print("MATRIX ORIG")
    #print(matrixcoor_to_realcoor)

    results = model.predict(frame_tilt, show=True, conf=0.3, verbose=False)
    # print("Results !!!")
    # print(results)

    for result in results:
        #print("Result !!!")
        #print(result)
        boxes = result.boxes
        #print("BOXES")
        #print(boxes)
        output = np.hstack([boxes.xyxy, boxes.cls[:, np.newaxis]])

    # Get the mapping between matrix entries and class, then draw the virtual board
    output = np.array(sorted(output, key=lambda x: x[-1]))

    #print("LMAOOOOO")
    #print(output)

    if len(output) != 0:
        output = output[output[:, -1] != 1]  # the output related to board ##error

    #print("LMAOOOOO2")
    #print(output)

    matrix, data = pieces_location.pieceOnEachLocation(output, matrixcoor_to_realcoor)

    #print(matrix)
    #print(data)

    # draw and display virtual board and board with pegs
    if show:
        final_image = virtual_board_all.show_estimated_board(matrix)
        final_image_bgr = cv2.cvtColor(np.array(final_image), cv2.COLOR_RGB2BGR)
        cv2.imshow("Virtual Board", final_image_bgr)
        

    return matrix, data, output
