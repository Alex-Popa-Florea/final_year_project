import numpy as np
import tasks
from enum import Enum

class StudType(Enum):
    NONE = 0
    POSITIVE = 1
    NEGATIVE = -1
    ANY = 2
    IN = 3
    OUT = 4
    TRIGGER = 5
    REPEAT = 6
    RESTART = 7
    SIGNAL = 8

class HistoryElement():
    def __init__(self, elem_type, move, contr_percentage, time) -> None:
        self.elem_type = elem_type
        self.move = move
        self.contr_percentage = contr_percentage
        self.time = time
    
    def __str__(self):
        return f"{self.elem_type} {self.move} {self.contr_percentage} {self.time}"

class PieceHistoryElement(HistoryElement):
    def __init__(self, piece_id, piece_type, move, contr_percentage, time) -> None:
        self.piece_id = piece_id
        self.piece_type = piece_type
        super().__init__(elem_type="piece", move=move, contr_percentage=contr_percentage, time=time)

    def __str__(self):
        return f"{self.piece_id} {self.piece_type} {self.elem_type} {self.move} {self.contr_percentage} {self.time}"

class StudDirectionHistoryElement(HistoryElement):
    def __init__(self, piece_id, piece_type, stud_type, move, contr_percentage, time) -> None:
        self.piece_id = piece_id
        self.piece_type = piece_type
        self.stud_type = stud_type
        super().__init__(elem_type="stud_direction", move=move, contr_percentage=contr_percentage, time=time)

    def __str__(self):
        return f"{self.piece_id} {self.piece_type} {self.stud_type} {self.elem_type} {self.move} {self.contr_percentage} {self.time}"

class History():
    def __init__(self, uids) -> None:
        self.uids = uids
        self.obs_history = {}

        for uid in self.uids:
            self.obs_history[uid] = []

    def __str__(self):
        string = ""
        for uid in self.uids:
            string += f"{str(uid)}: "
            for elem in self.obs_history[uid]:

                string += f"{str(elem)}, \n"
            string += "\n"
        return string

    def add_elem(self, uid, elem_type, move, contr_percentage, time):
        self.obs_history[uid].append(HistoryElement(elem_type, move, contr_percentage, time))

    def add_piece_elem(self, uid, piece_id, piece_type, move, contr_percentage, time):
        self.obs_history[uid].append(PieceHistoryElement(piece_id, piece_type, move, contr_percentage, time))

    def add_stud_direction_elem(self, uid, piece_id, piece_type, stud_type, move, contr_percentage, time):
        self.obs_history[uid].append(StudDirectionHistoryElement(piece_id, piece_type, stud_type, move, contr_percentage, time))

