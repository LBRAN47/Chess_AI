import math
from typing import List, Tuple
import random
EMPTY = 0
PAWN = 1
KNIGHT = 2
BISHOP = 3
ROOK = 4
QUEEN = 5
KING = 6
BLACK = 0
WHITE = 8

WHITE_PAWN = WHITE | PAWN
BLACK_PAWN = BLACK | PAWN
WHITE_BISHOP = WHITE | BISHOP
BLACK_BISHOP = BLACK | BISHOP
WHITE_KNIGHT = WHITE | KNIGHT
BLACK_KNIGHT = BLACK | KNIGHT
WHITE_ROOK = WHITE | ROOK
BLACK_ROOK = BLACK | ROOK
WHITE_QUEEN = WHITE | QUEEN
BLACK_QUEEN = BLACK | QUEEN
WHITE_KING = WHITE | KING
BLACK_KING = BLACK | KING

PIECE_REAL_VALS = {
    PAWN : 1,
    BISHOP : 3,
    KNIGHT : 3,
    ROOK : 5,
    QUEEN : 9,
    KING : 0,
}

PIECES = {"P": WHITE_PAWN, "p" : BLACK_PAWN,
        "B": WHITE_BISHOP, "b" : BLACK_BISHOP,
        "N": WHITE_KNIGHT, "n" : BLACK_KNIGHT,
        "R": WHITE_ROOK, "r" : BLACK_ROOK,
        "Q": WHITE_QUEEN, "q" : BLACK_QUEEN,
        "K": WHITE_KING, "k" : BLACK_KING}
INV_PIECES = {value: key for key, value in PIECES.items()}
SLIDING_PIECES = [ROOK, BISHOP, QUEEN]


START_BOARD = [BLACK_ROOK, BLACK_KNIGHT, BLACK_BISHOP, BLACK_QUEEN, BLACK_KING, BLACK_BISHOP, BLACK_KNIGHT, BLACK_ROOK] \
              + ([BLACK_PAWN] * 8) \
              + ([EMPTY] * 8 * 4) \
              + ([WHITE_PAWN] * 8) \
              + [WHITE_ROOK, WHITE_KNIGHT, WHITE_BISHOP, WHITE_QUEEN, WHITE_KING, WHITE_BISHOP, WHITE_KNIGHT, WHITE_ROOK]

BLACK_PIECES = ([BLACK_PAWN] * 8) + ([BLACK_ROOK] * 2) + ([BLACK_KNIGHT] * 2) + ([BLACK_BISHOP] * 2) + [BLACK_QUEEN, BLACK_KING]
WHITE_PIECES = ([WHITE_PAWN] * 8) + ([WHITE_ROOK] * 2) + ([WHITE_KNIGHT] * 2) + ([WHITE_BISHOP] * 2) + [WHITE_QUEEN, WHITE_KING]

PIECE_INDEX = {
    WHITE_PAWN : 0,
    BLACK_PAWN : 1,
    WHITE_BISHOP : 2,
    BLACK_BISHOP : 3,
    WHITE_KNIGHT : 4,
    BLACK_KNIGHT : 5,
    WHITE_ROOK : 6,
    BLACK_ROOK : 7,
    WHITE_QUEEN : 8,
    BLACK_QUEEN : 9,
    WHITE_KING : 10,
    BLACK_KING : 11,
}

random.seed(2025)

ZOBRIST_PIECE = [[random.getrandbits(64) for _ in range(64)] for _ in range(12)]
ZOBRIST_SIDE = random.getrandbits(64)
ZOBRIST_CASTLE = [random.getrandbits(64) for _ in range(16)]
ZOBRIST_EP = [random.getrandbits(64) for _ in range(8)]


WHITE_K_CASTLE = 8
WHITE_Q_CASTLE = 4
BLACK_K_CASTLE = 2
BLACK_Q_CASTLE = 1
CASTLES = {'K': WHITE_K_CASTLE, "Q": WHITE_Q_CASTLE,
           'k': BLACK_K_CASTLE, "q": BLACK_Q_CASTLE}
INV_CASTLES = {value: key for key, value in CASTLES.items()}
ALL = WHITE_K_CASTLE | WHITE_Q_CASTLE | BLACK_K_CASTLE | BLACK_Q_CASTLE
WHITE_KING_START = 7*8 + 4
BLACK_KING_START = 0*8 + 4

PIECENAMES  = ['B', 'N', 'R', 'Q', 'K']
COLUMNS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
ROWS    = ['1', '2', '3', '4', '5', '6', '7', '8']
TRUE_C = [i for i in range(8)]
TRUE_R = [i for i in range(7, -1, -1)]
COLUMN_CONVERT = dict(zip(COLUMNS, TRUE_C))
ROW_CONVERT = dict(zip(ROWS, TRUE_R))

