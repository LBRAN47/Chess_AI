import math

type Piece = int
type Coordinate = tuple[int, int]

KING = 2
QUEEN = 3
ROOK = 6
BISHOP = 4
KNIGHT = 5
PAWN = 1
BLACK = 0
WHITE = 8
EMPTY = 0


PIECES = {"P": WHITE | PAWN, "p" : BLACK | PAWN,
        "B": WHITE | BISHOP, "b" : BLACK | BISHOP,
        "N": WHITE | KNIGHT, "n" : BLACK | KNIGHT,
        "R": WHITE | ROOK, "r" : BLACK | ROOK,
        "Q": WHITE | QUEEN, "q" : BLACK | QUEEN,
        "K": WHITE | KING, "k" : BLACK | KING}
INV_PIECES = {value: key for key, value in PIECES.items()}

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





