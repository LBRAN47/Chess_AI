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
                color = "WHITE" if i == 0 else "BLACK"
                for j in range(8):
                    row.append(Pawn((j,i), color))
            else:
                for j in range(8):
                    row.append(None)
            board.append(row)
        return board
    
def interpreter(text):
    """Converts text into a set of BoardCordinates.

    Args:
        text (str): two squares on the chess board representing the move e.g. "d4e5"
    Returns:
        list[BoardCoordinate]: two BoardCoordinates, one for the starting square and one for the ending square.
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
        piece = board.board[pos[1]][pos[0]]
        print(piece)
        piece.move_piece(new_pos)
        board.board[pos[1]][pos[0]] = None
        board.board[new_pos[1]][new_pos[0]] = piece

