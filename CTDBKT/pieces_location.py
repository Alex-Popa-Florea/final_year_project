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
        9: 'button_switch', 
        10: 'reed_switch', 
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
    'button_switch': 9,
    'reed_switch': 10,
    'speaker': 11,
    'switch': 12,
    'wire': 13
}

class_size_map = {
    'battery': (2, 3),
    'board': (7, 8),
    'buzzer': (1, 3),
    'cds': (1, 3),
    'fm': (2, 3),
    'lamp': (1, 3),
    'led': (1, 3),
    'mc': (2, 3),
    'motor': (1, 3),
    'button_switch': (1, 3),
    'reed_switch': (1, 3),
    'speaker': (1, 3),
    'switch': (1, 3),
    'wire': (1, 2)
}

def get_direction(piece):
    px1, py1, px2, py2, _ = piece
    left_piece = min(px1, px2)
    right_piece = max(px1, px2)
    top_piece = min(py1, py2)
    bottom_piece = max(py1, py2)

    print(left_piece)
    print(right_piece)
    print(top_piece)
    print(bottom_piece)

    if (right_piece - left_piece) > (bottom_piece - top_piece):
        direct = "left_right"
    else:
        direct = "up_down"
    
    return direct

def is_in_peg(peg_center, peg_size, piece):
    row_size, col_size = peg_size

    px1, py1, px2, py2, _ = piece
    
    gx, gy = peg_center
    gx1, gy1, gx2, gy2 = gx - col_size / 2, gy - row_size / 2, gx + col_size / 2, gy + row_size / 2,

    left_piece = min(px1, px2)
    right_piece = max(px1, px2)
    top_piece = min(py1, py2)
    bottom_piece = max(py1, py2)

    left_peg = min(gx1, gx2)
    right_peg = max(gx1, gx2)
    top_peg = min(gy1, gy2)
    bottom_peg = max(gy1, gy2)

    left_overlap = max(left_piece, left_peg)
    right_overlap = min(right_piece, right_peg)
    top_overlap = max(top_piece, top_peg)
    bottom_overlap = min(bottom_piece, bottom_peg)

    if right_overlap > left_overlap and bottom_overlap > top_overlap:
        # Calculate the area of the overlapping rectangle
        overlap_width = right_overlap - left_overlap
        overlap_height = bottom_overlap - top_overlap
        return (overlap_width * overlap_height) / (row_size * col_size)
    else:
        return -1

def fix_side(side_name, pegs_along_side, first_peg, last_peg, correct_pegs, old_peg_overlap):
    new_peg_overlap = old_peg_overlap.copy()
    pegs_removed = {}
    
    first_peg_overlap = 0
    first_peg_count = 0
    
    last_peg_overlap = 0
    last_peg_count = 0

    while pegs_along_side != correct_pegs:
        for peg_row, peg_col in old_peg_overlap:
            if side_name == "row":
                if peg_row == first_peg:
                    first_peg_overlap += old_peg_overlap[peg_row, peg_col]
                    first_peg_count += 1
                if peg_row == last_peg:
                    last_peg_overlap += old_peg_overlap[peg_row, peg_col]
                    last_peg_count += 1
            elif side_name == "col":
                if peg_col == first_peg:
                    first_peg_overlap += old_peg_overlap[peg_row, peg_col]
                    first_peg_count += 1
                if peg_col == last_peg:
                    last_peg_overlap += old_peg_overlap[peg_row, peg_col]
                    last_peg_count += 1
        
        if last_peg_overlap / last_peg_count > first_peg_overlap / first_peg_count:
            for peg_row, peg_col in old_peg_overlap:
                if side_name == "row":
                    if peg_row == first_peg:
                        pegs_removed[peg_row, peg_col] = new_peg_overlap[peg_row, peg_col]
                        new_peg_overlap.pop((peg_row, peg_col))
                elif side_name == "col":
                    if peg_col == first_peg:
                        pegs_removed[peg_row, peg_col] = new_peg_overlap[peg_row, peg_col]
                        new_peg_overlap.pop((peg_row, peg_col))
            first_peg += 1
        else:
            for peg_row, peg_col in old_peg_overlap:
                if side_name == "row":
                    if peg_row == last_peg:
                        pegs_removed[peg_row, peg_col] = new_peg_overlap[peg_row, peg_col]
                        new_peg_overlap.pop((peg_row, peg_col))
                elif side_name == "col":
                    if peg_col == last_peg:
                        pegs_removed[peg_row, peg_col] = new_peg_overlap[peg_row, peg_col]
                        new_peg_overlap.pop((peg_row, peg_col))
            last_peg -= 1
        pegs_along_side -= 1
        old_peg_overlap = new_peg_overlap.copy()
    return new_peg_overlap, pegs_removed

