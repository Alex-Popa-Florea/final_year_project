import numpy as np
from PIL import Image, ImageDraw,ImageFont
import cv2
from ultralytics import YOLO
import time
import mediapipe as mp
import os


def whatAngle(boardBW):
    
	coords = np.column_stack(np.where(boardBW > 0))
	angle = cv2.minAreaRect(coords)[-1]

	if angle < -45:
		angle = -(90 + angle)
	 
	else:
		angle = -angle
		
	return angle


def tilt(image, angle):
    	# rotate the image to deskew it
	(h, w) = image.shape[:2]
	center = (w // 2, h // 2)
	M = cv2.getRotationMatrix2D(center, angle, 1.0)
	rotated = cv2.warpAffine(image, M, (w, h),
	flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

	return rotated

# def whatAngle(boardBW):
#     coords = np.column_stack(np.where(boardBW > 0))
#     rect = cv2.minAreaRect(coords)

#     # Get the angle from the minimum bounding rectangle
#     angle = rect[-1]

#     # Calculate the aspect ratio of the bounding rectangle
#     width, height = rect[1]
#     aspect_ratio = max(width, height) / min(width, height)

#     # Determine the desired orientation (longer side should be horizontal)
#     if aspect_ratio > 1:
#         # The longer side is vertical, we need to make it horizontal
#         if angle < -45:
#             angle = -(90 + angle)
#         else:
#             angle = -angle
#     else:
#         # The longer side is already horizontal, we need to make it vertical
#         angle = -(90 + angle)

#     return angle

# def tilt(image, angle):
#     # Make a copy of the image to avoid modifying the original
#     rotated_image = image.copy()

#     # Rotate the copied image to deskew it
#     (h, w) = rotated_image.shape[:2]
#     center = (w // 2, h // 2)
#     M = cv2.getRotationMatrix2D(center, angle, 1.0)
#     rotated = cv2.warpAffine(rotated_image, M, (w, h),
#                              flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

#     return rotated


def get_edges(image):
    # Convert the image to a NumPy array
    image_array = np.array(image)

    # Get the indices of non-zero elements (edge points)
    non_zero_indices = np.nonzero(image_array)

    # Get the minimum and maximum row and column indices of non-zero elements
    minRow, minColumn = np.min(non_zero_indices, axis=1)
    maxRow, maxColumn = np.max(non_zero_indices, axis=1)

    extLeft = minColumn
    extRight = maxColumn
    extTop = minRow
    extBot = maxRow
    return (extLeft, extRight, extBot, extTop)

def get_board_mask(img):
    color = [0, 0, 0, 255, 255, 50]
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # cv2.imshow("test", imgHSV)
    lower = np.array(color[:3])  
    upper = np.array(color[3:]) 
    mask = cv2.inRange(imgHSV, lower, upper)
    return mask

def get_pegs(img,x1,x2,y1,y2):
    matrixcoor_to_realcoor = {}
    dist_from_edge = [(x2-x1)/13,(y2-y1)/15]
    board_width = x2-x1-2*dist_from_edge[0]
    board_height = y2-y1-2*dist_from_edge[1]
    horizontal_interval = board_width / 12
    vertical_interval = board_height / 14
    img_circle = img.copy()
    
    # relate matrix coordinate to real peg coordinate
    for i in range(0,13):
        for j in range(0,15):
            matrixcoor_to_realcoor[i,j] = np.array([x1 + int(horizontal_interval * i + dist_from_edge[0]), y1 + int(vertical_interval * j + dist_from_edge[1])])
    
    for key in matrixcoor_to_realcoor:
        cv2.circle(img_circle, matrixcoor_to_realcoor[key], 2, (200, 200, 200), -1)
    
    return img_circle,matrixcoor_to_realcoor

def draws_pegs_on_rotated_board(image,draw_edge=False):
    #time1=time.time()
    boardBW = get_board_mask(image)
    angle = whatAngle(boardBW)
    #time2=time.time()
    #print("masking and calculate angle time:", time2-time1)
    boardBW_tilt = tilt(boardBW, angle) 
    image_tilt = tilt(image, angle) 
    #time3=time.time()
    #print("deskew time:", time3-time2)
    # cv2.imwrite('board_deskew.png',image_tilt)  
            
    #get the max edges of the board then draw edges and pegs on it
    x1,x2,y1,y2 = get_edges(boardBW_tilt)
    #time4=time.time()
    #print("get_edges:", time4-time3)
    img_circle, matrixcoor_to_realcoor = get_pegs(image_tilt,x1,x2,y1,y2)
    #time5=time.time()
    #print("get_pegs:", time5-time4)
    
    if draw_edge:
        cv2.rectangle(img_circle, (x1, y1), (x2, y2), (0, 255, 0), 3)
    # cv2.imwrite('board_with_pegs.png',img_circle)    
    return matrixcoor_to_realcoor, image_tilt, img_circle, angle

def round_to_integer_with_error(float_number, error_rate = 0.35, down = True):
    if down:
        lower_integer = int(float_number)

        # Calculate the error between the float number and the lower integer
        error = float_number - lower_integer

        # Check if the error is within the custom error rate
        if error <= error_rate:
            return lower_integer - 1
        else:
            return lower_integer 
    else:
        upper_integer = np.ceil(float_number).astype(int)

        # Calculate the error between the float number and the upper integer
        error = upper_integer - float_number

        # Check if the error is within the custom error rate
        if error <= error_rate:
            return upper_integer + 1
        else:
            return upper_integer

# def translate_coordinates(r):
#     x1,y1,x2,y2,class_id = r
#     grid_x1 = round_to_integer_with_error(((x1-x0) / x_len) * 12,down=False)
#     grid_y1 = round_to_integer_with_error(((y1-y0) / y_len) * 14,down=False)
#     grid_x2 = round_to_integer_with_error(((x2-x0) / x_len) * 12)
#     grid_y2 = round_to_integer_with_error(((y2-y0) / y_len) * 14)
#     # if class_id == 11:
#     #     print("x1:",((x1-x0) / x_len) * 12,grid_x1)
#     #     print("y1:",((y1-y0) / y_len) * 14,grid_y1)
#     #     print("x2:",((x2-x0) / x_len) * 12,grid_x2)
#     #     print("y2:",((y2-y0) / y_len) * 14,grid_y2)
        
#     grid_x2 = max(grid_x1,grid_x2)
#     grid_y2 = max(grid_y1,grid_y2)

#     grid_x1 = max(0, min(grid_x1, 12 - 1))
#     grid_y1 = max(0, min(grid_y1, 14 - 1))
#     grid_x2 = max(0, min(grid_x2, 12 - 1))
#     grid_y2 = max(0, min(grid_y2, 14 - 1))
    
#     return 12-grid_x2, 12-grid_x1,grid_y1,grid_y2

def matrix_class_mapping(results,matrixcoor_to_realcoor):
    x0,y0 = matrixcoor_to_realcoor[(0,14)]
    matrix = np.zeros((13, 15))-1
    x_len, y_len = np.abs(matrixcoor_to_realcoor[(0,0)]-matrixcoor_to_realcoor[(12,14)])
    results = sorted(results,key = lambda x:x[-1])

    for r in results:
        x1,y1,x2,y2,class_id = r
        grid_x1 = round_to_integer_with_error(((x1-x0) / x_len) * 12,down=False)
        grid_y1 = round_to_integer_with_error(((y1-y0) / y_len) * 14,down=False)
        grid_x2 = round_to_integer_with_error(((x2-x0) / x_len) * 12)
        grid_y2 = round_to_integer_with_error(((y2-y0) / y_len) * 14)
        # if class_id == 11:
        #     print("x1:",((x1-x0) / x_len) * 12,grid_x1)
        #     print("y1:",((y1-y0) / y_len) * 14,grid_y1)
        #     print("x2:",((x2-x0) / x_len) * 12,grid_x2)
        #     print("y2:",((y2-y0) / y_len) * 14,grid_y2)
        
        grid_x2 = max(grid_x1,grid_x2)
        grid_y2 = max(grid_y1,grid_y2)

        grid_x1 = max(0, min(grid_x1, 12 - 1))
        grid_y1 = max(0, min(grid_y1, 14 - 1))
        grid_x2 = max(0, min(grid_x2, 12 - 1))
        grid_y2 = max(0, min(grid_y2, 14 - 1))
    
        matrix[12-grid_x2:12-grid_x1+1,grid_y1:grid_y2+1]=class_id
    
    return matrix

color_mapping = {
    0: 'red', # done, battery
    1: 'black', # board
    2: 'green', # done, buzzer
    3: 'orange',
    4: 'limegreen', #done, fm
    5: 'grey', # done (lamp; check accuracy)
    6: 'darkred', # done, led
    7: 'blue', # mc
    8: 'yellow', # done, motor
    9: 'royalblue', # done, push button
    10: 'seagreen', # done, reed
    11: 'firebrick', # done, speaker
    12: 'darkgreen', # done, switch
    13: 'purple' # done, wire
}

def show_estimated_board(results_transferred,color_mapping=color_mapping,cell_size = 50):
    """Draw the virtual image of the board

    Args:
        results_transferred (matrix): a matrix to store class of each block of the board
        rows (int, optional): number of rows of the grid. Defaults to 8.
        cols (int, optional): number of columns of the grid. Defaults to 7.
        cell_size (int, optional): size of cell. Defaults to 50.
    """
    # Row and Col
    rows, cols = len(results_transferred), len(results_transferred[0])
    
    # Calculate the total size of the image
    image_width = cols * cell_size
    image_height = rows * cell_size

    # Create a new image with a black background
    image = Image.new("RGB", (image_width, image_height), color="black")

    # Create a draw object
    draw = ImageDraw.Draw(image)

    # Draw the grid with numbers
    for row in range(rows):
        for col in range(cols):
            # Calculate the position of the top-left corner of the cell
            x1 = col * cell_size
            y1 = row * cell_size

            # Calculate the position of the bottom-right corner of the cell
            x2 = x1 + cell_size
            y2 = y1 + cell_size

            # Calculate the number for each cell (you can use any logic here)
            cell_number = results_transferred[row][col]

            # Draw the cell with the corresponding number
            if cell_number >= 0:
                draw.rectangle([x1, y1, x2, y2], fill=color_mapping[cell_number],outline='white')
            else:
                draw.rectangle([x1, y1, x2, y2], fill="black",outline='white')
            draw.text((x1 + 20, y1 + 20), str(cell_number),  fill="white")
    
    return image

def draw_virtual_board_video(source=0,show_pegs=False,print_time=False,frame_rate=5,store=False):
    cap = cv2.VideoCapture(source)
    model = YOLO('best (8).pt')
    i = 0
    prev = 0
    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    
    if store:
        # Create the output folder if it doesn't exist
        if not os.path.exists('raw_videos'):
            os.makedirs('raw_videos')
            
        # Get the list of existing files in the "cropped_frames" directory
        existing_files = os.listdir('raw_videos')
        if existing_files:
            video_count = max([int(file_name.split('_')[2].split('.')[0]) for file_name in existing_files]) + 1
        else:
            video_count = 0
        
        # Create a VideoWriter to save the cropped video
        fourcc = cv2.VideoWriter_fourcc(*'DIVX')
        output_path = os.path.join('raw_videos', f"raw_video_{video_count}.mp4")
        writer = cv2.VideoWriter(output_path, fourcc, 20.0, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
    
    
    while True:
        # Capture a frame
        ret, frame = cap.read()
        
        if not ret:
            print("Camera Connection Failed")
            break
        
        if store:
            writer.write(frame)

        # Read the video properties to get the frame width and height
        crop_x, crop_y, crop_width, crop_height = 760, 250, 450, 500
        frame_for_veri = frame[crop_y:crop_y + crop_height, crop_x:crop_x + crop_width]
        frame_for_hand = frame[crop_y:crop_y + crop_height, crop_x:crop_x + crop_width+120]
        frame = cv2.rotate(frame_for_veri, cv2.ROTATE_90_CLOCKWISE)
        
        # Detecting hand
        results = hands.process(cv2.cvtColor(frame_for_hand, cv2.COLOR_BGR2RGB))
        if results.multi_hand_landmarks:
            # If a hand is detected, skip this frame
            continue
        
        time_elapsed = time.time() - prev
        if time_elapsed > 1./frame_rate:
            prev = time.time()
        
            # Convert the raw frame to PIL Image
            #raw_frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            # Reflect the raw frame horizontally and Rotate the raw frame 90 degrees counterclockwise
            #raw_frame_pil = raw_frame_pil.transpose(Image.FLIP_LEFT_RIGHT)
            #raw_frame_pil = raw_frame_pil.rotate(90, expand=True)
            
            # Convert the frame to RGB for PIL (optional)
            # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            start_time = time.time()
            if print_time:
                print(f"Frame {i} starts")
            
            # Detect hands in the frame and Check if any hands are detected
            
            
            # Draw pegs, return a mapping between matrix and real coordinates
            matrixcoor_to_realcoor, frame_tilt, frame_circle = draws_pegs_on_rotated_board(frame)
            if print_time:
                draw_peg_time = time.time()
                print("Draw pegs uses:", draw_peg_time - start_time)

            # Use YOLO object detection to get position
            results = model.predict(frame_tilt,show=True,conf=0.3)
            if print_time:
                print("YOLO object detection uses:", time.time()-draw_peg_time)
            
            for result in results:
                boxes = result.boxes
                output = np.hstack([boxes.xyxy, boxes.cls[:, np.newaxis]])

            # Get the mapping between matrix entries and class, then draw the virtual board
            matrix = matrix_class_mapping(output, matrixcoor_to_realcoor)
            final_image = show_estimated_board(matrix)

            # Convert the image back to BGR format for displaying with OpenCV
            final_image_bgr = cv2.cvtColor(np.array(final_image), cv2.COLOR_RGB2BGR)
            #raw_frame_pil = cv2.cvtColor(np.array(raw_frame_pil), cv2.COLOR_RGB2BGR)

            # Display the raw board and virtual board outputs in separate windows
            # cv2.imshow("Raw Board", np.array(raw_frame_pil))
            cv2.imshow("Virtual Board", final_image_bgr)
            if show_pegs:
                cv2.imshow("Board with Pegs",frame_circle)
            
            if print_time:
                end_time = time.time()
                time_elapsed = end_time - start_time
                print("Frame {i} ends, using:", time_elapsed)
            i += 1
            # Wait for the specified interval time
            #time.sleep(interval_seconds)

        # Check for the 'q' key press to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close the windows
    cap.release()
    if store:
        writer.release() 
    cv2.destroyAllWindows()

# Assuming you have the matrix results_transferred ready
# draw_virtual_board_video(source='raw_videos/raw_video_5.mp4', show_pegs=True)

# draw_virtual_board_video(source=0,show_pegs=True,store=True)