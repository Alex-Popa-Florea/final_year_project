import numpy as np
from PIL import Image, ImageDraw, ImageFont
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

def get_edges(image):
    # Convert the image to a NumPy array
    image_array = np.array(image)

    # Get the indices of non-zero elements (edge points)
    non_zero_indices = np.nonzero(image_array)

    # Get the minimum and maximum row and column indices of non-zero elements
    minRow, minColumn = np.min(non_zero_indices, axis=1)
    maxRow, maxColumn = np.max(non_zero_indices, axis=1)

    return (minRow, maxRow, minColumn, maxColumn)

def get_board_mask(img):
    color = [0, 0, 0, 255, 255, 50]
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    cv2.imshow("test1", img)
    cv2.imshow("test2", imgHSV)
    lower = np.array(color[:3])  
    upper = np.array(color[3:]) 
    mask = cv2.inRange(imgHSV, lower, upper)
    return mask

def get_pegs(img, min_row, max_row, min_col, max_col):

    matrixcoor_to_realcoor = {}
    row_length = max_row - min_row
    col_length = max_col - min_col

    if row_length > col_length:
        row_sq_count = 8
        col_sq_count = 7
    else:
        row_sq_count = 7
        col_sq_count = 8

    square_size_rows = row_length / row_sq_count
    square_size_cols = col_length / col_sq_count
    
    for row in range(row_sq_count):
        for col in range(col_sq_count):
            matrixcoor_to_realcoor[row, col] = np.array([min_col + int(square_size_cols * col + square_size_cols / 2), min_row + int(square_size_rows * row + square_size_rows / 2)])
    print(matrixcoor_to_realcoor)
    
    img_circle = img.copy()
    for key in matrixcoor_to_realcoor:
        cv2.circle(img_circle, matrixcoor_to_realcoor[key], 2, (200, 200, 200), -1)

    return img_circle, matrixcoor_to_realcoor, (square_size_rows, square_size_cols), (row_sq_count, col_sq_count)

def draws_pegs_on_rotated_board(image, draw_edge=True):
    boardBW = get_board_mask(image)
    angle = whatAngle(boardBW)
 
    boardBW_tilt = tilt(boardBW, angle) 
    image_tilt = tilt(image, angle) 
 
    min_row, max_row, min_col, max_col = get_edges(boardBW_tilt)

    img_circle, matrixcoor_to_realcoor, square_size, board_size = get_pegs(image_tilt, min_row, max_row, min_col, max_col)

    if draw_edge:
        cv2.rectangle(img_circle, (min_col, min_row), (max_col, max_row), (0, 255, 0), 3)
  
    return matrixcoor_to_realcoor, square_size, image_tilt, img_circle, angle, board_size

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
    13: 'purple', # done, wire
    14: 'white' # done, connection
}

def show_estimated_board(results_transferred, color_mapping=color_mapping, cell_size = 50):
    """Draw the virtual image of the board

    Args:
        results_transferred (matrix): a matrix to store class of each block of the board
        rows (int, optional): number of rows of the grid. Defaults to 8.
        cols (int, optional): number of columns of the grid. Defaults to 7.
        cell_size (int, optional): size of cell. Defaults to 50.
    """
    # Row and Col
    for row, col in results_transferred:
        rows = row
        cols = col
    rows += 1
    cols += 1

    # Calculate the total size of the image
    image_width = cols * cell_size
    image_height = rows * cell_size

    # Create a new image with a black background
    image = Image.new("RGB", (image_width, image_height), color="black")

    # Create a draw object
    draw = ImageDraw.Draw(image)

    # Draw the grid with numbers
    for row, col in results_transferred:
        # Calculate the position of the top-left corner of the cell
        x1 = col * cell_size
        y1 = row * cell_size

        # Calculate the position of the bottom-right corner of the cell
        x2 = x1 + cell_size
        y2 = y1 + cell_size

        # Calculate the number for each cell (you can use any logic here)
        if len(results_transferred[row, col]) == 1:
            _, _, _, _, cell_number = results_transferred[row, col][0]

            # Draw the cell with the corresponding number
            draw.rectangle([x1, y1, x2, y2], fill=color_mapping[cell_number],outline='white')
        elif len(results_transferred[row, col]) > 1:

            # Draw the cell with the corresponding number
            cell_number = 14
            draw.rectangle([x1, y1, x2, y2], fill=color_mapping[cell_number],outline='white')
        else:
            cell_number = -1
            draw.rectangle([x1, y1, x2, y2], fill="black",outline='white')

        draw.text((x1 + 20, y1 + 20), str(cell_number),  fill="white")
    
    return image