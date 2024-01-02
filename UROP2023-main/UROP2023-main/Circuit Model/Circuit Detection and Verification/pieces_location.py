import numpy as np

class_id_mapping = {
        0: 'battery', 
        1: 'board', 
        2: 'buzzer', 
        3: 'cds', 
        4: 'fm', 
        5: 'lamp', 
        6: 'led', 
        7: 'mc', 
        8: 'motor', 
        9: 'push button', 
        10: 'reed', 
        11: 'speaker', 
        12: 'switch', 
        13: 'wire'
}

class_id_mapping_reverse = {
    'battery': 0,
    'board': 1,
    'buzzer': 2,
    'cds': 3,
    'fm': 4,
    'lamp': 5,
    'led': 6,
    'mc': 7,
    'motor': 8,
    'push button': 9,
    'reed': 10,
    'speaker': 11,
    'switch': 12,
    'wire': 13
}


def round_to_integer_with_error(float_number, error_rate = 0.1, down = True):
    """
    Round a floating-point number to the nearest integer with optional error rate adjustments.
    We used this because bounding boxes of pieces drawn by YOLO might not be very tight to the pieces.

    Args:
        float_number (float): The input floating-point number to be rounded.
        error_rate (float, optional): The custom error rate used for fine-tuning the rounding.
            Default is 0.1 (equivalent to 10%).
        down (bool, optional): If True, round down to the nearest integer; if False, round up.
            Default is True.

    Returns:
        int: The rounded integer value.
    """
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

def correct_size_from_data(d):
    """
    Correct the size of a piece, such as a wire, to ensure accurate representation, 
    especially when overlapping with other pieces.

    Args:
        d (dict): The data with piece location information (already converted to coordinates on board)
    """
    if d['type'] in ['wire', 'switch', 'lamp', 'push button', 'reed', 'led', 'motor']:
            # forced to cover odd coordinates on board (as it is the  point between pegs)
            if d['x1'] == d['x2']:
                if d['y1'] % 2 != 0:
                    d['y1'] -= 1
                if d['y2'] % 2 != 0:
                    d['y2'] += 1
            else:
                if d['x1'] % 2 != 0:
                    d['x1'] -= 1
                if d['x2'] % 2 != 0:
                    d['x2'] += 1
    
    # due to the size of buzzer, it may occupy 2-3 rows/columns (while it should be occupy only 1 row/column)
    if d['type'] == 'buzzer': 
        if abs(d['x1']-d['x2']) < abs(d['y1']-d['y2']): # horizontal
            d['x1'] = d['x2'] = [i for i in range(d['x1'],d['x2']) if i%2 == 0][0]
        else: # vertical
            d['y1'] = d['y2'] = [i for i in range(d['y1'],d['y2']) if i%2 == 0][0]
            
    return d

def pieceOnEachLocation(results, matrixcoor_to_realcoor): 
    """
    Identify and map pieces to their respective grid locations in a matrix based on detected object results.

    Args:
        results (list): A list of detected object results, typically containing bounding box coordinates and class IDs.
        matrixcoor_to_realcoor (dict): A dictionary mapping matrix coordinates to real coordinates on frame.

    Returns:
        tuple: A tuple containing two elements:
            - numpy.ndarray: A matrix where each cell corresponds to a grid location and contains the class ID of the detected piece.
            - list: A list of dictionaries, each representing a detected piece with keys 'type', 'x1', 'x2', 'y1', and 'y2'.

    Note:
        This function is designed to map detected objects, typically pieces on a board, to their respective grid locations.
        It accounts for object bounding box coordinates, class IDs, and grid transformations.
    """
    x0,y0 = matrixcoor_to_realcoor[(0,14)]
    x_max, y_max = matrixcoor_to_realcoor[(12,0)]
    if x_max-x0<y_max-y0:
        num_row, num_col = 12,14
    else:
        num_row, num_col = 14,12
    matrix = np.zeros((num_row+1, num_col+1))-1
    
    x_len, y_len = np.abs(matrixcoor_to_realcoor[(0,0)]-matrixcoor_to_realcoor[(12,14)])
    data = []

    for r in results:
        x1,y1,x2,y2,class_id = r
        if class_id != 1:
            grid_x1 = round_to_integer_with_error(((x1-x0) / x_len) * num_row, down=False)
            grid_y1 = round_to_integer_with_error(((y1-y0) / y_len) * num_col, down=False)
            grid_x2 = round_to_integer_with_error(((x2-x0) / x_len) * num_row)
            # if class_id != 13:
            #     grid_y2 = max(round_to_integer_with_error(((y2-y0) / y_len) * num_col),int(((y2-y0) / y_len) * num_col)) if int(((y2-y0) / y_len) * num_col) % 2 != 0 else round_to_integer_with_error(((y2-y0) / y_len) * num_col)
            # else: 
            #     grid_y2 = round(((y2-y0) / y_len) * num_col) if ((y2-y0) / y_len) * num_col % 2 != 0 else round_to_integer_with_error(((y2-y0) / y_len) * num_col)
            grid_y2 = max(round_to_integer_with_error(((y2-y0) / y_len) * num_col),int(((y2-y0) / y_len) * num_col)) if int(((y2-y0) / y_len) * num_col) % 2 != 0 else round_to_integer_with_error(((y2-y0) / y_len) * num_col)    
            
            
            grid_x2 = max(grid_x1,grid_x2)
            grid_y2 = max(grid_y1,grid_y2)

            grid_x1 = max(0, min(grid_x1, num_row))
            grid_y1 = max(0, min(grid_y1, num_col))
            grid_x2 = max(0, min(grid_x2, num_row))
            grid_y2 = max(0, min(grid_y2, num_col))
            
            
            r_data = {}
            r_data['type'] = class_id_mapping[class_id]
            r_data['x1'], r_data['x2'], r_data['y1'],r_data['y2'] = num_row-grid_x2,num_row-grid_x1,grid_y1,grid_y2
            correct_size_from_data(r_data)
            data.append(r_data)
            
            matrix[r_data['x1']:r_data['x2']+1,r_data['y1']:r_data['y2']+1] = class_id


    return matrix, data
