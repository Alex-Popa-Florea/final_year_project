import numpy as np




class Board:
    def __init__(self, name, direction):
        self.type = "board"
        self.name = name
        if direction == 'vertical':
            rows = 7
            cols = 8
        else:
            rows = 8
            cols = 7
        
        self.pegs = np.empty([rows, cols], dtype=list)
        for i in range(rows):
            for j in range(cols):
                self.pegs[i][j] = []
        
        self.pieces = []
        self.flow = None

    def init_pieces(self, pieces):
        self.pieces = []
        self.flow = None

        for piece in pieces:
            self.pieces.append(pieces)
        pass

    def add_piece(self, piece):
        self.pieces.append(piece)
        if piece.type == "battery":
            pos_peg = piece.pos_peg
            neg_peg = piece.neg_peg
            self.pegs[pos_peg[0]][pos_peg[1]].append(piece.name + "_pos_peg")
            self.pegs[neg_peg[0]][neg_peg[1]].append(piece.name + "_neg_peg")
        


    def find_flow(self):
        flow_found = False
        for piece in self.pieces:
            if piece.type == "battery":
                flow_found = self.flow(piece, piece.pos_peg)
        return flow_found

    def flow(self, piece, peg):
        pass



class Battery:
    b_id = 1
    def __init__(self, name, x1, x2, y1, y2, direction): 
        self.type = "battery"
        self.name = name

        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        
        if direction == "pos topleft":
            self.pos_peg = (x1, y1)
            self.neg_peg = (x1, y2)
        elif direction == "pos topright":
            self.pos_peg = (x2, y1)
            self.neg_peg = (x1, y1)
        elif direction == "pos botleft":
            self.pos_peg = (x2, y2)
            self.neg_peg = (x2, y1)
        elif direction == "pos botright":
            self.pos_peg = (x1, y2)
            self.neg_peg = (x2, y2)
        
        self.power = True
    