class Board:
    def __init__(self, direction):
        if direction == 0:
            self.rows = 7
            self.cols = 8
        else:
            self.rows = 8
            self.cols = 7
        
        self.pegs = []
        for i in range(self.rows):
            self.pegs.append([])
            for _ in range(self.cols):
                self.pegs[i].append({})
        
        self.pieces = {}
        self.history = History([0, 1])

    def __str__(self):
        string = ""
        for i in self.pegs:
            for j in i:
                string += str(j)
                string += " "
            string += "\n"
        return string

    def find_piece(self, piece_type):
        for piece in self.pieces:
            if self.pieces[piece].type == piece_type:
                return True
        return False

    def swap_pieces(self, pieces, time, contr={}):
        changes = False
        found_pieces = {}
        for old_piece_id in self.pieces:
            found_pieces[old_piece_id] = False
        
        for new_piece in pieces:
            found = False
            for old_piece_id in found_pieces:
                old_piece = self.pieces[old_piece_id]
                if new_piece.type == old_piece.type and new_piece.position == old_piece.position and new_piece.direction == old_piece.direction:
                    found_pieces[old_piece_id] = True
                    found = True
            if not found:
                changes = True
                self.add_piece(new_piece, time, contr)
        
        for old_piece_id in found_pieces:
            if not found_pieces[old_piece_id]:
                changes = True
                self.remove_piece(old_piece_id, time, contr)
        return changes

    def fits_in_board(self, piece):
        for row_index, col in enumerate(piece.stud_matrix):
            for col_index, value in enumerate(col):
                if piece.position[0] + row_index >= self.rows or  piece.position[0] + row_index < 0:
                    return False
                if piece.position[1] + col_index >= self.cols or piece.position[1] + col_index < 0:
                    return False
        return True

    def add_piece(self, piece, time, contr={}):
        if not self.fits_in_board(piece=piece):
            return 0
        self.pieces[piece.name] = piece
        connection_formed = False
        for row_index, col in enumerate(piece.stud_matrix):
            for col_index, value in enumerate(col):
                if value != StudType.NONE.value:
                    for other_piece_id in self.pegs[piece.position[0] + row_index][piece.position[1] + col_index]:
                        if other_piece_id != piece.name:
                            if self.pegs[piece.position[0] + row_index][piece.position[1] + col_index][other_piece_id] != StudType.NONE.value:
                                connection_formed = True
                self.pegs[piece.position[0] + row_index][piece.position[1] + col_index][piece.name] = value
        
        flow_found, num_flows, correct_studs = self.find_flow()
        
        for uid in contr:
            self.history.add_piece_elem(uid, piece.name, piece.type, "added", contr[uid], time)
            if connection_formed:
                self.history.add_elem(uid, "connection", "added", contr[uid], time)
            if flow_found:
                self.history.add_elem(uid, "closed", "added", contr[uid], time)
                for stud in correct_studs:
                    self.history.add_stud_direction_elem(uid, stud[0], stud[1], stud[2], "added", contr[uid], time)
                if num_flows == 1:
                    self.history.add_elem(uid, "series", "added", contr[uid], time)
                if num_flows > 1:
                    self.history.add_elem(uid, "parallel", "added", contr[uid], time)
        return connection_formed
        
    def remove_piece(self, piece_id, time, contr={}):
        piece = self.pieces[piece_id]
        _, connection_count = self.get_connections(piece_id)
        for row_index, col in enumerate(piece.stud_matrix):
            for col_index, _ in enumerate(col):
                self.pegs[piece.position[0] + row_index][piece.position[1] + col_index].pop(piece_id)
        self.pieces.pop(piece_id)

        for uid in contr:
            self.history.add_piece_elem(uid, piece.name, piece.type, "removed", contr[uid], time)
            if connection_count > 0:
                self.history.add_elem(uid, "connection", "removed", contr[uid], time)
        return connection_count > 0

    def get_connections(self, piece_id):

        connections = {}
        connection_count = 0

        piece = self.pieces[piece_id]
        for row_index, col in enumerate(piece.stud_matrix):
            for col_index, value in enumerate(col):
                if value != StudType.NONE.value:
                    connections[(piece.position[0] + row_index, piece.position[1] + col_index)] = (value, [])

                    for other_piece_id in self.pegs[piece.position[0] + row_index][piece.position[1] + col_index]:
                        if other_piece_id != piece.name:
                            other_value = self.pegs[piece.position[0] + row_index][piece.position[1] + col_index][other_piece_id]
                            if other_value != StudType.NONE.value:
                                connections[(piece.position[0] + row_index, piece.position[1] + col_index)][1].append((other_piece_id, other_value))
                                connection_count += 1
        return connections, connection_count

    def find_flow(self):
        overall_flow_found = False
        overall_num_flows = 0
        all_correct_studs = []
        for piece_id in self.pieces:
            if self.pieces[piece_id].type == "battery":
                battery_conns, _ = self.get_connections(piece_id)
                piece_list = []
                for con in battery_conns:
                    if battery_conns[con][0] == StudType.POSITIVE.value:
                        for (other_piece_id, con_value) in battery_conns[con][1]:
                            flow_found, num_flows, path, correct_studs = self.flow_step(other_piece_id, con_value, [piece_id])
                            if flow_found:
                                overall_num_flows += num_flows
                                overall_flow_found = True
                                piece_list.append(path)
                                for correct_stud in correct_studs:
                                    all_correct_studs.append(correct_stud)

        return overall_flow_found, overall_num_flows, all_correct_studs

    def flow_step(self, piece_id, con_value, visited):
        found_closed = False
        all_correct_studs = []

        piece = self.pieces[piece_id]
        if piece.type == "battery" and con_value == StudType.NEGATIVE.value:
            return True, 1, {piece_id: "Complete!"}, []
        if piece_id in visited:
            return False, 0, None, []
        
        if piece.type == "led" and con_value == StudType.NEGATIVE.value:
            return False, 0, None, []
        elif piece.type == "led" and con_value == StudType.POSITIVE.value:
            all_correct_studs.append((piece_id, "led", StudType.POSITIVE))

        if piece.type == "fm" and con_value == StudType.OUT.value:
            return False, 0, None, []
        elif piece.type == "fm" and con_value == StudType.IN.value:
            all_correct_studs.append((piece_id, "fm", StudType.IN))
        elif piece.type == "fm" and con_value == StudType.SIGNAL.value:
            all_correct_studs.append((piece_id, "fm", StudType.SIGNAL))

        if piece.type == "mc" and con_value == StudType.OUT.value:
            return False, 0, None, []
        elif piece.type == "mc" and con_value == StudType.IN.value:
            all_correct_studs.append((piece_id, "mc", StudType.IN))
        elif piece.type == "mc" and con_value == StudType.TRIGGER.value:
            all_correct_studs.append((piece_id, "mc", StudType.TRIGGER))
        elif piece.type == "mc" and con_value == StudType.REPEAT.value:
            all_correct_studs.append((piece_id, "mc", StudType.REPEAT))
        elif piece.type == "mc" and con_value == StudType.RESTART.value:
            all_correct_studs.append((piece_id, "mc", StudType.RESTART))

        new_visited = []
        for item in visited:
            new_visited.append(item)
        new_visited.append(piece_id)
        piece_list = []

        cons, _ = self.get_connections(piece_id)

        
        total_closed = 0
        for index in cons: 
            current_correct_studs = []
            if piece.type == "led" and cons[index][0] == StudType.POSITIVE.value:
                continue
            elif piece.type == "led" and  cons[index][0] == StudType.NEGATIVE.value:
                current_correct_studs.append((piece_id, "led", StudType.NEGATIVE))

            if piece.type == "fm" and cons[index][0] == StudType.IN.value:
                continue
            elif piece.type == "fm" and cons[index][0] == StudType.OUT.value:
                current_correct_studs.append((piece_id, "fm", StudType.OUT))
            elif piece.type == "fm" and cons[index][0] == StudType.SIGNAL.value:
                current_correct_studs.append((piece_id, "fm", StudType.SIGNAL))

            if piece.type == "mc" and cons[index][0] == StudType.IN.value:
                return False, 0, None, []
            elif piece.type == "mc" and cons[index][0] == StudType.OUT.value:
                current_correct_studs.append((piece_id, "mc", StudType.OUT))
            elif piece.type == "mc" and cons[index][0] == StudType.TRIGGER.value:
                current_correct_studs.append((piece_id, "mc", StudType.TRIGGER))
            elif piece.type == "mc" and cons[index][0] == StudType.REPEAT.value:
                current_correct_studs.append((piece_id, "mc", StudType.REPEAT))
            elif piece.type == "mc" and cons[index][0] == StudType.RESTART.value:
                current_correct_studs.append((piece_id, "mc", StudType.RESTART))
            
            for (other_piece_id, other_con_value) in cons[index][1]:
                closed, num_closed, path, correct_studs = self.flow_step(other_piece_id, other_con_value, new_visited)
                total_closed += num_closed
                if closed:
                    for current_correct_stud in current_correct_studs:
                        all_correct_studs.append(current_correct_stud)
                    for correct_stud in correct_studs:
                        all_correct_studs.append(correct_stud)
                    found_closed = True
                    piece_list.append(path)
        
        return found_closed, total_closed, {piece_id: piece_list}, all_correct_studs

