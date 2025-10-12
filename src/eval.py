from util import PAWN, BISHOP, QUEEN, KING, ROOK, KNIGHT, get_colour, WHITE, BLACK, strip_piece, EMPTY


# The value of a given piece. bishops slightly better than knights, knights
# and bishops better than 3 pawns
PIECE_VALS = {
    PAWN : 100,
    KNIGHT: 320,
    BISHOP: 330,
    ROOK: 500,
    QUEEN: 900,
    KING: 20000, #placeholder
}

# Piece square tables: Give bonuses based on where the piece is.

PST_PAWN = [
 0,  0,  0,  0,  0,  0,  0,  0,
50, 50, 50, 50, 50, 50, 50, 50,
10, 10, 20, 30, 30, 20, 10, 10,
 5,  5, 10, 25, 25, 10,  5,  5,
 0,  0,  0, 20, 20,  0,  0,  0,
 5, -5,-10,  0,  0,-10, -5,  5,
 5, 10, 10,-20,-20, 10, 10,  5,
 0,  0,  0,  0,  0,  0,  0,  0
]

PST_KNIGHT = [
-50,-40,-30,-30,-30,-30,-40,-50,
-40,-20,  0,  0,  0,  0,-20,-40,
-30,  0, 10, 15, 15, 10,  0,-30,
-30,  5, 15, 20, 20, 15,  5,-30,
-30,  0, 15, 20, 20, 15,  0,-30,
-30,  5, 10, 15, 15, 10,  5,-30,
-40,-20,  0,  5,  5,  0,-20,-40,
-50,-40,-30,-30,-30,-30,-40,-50,
]

PST_BISHOP = [
-20,-10,-10,-10,-10,-10,-10,-20,
-10,  0,  0,  0,  0,  0,  0,-10,
-10,  0,  5, 10, 10,  5,  0,-10,
-10,  5,  5, 10, 10,  5,  5,-10,
-10,  0, 10, 10, 10, 10,  0,-10,
-10, 10, 10, 10, 10, 10, 10,-10,
-10,  5,  0,  0,  0,  0,  5,-10,
-20,-10,-10,-10,-10,-10,-10,-20,
]

PST_ROOK = [
  0,  0,  0,  0,  0,  0,  0,  0,
  5, 10, 10, 10, 10, 10, 10,  5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
  0,  0,  0,  5,  5,  0,  0,  0
]

PST_QUEEN = [
-20,-10,-10, -5, -5,-10,-10,-20,
-10,  0,  0,  0,  0,  0,  0,-10,
-10,  0,  5,  5,  5,  5,  0,-10,
 -5,  0,  5,  5,  5,  5,  0, -5,
  0,  0,  5,  5,  5,  5,  0, -5,
-10,  5,  5,  5,  5,  5,  0,-10,
-10,  0,  5,  0,  0,  0,  0,-10,
-20,-10,-10, -5, -5,-10,-10,-20
]


PST_KING_OPENING = [
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-20,-30,-30,-40,-40,-30,-30,-20,
-10,-20,-20,-20,-20,-20,-20,-10,
 20, 20,  0,  0,  0,  0, 20, 20,
 20, 30, 10,  0,  0, 10, 30, 20
]

PST_KING_ENDGAME = [
-50,-40,-30,-20,-20,-30,-40,-50,
-30,-20,-10,  0,  0,-10,-20,-30,
-30,-10, 20, 30, 30, 20,-10,-30,
-30,-10, 30, 40, 40, 30,-10,-30,
-30,-10, 30, 40, 40, 30,-10,-30,
-30,-10, 20, 30, 30, 20,-10,-30,
-30,-30,  0,  0,  0,  0,-30,-30,
-50,-30,-30,-30,-30,-30,-30,-50
]


MATCH_PIECE = {
    PAWN : PST_PAWN,
    KNIGHT : PST_KNIGHT,
    BISHOP : PST_BISHOP,
    ROOK : PST_ROOK,
    QUEEN : PST_QUEEN,
    KING : PST_KING_OPENING,
}

def mirror(idx):
    return idx ^ 56

def count_minor_pieces(board, colour):
    count = 0

    if colour == WHITE:
        minors = board.white_bishops | board.white_knights | board.white_rooks
    else:
        minors = board.black_bishops | board.black_knights | board.black_rooks

    for _ in board.bb_iterate(minors):
        count += 1
    return count

def is_endgame(board):
    """we are in the endgame if, for both sides, """
    white = not board.white_queens or (board.white_queens and count_minor_pieces(board, WHITE) <= 1)
    black = not board.black_queens or (board.black_queens and count_minor_pieces(board, BLACK) <= 1)
    return black and white

def evaluate_board(board):
    board_list = board.board
    score = 0
    for i in range(64):
        piece = board_list[i]
        if piece == EMPTY:
            continue
        piece_type = strip_piece(piece)
        colour = get_colour(piece)

        if colour == BLACK:
            i = mirror(i)
            factor = -1
        else:
            factor = 1

        #add the piece's base value
        score += factor * (PIECE_VALS[piece_type])

        # get the piece's bonus value
        if piece_type == KING:
            if is_endgame(board):
                bonus =  PST_KING_ENDGAME[i]
            else:
                bonus =  PST_KING_OPENING[i]
        else:
            bonus = MATCH_PIECE[piece_type][i]

        score += factor * (bonus)

    return score








