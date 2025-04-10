from pieces import *

def print_board(board):
    for row in range(7, -1, -1):
        row_string = "|"
        for col in range(8):
            if board[row][col] is None:
                row_string += " "
            else:
                row_string += str(board[row][col])
            row_string += "|"
        print(row_string)


class Board():

    def __init__(self):
        self.board = self.make_board()

    def get_square(self, position):
        """Return the piece at position, or None if no piece is at position"""
        return self.board[position[1]][position[0]]

    def replace_square(self, position, piece):
        """replace the postiion in board with piece"""
        self.board[position[1]][position[0]] = piece
        return
    

    def make_board(self):
        board = []
        for i in range(8):
            row = []
            if i == 0 or i == 7:
                color = "WHITE" if i == 0 else "BLACK"
                row.append(Rook((0, i), color))
                row.append(Knight((1, i), color))
                row.append(Bishop((2, i), color))
                row.append(Queen((3, i), color))
                row.append(King((4, i), color))
                row.append(Bishop((5, i), color))
                row.append(Knight((6, i), color))
                row.append(Rook((7, i), color))
            elif i == 1 or i == 6:
                color = "WHITE" if i == 1 else "BLACK"
                for j in range(8):
                    row.append(Pawn((j,i), color))
            else:
                for j in range(8):
                    row.append(None)
            board.append(row)
        return board
    
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
    board = Board()
    while True:
        print_board(board.board)
        move = input("Make a move: ")
        pos, new_pos = interpreter(move)
        piece = board.get_square(pos)
        if piece is not None and new_pos in piece.get_possible_moves():
            piece.move_piece(new_pos)
            board.replace_square(pos, None)
            board.replace_square(new_pos, piece)