PIECE_FILENAMES = {
    WHITE_PAWN:"wp", BLACK_PAWN:"bp",
    WHITE_BISHOP:"wb", BLACK_BISHOP:"bb",
    WHITE_KNIGHT:"wn", BLACK_KNIGHT:"bn",
    WHITE_ROOK:"wr", BLACK_ROOK:"br",
    WHITE_QUEEN:"wq", BLACK_QUEEN:"bq",
    WHITE_KING:"wk", BLACK_KING:"bk",
}

def assemble_start_board():
    return [BLACK_ROOK, BLACK_KNIGHT, BLACK_BISHOP, BLACK_QUEEN, BLACK_KING, BLACK_BISHOP, BLACK_KNIGHT, BLACK_ROOK] \
              + ([BLACK_PAWN] * 8) \
              + ([EMPTY] * 8 * 4) \
              + ([WHITE_PAWN] * 8) \
              + [WHITE_ROOK, WHITE_KNIGHT, WHITE_BISHOP, WHITE_QUEEN, WHITE_KING, WHITE_BISHOP, WHITE_KNIGHT, WHITE_ROOK]

def count_value(pieces):
    val = 0
    for piece in pieces:
        piece = strip_piece(piece)
        val += PIECE_REAL_VALS[piece]
    return val

def get_real_index(square: tuple[int, int]) -> int:
    return square[1]*8 + square[0]

def get_piece_name(piece: int):
    return INV_PIECES[piece]

def coordinate_to_square(c: int) -> str:
    row, col = divmod(c, 8)
    ans = ""
    for key in COLUMN_CONVERT.keys():
        if COLUMN_CONVERT[key] == col:
            ans += key
            break
    for key in ROW_CONVERT.keys():
        if ROW_CONVERT[key] == row:
            ans += key
            break
    return ans

def get_colour(piece: int) -> int:
    """Return the colour of the piece (i.e such that return value in [WHITE, BLACK])"""
    return piece & (1 << 3)

def strip_piece(piece: int) -> int:
    """Returns the piece striped of its colour (e.g. strip_piece(BLACK | BISHOP) == BISHOP)"""
    return piece & (1 << 2 | 1 << 1 | 1 << 0)

def tuple_add(a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[int, int]:
    """
    returns the element-wise addition of 2 tuples
    e.g. tuple_add((1, 1), (3, -2)) == (4, -1)
    """
    return tuple(map(sum, zip(a,b)))

def tuple_diff(a, b):
    """
    Return the difference from a to b
    """
    return (b[0] - a[0], b[1] - a[1])

def out_of_bounds(x: tuple[int, int]):
    """
    returns true if any element in x is outside of the bounds 0 to 7
    """
    return x[0] > 7 or x[0] < 0 or x[1] > 7 or x[1] < 0

def filter_oob(x):
    return not out_of_bounds(x)


def remove_oob(moves):
    """
    takes a list of moves and removes any out of bounds moves
    """
    return list(filter(filter_oob, moves))

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


class ListBoard():
    """Simple data structure to simulate 2D array functionality w/ a 1D array"""

    def __init__(self, board_list: list[int]=[0]*64, rows:int | None=None):
        self.board = board_list
        self.length = len(board_list)
        self.rows = rows if rows is not None else int(math.sqrt(self.length))

    def __getitem__(self, index: int):
        """returns the row. This allows for use of double square brackets for individual lookup"""
        if index >= self.rows:
            raise IndexError("Index out of range")
        return self.board[index*self.rows:(index+1)*self.rows]

    def __setitem__(self, index: int, item: list[int]):
        for i in range(8):
            self.board[self.rows*index + i] = item[i]

    def get_true_index(self, index: int | Tuple[int, int], row: int | None=None):
        """from a set of coordinates, return the index to the concrete list"""
        if type(index) is not int:
            col, row = index
        else:
            col = index
        return self.rows*row + col 

    def get(self, index: int):
        """get allows for either a Tuple[int, int] or 2 integers to
        be passed. And returns the value accordingly"""
        return self.board[index]

    def set(self, value:int, index: int):
        """set the value at the coordinate, or row and column"""
        self.board[index] = value

    def copy(self):
        return ListBoard(self.board.copy())



def make_bit_board(*squares) -> int:
    bb = 0
    for square in squares:
        bb |= 1 << square
    return bb

def set_bit_board(board: int, coords: Tuple[int, int]):
    col, row = coords
    true_coord = 8*row + col 
    board = board | (1 << true_coord)
    return board


def check_bit_board(board: int, coords: Tuple[int, int]) -> int:
    return board & (1 << (8*coords[1] + coords[0]))

def print_bit_board(bb: int):
    row = ""
    for val in range(64):
        if bb & (1 << val):
            row += "1 "
        else:
            row += "0 "
        if val % 8 == 7:
            print(row)
            row = ""



