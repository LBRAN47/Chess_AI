from pieces import (tuple_add, out_of_bounds, Pawn, Knight, Bishop, Rook, King, Queen)

def print_board(board):
    print()
    for row in range(7, -1, -1):
        row_string = f"{row} |"
        for col in range(8):
            if board[row][col] is None:
                row_string += " "
            else:
                row_string += str(board[row][col])
            row_string += "|"
        print(row_string)
    print("   0 1 2 3 4 5 6 7")



class Board():

    def __init__(self):
        self.make_board()
        self.turn = "WHITE"

    def make_board(self):
        """Generate the starting chess board"""
        board = []
        for i in range(8):
            row = []
            if i == 0 or i == 7:
                colour = "WHITE" if i == 0 else "BLACK"
                row.append(Rook((0, i), colour))
                row.append(Knight((1, i), colour))
                row.append(Bishop((2, i), colour))
                row.append(Queen((3, i), colour))
                row.append(King((4, i), colour))
                row.append(Bishop((5, i), colour))
                row.append(Knight((6, i), colour))
                row.append(Rook((7, i), colour))
            elif i == 1 or i == 6:
                colour = "WHITE" if i == 1 else "BLACK"
                for j in range(8):
                    row.append(Pawn((j,i), colour))
            else:
                for j in range(8):
                    row.append(None)
            board.append(row)
        self.black_king_pos = (4, 7) 
        self.white_king_pos = (4, 0)
        self.board = board

    def get_square(self, position):
        """Return the piece at position, or None if no piece is at position"""
        if out_of_bounds(position):
            return None
        return self.board[position[1]][position[0]]

    def replace_square(self, position, piece):
        """replace the postiion in board with piece"""
        self.board[position[1]][position[0]] = piece
        return

    def change_turn(self):
        """Swap Turns"""
        self.turn = "BLACK" if self.turn == "WHITE" else "WHITE"

    def can_move(self, pos, new_pos):
        """Return True if there is a piece at pos that can move legally to new_pos

        Move order is not considered"""
        piece = self.get_square(pos)
        new_square = self.get_square(new_pos)

        if piece is None:
            #no piece at position
            return False

        assert piece.position == pos

        if not piece.can_move(new_pos):
            #print("move not in piece moveset")

            return False


        if new_square is not None:
            if new_square.colour == piece.colour:
                #print("cannot move to a square occupied by same coloured piece")
                return False
        if isinstance(piece, Pawn):
            delta = get_delta(pos, new_pos)

            if (delta[0] == 0 and new_square is not None) \
            or (delta[0] != 0 and new_square is None):
                #print("must move diagonally on capture, or straight on move")
                return False

        if isinstance(piece, Knight):
            #Knights can jump over peices
            return True
        
        delta = get_delta(pos, new_pos)
        ghost_pos = tuple_add(pos, delta)
        while ghost_pos != new_pos:
            square = self.get_square(ghost_pos)
            if square is not None:
                #print("attempting to move through a piece")
                return False
            ghost_pos = tuple_add(ghost_pos, delta)

        return True

    def in_check(self, player):
        """return True if the player is in check, otherwise False

        Where player is either 'WHITE' or 'BLACK' """

        king_pos = self.black_king_pos if player == "BLACK" else self.white_king_pos
        for row in range(8):
            for collumn in range(8):
                piece = self.get_square((collumn, row))
                if piece is None:
                    continue
                if piece.colour != player:
                    if self.can_move(piece.position, king_pos):
                        return True
        return False


    def try_move_piece(self, pos, new_pos):
        """Attempt to move the piece if legal"""

        piece = self.get_square(pos)
        dest  = self.get_square(new_pos) #save this
        
        if piece.colour != self.turn:
            return
        
        #Move the piece
        piece.move_piece(new_pos)
        self.replace_square(pos, None)
        self.replace_square(new_pos, piece)
        if isinstance(piece, King):
            if piece.colour == "WHITE":
                self.white_king_pos = piece.position
            else:
                self.black_king_pos = piece.position


        if self.in_check(self.turn):
            #backtrack
            piece.move_piece(pos)
            self.replace_square(pos, piece)
            self.replace_square(new_pos, dest)
            if isinstance(piece, King):
                if piece.colour == "WHITE":
                    self.white_king_pos = piece.position
                else:
                    self.black_king_pos = piece.position
            print(f"Cannot move in a way that leaves {self.turn} in check")
            return

        self.change_turn()

    def in_checkmate(self, player):
        """Return True if the player is in checkmate, otherwise False"""
        pass 
        


def get_delta(pos, new_pos):
    """get a tuple of size 2 representing a single step towards new_pos from pos

    e.g. pos = (2, 2) new_pos = (0,4) ==> delta = (-1, 1)

    """
    diff = (new_pos[0] - pos[0], new_pos[1] - pos[1])
    delta_x = 0 if diff[0] == 0 else diff[0] // abs(diff[0])
    delta_y = 0 if diff[1] == 0 else diff[1] // abs(diff[1]) 
    return (delta_x, delta_y)


    
def interpreter(text):
    """Converts text into a tuple of coordinates.

    Args:
        text (str): two squares on the chess board representing the move
        e.g. "0103" == A2 to A4
    """
    
    if len(text) != 4:
        print("text must be of length 4\n")
        return
    pos = text[0:2]
    target = text[2:]
    squares = []
    for coord in [pos, target]:
        col = int(coord[0])
        row = int(coord[1])
        squares.append((col, row))
    return squares


if __name__ == "__main__":
    assert get_delta((4,4), (3, 3)) == (-1, -1)
    assert get_delta((4, 3), (4, 1)) == (0, -1)
    assert get_delta((2,2), (1, 3)) == (-1, 1)
    board = Board()
    while True:
        print_board(board.board)
        move = input("Make a move: ")
        pos, new_pos = interpreter(move)
        if board.can_move(pos, new_pos):
            board.try_move_piece(pos, new_pos)