class Piece:
    def __init__(self, name, type, stud_matrix, position, direction, is_special = False):
        self.name = name
        self.type = type
        self.stud_matrix = stud_matrix
        self.position = position
        self.direction = direction
        self.is_special = is_special

    def __str__(self):
        return f"{self.name} {self.type} \n{self.stud_matrix} \n {self.position} {self.direction}"

class ThreeLengthUnpoledPiece(Piece):
    def __init__(self, name, type, position, direction): 
        if direction == 0:
            stud_matrix = np.zeros([1, 3])
            stud_matrix[0, 0] = StudType.ANY.value
            stud_matrix[0, 2] = StudType.ANY.value
        elif direction == 90:
            stud_matrix = np.zeros([3, 1])
            stud_matrix[0, 0] = StudType.ANY.value
            stud_matrix[2, 0] = StudType.ANY.value
        super().__init__(name=name, type=type, stud_matrix=stud_matrix, position=position, direction=direction, is_special=False)

class Battery(Piece):
    b_id = 1
    def __init__(self, name, position, direction): 
        if direction == 0:
            stud_matrix = np.zeros([3, 2])
            stud_matrix[0, 0] = StudType.POSITIVE.value
            stud_matrix[2, 0] = StudType.NEGATIVE.value
        elif direction == 90:
            stud_matrix = np.zeros([2, 3])
            stud_matrix[0, 2] = StudType.POSITIVE.value
            stud_matrix[0, 0] = StudType.NEGATIVE.value
        elif direction == 180:
            stud_matrix = np.zeros([3, 2])
            stud_matrix[2, 1] = StudType.POSITIVE.value
            stud_matrix[0, 1] = StudType.NEGATIVE.value
        elif direction == 240:
            stud_matrix = np.zeros([2, 3])
            stud_matrix[1, 0] = StudType.POSITIVE.value
            stud_matrix[1, 2] = StudType.NEGATIVE.value
        
        super().__init__(name=name, type="battery", stud_matrix=stud_matrix, position=position, direction=direction, is_special=True)

        self.power = True