def adjust_size(data_item, direct):

    old_peg_overlap = data_item["pegs_kept"]
    new_data_item = data_item.copy()

    smallest_row = 100
    smallest_col = 100
    largest_row = 0
    largest_col = 0

    for row, col in old_peg_overlap:
        if smallest_row > row:
            smallest_row = row
        if smallest_col > col:
            smallest_col = col
        if largest_row < row:
            largest_row = row
        if largest_col < col:
            largest_col = col

    first_row, first_col = smallest_row, smallest_col
    last_row, last_col = largest_row, largest_col
    rows = last_row - first_row + 1
    cols = last_col - first_col + 1


    if direct == "left_right":
        correct_rows, correct_cols = class_size_map[data_item["type"]]
    else:
        correct_cols, correct_rows = class_size_map[data_item["type"]]

    if rows == correct_rows and cols == correct_cols:
        return True, new_data_item
    if data_item["type"] == "wire" and direct == "left_right":
        if rows == correct_rows:
            return True, new_data_item
    elif data_item["type"] == "wire" and direct == "up_down":
        if cols == correct_cols:
            return True, new_data_item

    if rows != correct_rows and cols != correct_cols:
        return False, new_data_item

    if rows < correct_rows or cols < correct_cols:
        return False, new_data_item

    total_pegs_removed = {}
    new_peg_overlap = old_peg_overlap
    if data_item["type"] == "wire" and direct == "left_right":
        new_peg_overlap, pegs_removed = fix_side("row", rows, first_row, last_row, correct_rows, new_peg_overlap)
        for peg in pegs_removed:
            total_pegs_removed[peg] = pegs_removed[peg]
    if data_item["type"] == "wire" and direct == "up_down":
        new_peg_overlap, pegs_removed = fix_side("col", cols, first_col, last_col, correct_cols, new_peg_overlap)
        for peg in pegs_removed:
            total_pegs_removed[peg] = pegs_removed[peg]
    else:
        new_peg_overlap, pegs_removed = fix_side("row", rows, first_row, last_row, correct_rows, new_peg_overlap)
        for peg in pegs_removed:
            total_pegs_removed[peg] = pegs_removed[peg]
        new_peg_overlap, pegs_removed = fix_side("col", cols, first_col, last_col, correct_cols, new_peg_overlap)
        for peg in pegs_removed:
            total_pegs_removed[peg] = pegs_removed[peg]
    
    
    new_data_item["pegs_kept"] = new_peg_overlap
    new_data_item["pegs_removed"] = total_pegs_removed

    return True, new_data_item

    

        
    


def piece_on_each_location(results, matrixcoor_to_realcoor, peg_size): 
    matrix = {}
    data = []
    for peg in matrixcoor_to_realcoor:
        matrix[peg] = []

    for piece in results:
        _, _, _, _, class_id = piece
        if class_id != 1:
            direct = get_direction(piece)

            data_item = {"type": class_id_mapping[class_id], "direct": direct, "pegs_kept": {}, "pegs_removed": {}}
            
            smallest_row = 100
            smallest_col = 100
            largest_row = 0
            largest_col = 0

            for peg in matrixcoor_to_realcoor:
                row, col = peg
                peg_center = matrixcoor_to_realcoor[peg]

                overlap = is_in_peg(peg_center, peg_size, piece)

                if overlap != -1:
                    if smallest_row > row:
                        smallest_row = row
                    if smallest_col > col:
                        smallest_col = col
                    if largest_row < row:
                        largest_row = row
                    if largest_col < col:
                        largest_col = col
                    data_item["pegs_kept"][peg] = overlap
            
            print(data_item)

            for row in range(smallest_row, largest_row + 1):
                for col in range(smallest_col, largest_col + 1):
                    if not (row, col) in data_item["pegs_kept"]:
                        data_item["pegs_kept"][row, col] = 0
            print(data_item)
            correct_size, new_data_item = adjust_size(data_item, direct)
            print(new_data_item)
            if correct_size:
                data.append(new_data_item)
                for peg in new_data_item["pegs_kept"]:
                    matrix[peg].append(piece)
            
    print("YAAAAAY")
    print(data)
    return matrix, data