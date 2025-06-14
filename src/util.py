import math

type Piece = int
type Coordinate = tuple[int, int]

EMPTY = 0
PAWN = 1
KING = 2
QUEEN = 3
BISHOP = 4
KNIGHT = 5
ROOK = 6
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

PIECES = {"P": WHITE_PAWN, "p" : BLACK_PAWN,
        "B": WHITE_BISHOP, "b" : BLACK_BISHOP,
        "N": WHITE_KNIGHT, "n" : BLACK_KNIGHT,
        "R": WHITE_ROOK, "r" : BLACK_ROOK,
        "Q": WHITE_QUEEN, "q" : BLACK_QUEEN,
        "K": WHITE_KING, "k" : BLACK_KING}
INV_PIECES = {value: key for key, value in PIECES.items()}

START_BOARD = [BLACK_ROOK, BLACK_KNIGHT, BLACK_BISHOP, BLACK_QUEEN, BLACK_KING, BLACK_BISHOP, BLACK_KNIGHT, BLACK_ROOK] \
              + ([BLACK_PAWN] * 8) \
              + ([EMPTY] * 8 * 4) \
              + ([WHITE_PAWN] * 8) \
              + [WHITE_ROOK, WHITE_KNIGHT, WHITE_BISHOP, WHITE_QUEEN, WHITE_KING, WHITE_BISHOP, WHITE_KNIGHT, WHITE_ROOK]


WHITE_K_CASTLE = 8
WHITE_Q_CASTLE = 4
BLACK_K_CASTLE = 2
BLACK_Q_CASTLE = 1
CASTLES = {'K': WHITE_K_CASTLE, "Q": WHITE_Q_CASTLE,
           'k': BLACK_K_CASTLE, "q": BLACK_Q_CASTLE}
INV_CASTLES = {value: key for key, value in CASTLES.items()}
ALL = WHITE_K_CASTLE | WHITE_Q_CASTLE | BLACK_K_CASTLE | BLACK_Q_CASTLE

PIECENAMES  = ['B', 'N', 'R', 'Q', 'K']
COLUMNS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
ROWS    = ['1', '2', '3', '4', '5', '6', '7', '8']
TRUE_RC = [i for i in range(8)]
COLUMN_CONVERT = dict(zip(COLUMNS, TRUE_RC))
ROW_CONVERT = dict(zip(ROWS, TRUE_RC))

def get_piece_name(piece: Piece):
    return INV_PIECES[piece]

def coordinate_to_square(c: Coordinate) -> str:
    col, row = c
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

def get_colour(piece: Piece) -> int:
    """Return the colour of the piece (i.e such that return value in [WHITE, BLACK])"""
    return piece & (1 << 3)

def strip_piece(piece: Piece) -> Piece:
    """Returns the piece striped of its colour (e.g. strip_piece(BLACK | BISHOP) == BISHOP)"""
    return piece & (1 << 2 | 1 << 1 | 1 << 0)

def tuple_add(a, b):
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


   

class ListBoard():
    """Simple data structure to simulate 2D array functionality w/ a 1D array"""

    def __init__(self, board_list: list[Piece], rows:int | None=None):
        self.board = board_list
        self.length = len(board_list)
        self.rows = rows if rows is not None else int(math.sqrt(self.length))

    def __getitem__(self, index: int):
        """returns the row. This allows for use of double square brackets for individual lookup"""
        if index >= self.rows:
            raise IndexError("Index out of range")
        return self.board[index*self.rows:(index+1)*self.rows]

    def __setitem__(self, index: int, item: list[Piece]):
        for i in range(8):
            self.board[self.rows*index + i] = item[i]

    def get_true_index(self, index: int | Coordinate, row: int | None=None):
        """from a set of coordinates, return the index to the concrete list"""
        if type(index) is not int:
            col, row = index
        else:
            col = index
        return self.rows*row + col 

    def get(self, index: int | Coordinate, row: int | None=None):
        """get allows for either a Coordinate or 2 integers to
        be passed. And returns the value accordingly"""
        return self.board[self.get_true_index(index, row)]

    def set(self, value:Piece, index: int | Coordinate, row: int | None=None):
        """set the value at the coordinate, or row and column"""
        idx = self.get_true_index(index, row)
        self.board[idx] = value


START_BOARD = ListBoard(START_BOARD)



