def tuple_add(a, b):
    """
    returns the element-wise addition of 2 tuples
    e.g. tuple_add((1, 1), (3, -2)) == (4, -1)
    """
    return tuple(map(sum, zip(a,b)))

def out_of_bounds(x):
    """
    returns true if any element in x is outside of the bounds 0 to 7
    """
    for num in x:
        if num > 7 or num < 0:
            return True
    return False

def filter_oob(x):
    return not out_of_bounds(x)


def remove_oob(moves):
    """
    takes a list of moves and removes any out of bounds moves
    """
    return list(filter(filter_oob, moves))

class Piece():

    def __init__(self, position, colour):
        self.position = position
        self.colour = colour

    def move_piece(self, new_position):
        self.position = new_position

    def get_possible_moves(self):
        raise NotImplementedError("Please Implement get_possible_moves")

    def can_move(self, new_position):
        return new_position in self.get_possible_moves()


class Pawn(Piece):

    def __init__(self, position, colour):
        super().__init__(position, colour)
        self.has_moved = False

    def move_piece(self, new_position):
        super().move_piece(new_position)
        self.has_moved = True

    def get_possible_moves(self):
        if self.colour == "WHITE":
            DELTAS = [(1,1), (-1,1), (0,1)]
            if not self.has_moved:
                DELTAS.append((0,2))
        elif self.colour == "BLACK":
            DELTAS = [(1,-1), (-1,-1), (0,-1)]
            if not self.has_moved:
                DELTAS.append((0,-2))
        else:
            raise NameError("Incorrect piece colour")

        moves = [tuple_add(self.position, coords) for coords in DELTAS]
        return remove_oob(moves) 
    
    def __str__(self):
        return "P"

class Knight(Piece):
    
    def __init__(self, position, colour):
        super().__init__(position, colour)

    def get_possible_moves(self):
        DELTAS = [-2, -1, 1, 2]
        moves = [tuple_add(self.position, (x,y)) for x in DELTAS
                                                for y in DELTAS
                                                if abs(x) != abs(y)]
        return remove_oob(moves)

    def __str__(self):
        return "N"

class Bishop(Piece):

    def __init__(self, position, colour):
        super().__init__(position, colour)

    def get_possible_moves(self):
        moves = []
        move = self.position
        DELTAS = [-1,1]
        for x in DELTAS:
            for y in DELTAS:
                while not out_of_bounds(move := tuple_add(move, (x,y))):
                    moves.append(move)
                move = self.position
        return moves

    def __str__(self):
        return "B"

class Rook(Piece):

    def __init__(self, position, colour):
        super().__init__(position, colour)
        self.has_moved = False

    def get_possible_moves(self):
        moves = []
        move = self.position
        DELTAS = [(1,0), (-1, 0), (0, 1), (0, -1)]

        for delta in DELTAS:
            while not out_of_bounds(move := tuple_add(move, delta)):
                moves.append(move)
            move = self.position
        return moves

    def move_piece(self, new_position):
        super().move_piece(new_position)
        self.has_moved = True

    def __str__(self):
        return "R"
class Queen(Piece):
    
    def __init__(self, position, colour):
        super().__init__(position, colour)
        self.rook = Rook(position, colour)
        self.bishop = Bishop(position, colour)

    def get_possible_moves(self):
        return self.rook.get_possible_moves() + self.bishop.get_possible_moves()

    def move_piece(self, new_position):
        self.rook.move_piece(new_position)
        self.bishop.move_piece(new_position)
        self.position = new_position
    
    def __str__(self):
        return "Q"

class King(Piece):

    def __init__(self, position, colour):
        super().__init__(position, colour)
        self.start_pos = position
        self.has_moved = False

    def move_piece(self, new_position):
        super().move_piece(new_position)
        self.has_moved = True

    def get_possible_moves(self):
        DELTAS = [-1, 0, 1]
        ans = [tuple_add(self.position, (x,y)) for x in DELTAS
                                                for y in DELTAS
                                                if x or y]
        #castling
        if not self.has_moved:
            ans.append(tuple_add(self.start_pos, (2,0)))
            ans.append(tuple_add(self.start_pos, (-2,0)))

        return remove_oob(ans)

    def __str__(self):
        return "K"


if __name__ == "__main__":
    my_piece = Piece((2, 4), "White")
    assert my_piece.position == (2,4)
    assert my_piece.colour == "White"
    my_piece.move_piece((3, 4))
    assert my_piece.position == (3,4)
    knight = Knight((3,3), "WHITE")
    print(f"knight at {knight.position} can move: {knight.get_possible_moves()}")
    bishop = Bishop((3, 3), "WHITE")
    print(f"bishop at {bishop.position} can move: {bishop.get_possible_moves()}")
    rook = Rook((4,4),"White")
    print(f"rook at {rook.position} can move: {rook.get_possible_moves()}")
    queen = Queen((3,2),"White")
    print(f"queen at {queen.position} can move: {queen.get_possible_moves()}")
    king = King((3,2),"White")
    print(f"king at {king.position} can move: {king.get_possible_moves()}")
    king.move_piece((0,0))
    print(f"king at {king.position} can move: {king.get_possible_moves()}")
    pawn = Pawn((1,2), "WHITE")
    print(f"{pawn.colour} pawn at {pawn.position} can move: {pawn.get_possible_moves()}")
    pawn = Pawn((1,1), "BLACK")
    print(f"{pawn.colour} pawn at {pawn.position} can move: {pawn.get_possible_moves()}")



