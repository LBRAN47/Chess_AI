
type Piece = int
type ListBoard = list[list[Piece]]
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

            