class Wire(Piece):
    w_id = 1
    def __init__(self, name, position, direction, size): 
        if direction == 0:
            stud_matrix = np.zeros([1, size])
            for j in range(size):
                stud_matrix[0, j] = StudType.ANY.value
        elif direction == 90:
            stud_matrix = np.zeros([size, 1])
            for i in range(size):
                stud_matrix[i, 0] = StudType.ANY.value
        
        super().__init__(name=name, type="wire", stud_matrix=stud_matrix, position=position, direction=direction, is_special=False)

class FM(Piece):
    fm_id = 1
    def __init__(self, name, position, direction): 
        if direction == 0:
            stud_matrix = np.zeros([2, 3])
            stud_matrix[0, 0] = StudType.IN.value
            stud_matrix[0, 1] = StudType.SIGNAL.value
            stud_matrix[0, 2] = StudType.OUT.value
        elif direction == 90:
            stud_matrix = np.zeros([3, 2])
            stud_matrix[0, 1] = StudType.IN.value
            stud_matrix[1, 1] = StudType.SIGNAL.value
            stud_matrix[2, 1] = StudType.OUT.value
        elif direction == 180:
            stud_matrix = np.zeros([2, 3])
            stud_matrix[1, 2] = StudType.OUT.value
            stud_matrix[1, 1] = StudType.SIGNAL.value
            stud_matrix[1, 0] = StudType.IN.value
        elif direction == 240:
            stud_matrix = np.zeros([3, 2])
            stud_matrix[2, 0] = StudType.OUT.value
            stud_matrix[1, 0] = StudType.SIGNAL.value
            stud_matrix[0, 0] = StudType.IN.value
        super().__init__(name=name, type="fm", stud_matrix=stud_matrix, position=position, direction=direction, is_special=True)

class Buzzer(ThreeLengthUnpoledPiece):
    buz_id = 1
    def __init__(self, name, position, direction): 
        super().__init__(name=name, type="buzzer", position=position, direction=direction)

class TouchPlate(ThreeLengthUnpoledPiece):
    t_id = 1
    def __init__(self, name, position, direction): 
        super().__init__(name=name, type="touch_plate", position=position, direction=direction)

class ReedSwitch(ThreeLengthUnpoledPiece):
    rsw_id = 1
    def __init__(self, name, position, direction): 
        super().__init__(name=name, type="reed_switch", position=position, direction=direction)

class ButtonSwitch(ThreeLengthUnpoledPiece):
    bsw_id = 1
    def __init__(self, name, position, direction): 
        super().__init__(name=name, type="button_switch)", position=position, direction=direction)

class Switch(ThreeLengthUnpoledPiece):
    sw_id = 1
    def __init__(self, name, position, direction): 
        super().__init__(name=name, type="switch", position=position, direction=direction)

class Cds(ThreeLengthUnpoledPiece):
    c_id = 1
    def __init__(self, name, position, direction): 
        super().__init__(name=name, type="cds", position=position, direction=direction)

class Led(Piece):
    led_id = 1
    def __init__(self, name, position, direction): 
        if direction == 0:
            stud_matrix = np.zeros([1, 3])
            stud_matrix[0, 0] = StudType.POSITIVE.value
            stud_matrix[0, 2] = StudType.NEGATIVE.value
        elif direction == 90:
            stud_matrix = np.zeros([3, 1])
            stud_matrix[2, 0] = StudType.POSITIVE.value
            stud_matrix[0, 0] = StudType.NEGATIVE.value
        elif direction == 180:
            stud_matrix = np.zeros([1, 3])
            stud_matrix[0, 2] = StudType.POSITIVE.value
            stud_matrix[0, 0] = StudType.NEGATIVE.value
        elif direction == 240:
            stud_matrix = np.zeros([3, 1])
            stud_matrix[0, 0] = StudType.POSITIVE.value
            stud_matrix[2, 0] = StudType.NEGATIVE.value

        super().__init__(name=name, type="led", stud_matrix=stud_matrix, position=position, direction=direction, is_special=True)

class Lamp(ThreeLengthUnpoledPiece):
    la_id = 1
    def __init__(self, name, position, direction): 
        super().__init__(name=name, type="lamp", position=position, direction=direction)

class Speaker(ThreeLengthUnpoledPiece):
    sp_id = 1
    def __init__(self, name, position, direction): 
        super().__init__(name=name, type="speaker", position=position, direction=direction)

class MC(Piece):
    mc_id = 1
    def __init__(self, name, position, direction): 
        if direction == 0:
            stud_matrix = np.zeros([2, 3])
            stud_matrix[1, 0] = StudType.OUT.value
            stud_matrix[1, 2] = StudType.IN.value

            stud_matrix[0, 0] = StudType.RESTART.value
            stud_matrix[0, 1] = StudType.TRIGGER.value
            stud_matrix[0, 2] = StudType.REPEAT.value
        elif direction == 90:
            stud_matrix = np.zeros([3, 2])
            stud_matrix[2, 0] = StudType.IN.value
            stud_matrix[0, 0] = StudType.OUT.value

            stud_matrix[0, 1] = StudType.RESTART.value
            stud_matrix[1, 1] = StudType.TRIGGER.value
            stud_matrix[2, 1] = StudType.REPEAT.value
        elif direction == 180:
            stud_matrix = np.zeros([2, 3])
            stud_matrix[0, 2] = StudType.OUT.value
            stud_matrix[0, 0] = StudType.IN.value

            stud_matrix[1, 2] = StudType.RESTART.value
            stud_matrix[1, 1] = StudType.TRIGGER.value
            stud_matrix[1, 0] = StudType.REPEAT.value
        elif direction == 240:
            stud_matrix = np.zeros([3, 2])
            stud_matrix[0, 1] = StudType.IN.value
            stud_matrix[2, 1] = StudType.OUT.value

            stud_matrix[2, 0] = StudType.RESTART.value
            stud_matrix[1, 0] = StudType.TRIGGER.value
            stud_matrix[0, 0] = StudType.REPEAT.value
        super().__init__(name=name, type="mc", stud_matrix=stud_matrix, position=position, direction=direction, is_special=True)

class Motor(Piece):
    mo_id = 1
    def __init__(self, name, position, direction): 
        if direction == 0:
            stud_matrix = np.zeros([1, 3])
            stud_matrix[0, 0] = StudType.NEGATIVE.value
            stud_matrix[0, 2] = StudType.POSITIVE.value
        elif direction == 90:
            stud_matrix = np.zeros([3, 1])
            stud_matrix[0, 0] = StudType.NEGATIVE.value
            stud_matrix[2, 0] = StudType.POSITIVE.value
        elif direction == 180:
            stud_matrix = np.zeros([1, 3])
            stud_matrix[0, 0] = StudType.POSITIVE.value
            stud_matrix[0, 2] = StudType.NEGATIVE.value
        elif direction == 240:
            stud_matrix = np.zeros([3, 1])
            stud_matrix[0, 0] = StudType.POSITIVE.value
            stud_matrix[2, 0] = StudType.NEGATIVE.value
        super().__init__(name=name, type="motor", stud_matrix=stud_matrix, position=position, direction=direction, is_special=True)



# board = Board(direction=0)

# board.swap_pieces([Battery("b1", (0, 2), 0)], {0: 0.1, 1: 0.9})
# board.swap_pieces([Battery("b2", (0, 2), 0), Wire("w1", (0, 0), 90, 3)], {0: 0.2, 1: 0.8})
# board.swap_pieces([Battery("b3", (0, 2), 0), Wire("w4", (0, 0), 90, 3), Wire("w5", (0, 1), 90, 3)], {0: 0.3, 1: 0.7})
# board.swap_pieces([Battery("b4", (0, 2), 0), Wire("w6", (0, 0), 90, 3), Wire("w7", (0, 1), 90, 3), Wire("w8", (0, 0), 0, 3)], {0: 0.4, 1: 0.6})
# board.swap_pieces([Battery("b5", (0, 2), 0), Wire("w9", (0, 0), 90, 3), Wire("w10", (0, 1), 90, 3), Wire("w11", (0, 0), 0, 3), Wire("led1", (2, 0), 0, 3)], {0: 0.3, 1: 0.7})

# test = tasks.TaskObservations("lol", [7, 9, 13, 14, 15, 16, 17], [0, 1])
# print("\n")
# print("BOARD")
# print(board)
# print("\n")
# print("BOARD HISTORY")
# print(board.history)
# test.check_skills(board)
# print("\n")
# print(test)