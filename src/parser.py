from pieces import Pawn
from board import Game
from util import (INV_PIECES, WHITE, BLACK, PAWN, BISHOP, KNIGHT, ROOK, QUEEN, KING, Coordinate, ListBoard, Piece,
                  CASTLES, EMPTY, PIECENAMES, COLUMNS, ROWS, COLUMN_CONVERT, ROW_CONVERT, PIECES,
                  coordinate_to_square, INV_CASTLES, strip_piece)

def parse_FEN(text: str):
    board, turn, castling, ep_target, halfs, fulls = text.split()
    board = get_board(board)
    turn  = WHITE if turn == "w" else BLACK
    castling = get_castling(castling)
    ep_target = get_ep_target(ep_target)
    halfs = int(halfs)
    fulls = int(fulls)
    return Game(board, turn, castling, ep_target, halfs, fulls)

def get_board(text: str) -> ListBoard:
    """Takes in the board segment of the FEN, and returns a ListBoard.
    Where 0 is an empty square"""
    board = []
    for square in text:
        if square.isdigit(): #empty squares
            for _ in range(int(square)):
                board.append(EMPTY)
        elif square in PIECES.keys():
            board.append(PIECES[square])
    if len(board) != 64:
                raise Exception(f"invalid FEN board size: {len(board)} expected 64")
    return ListBoard(board)

def get_castling(text: str) -> int:
    """Returns the a 4-bit integer where:
        1st bit (MSB): set if white can Kingside castle
        2nd bit: set if white can Queenside castle
        3rd bit: set if black can Kingside castle
        4th bit: set if black can Queenside castle
    """
    castle_int = 0
    for castle in text:
        if castle in CASTLES.keys():
            castle_int = castle_int | CASTLES[castle]
        else:
            raise Exception(f"Invalid character in castle section: {castle}")
    return castle_int

def get_ep_target(text: str) -> Coordinate | None:
    """Returns the coordinates of the ep target square, or None if no square is provided"""
    if text == '-':
        return None
    else:
        return convert_coordinate(text)

def board_to_FEN(board: Game) -> str:
    """Reverse parse a board object to a FEN string"""
    ans = get_board_str(board.board)
    ans += " "
    ans += get_turn_str(board.turn)
    ans += " "
    ans += get_castling_str(board.castling)
    ans += " "
    ans += coordinate_to_square(board.ep_target) if board.ep_target is not None else '-' #ep target
    ans += " "
    ans += str(board.halfs)
    ans += " "
    ans += str(board.fulls)
    return ans

def get_board_str(board: ListBoard) -> str:
    """return the FEN board string from the ListBoard"""
    ans = ""
    for row in range(board.rows):
        square_count = 0
        for col in range(board.rows):
            square = board.get(col, row)
            if square == EMPTY:
                square_count += 1
            else:
                if square_count > 0:
                    ans += str(square_count)
                    square_count = 0
                ans += INV_PIECES[square]
        if square_count > 0:
            ans += str(square_count)
        ans += '/'
    return ans[:-1] #remove last /

def get_turn_str(turn: int):
    return 'w' if turn == WHITE else 'b'

def get_castling_str(castle: int):
    ans = ""
    for i in range(4):
        mask = 1 << (3 - i)
        if castle & mask:
            ans += INV_CASTLES[mask]
    return ans


def parse_PGN( pgn):
    """Given a string of a PGN (Portable Game Notation) file, return a list
    of parsable moves"""
    MOVE_START_SET = PIECENAMES + COLUMNS + ["O"]
    idx = 0
    pgn = pgn.strip()

    headers = {}
    #get headers
    while pgn[idx] == '[':
        idx += 1
        header_key = ''
        while pgn[idx] != ' ':
            header_key += pgn[idx]
            idx += 1
        idx += 2
        header_val = ''
        while pgn[idx] != '"':
            header_val += pgn[idx]
            idx += 1
        headers[header_key] = header_val
        while pgn[idx] != '\n':
            idx += 1
        idx += 1

    idx += 1 #skip newline

    #parse game
    moves = []
    while pgn[idx:] not in ["1-0", "0-1", "1/2-1/2"]:
        while pgn[idx] not in MOVE_START_SET:
            idx += 1
        move = ''
        while pgn[idx] != ' ' and pgn[idx] != '\n':
            move += pgn[idx]
            idx += 1
        moves.append(move)
        idx += 1

    print(headers)
    return moves

def get_coordinate(row, col):
    """Return a coordinate tuple based on the row and collumn string"""
    if col not in COLUMNS or row not in ROWS:
        print("Invalid Coordinate")
        return
    return (COLUMN_CONVERT[col], ROW_CONVERT[row])


def convert_coordinate(coord):
    """Convert from Chess Coordinate to tuple"""

    if len(coord) != 2:
        print("Invalid Coordinate")
        return
    col, row = coord 
    if col not in COLUMNS or row not in ROWS:
        print("Invalid Coordinate")
        return
    return (COLUMN_CONVERT[col], ROW_CONVERT[row])


def parse_move(move, board):
    """Convert a move in Chess Notation into the form used by the board

    parameters:
        move : String in the form of Standard Chess Notation
        board: Instance of the class Board

    Returns: two sets of coordinates, the first being the square to move from
    and the second to move to."""
    

    move = move.strip("+#")

    if len(move) < 2:
        print(f"invalid notation {move}")
        return

    if move[0] == '0' or move[0] == 'O':
        return parse_castle(move, board)

    if move[0] in COLUMNS:
        return parse_pawn(move, board)

    elif move[0] in PIECENAMES: #Basic Move
        if len(move) < 3:
            print(f"invalid length notation {move}")
            return
        piece_str, move = move[0], move[1:] #cut off processed characters
        row, col = None, None
        if move[0] in ROWS:
            row, move = ROW_CONVERT[move[0]], move[1:] 
        elif move[0] in COLUMNS:
            col, move = COLUMN_CONVERT[move[0]], move[1:]
            if move[0] in ROWS:
                row, move = ROW_CONVERT[move[0]], move[1:]
                if len(move) == 0:
                    return get_moveset(piece_str, (col, row), board)

        if len(move) != 0 and move[0] == 'x':
            move = move[1:]

        start_coords = col, row

        if len(move) < 2:
            print("invalid length notation")
            return
        target_coords = convert_coordinate(move[:2])
        move = move[2:]
        if len(move) == 0:
            return get_moveset(piece_str, target_coords, board, start_coords)
        else:
            print(f"Invalid trailing characters: {move}")
            return


def parse_castle(move, board):
    """Return the castling moveset represented by move"""
    row = 7 if board.turn == "WHITE" else 0
    if move in ['0-0', 'O-O']: #short castle
        return ((4,row), (6,row), None)
    elif move in ['0-0-0', 'O-O-O']: #long castle
        return ((4,row), (2,row), None)
    else:
        print("invalid move: did you mean castle?")
        


    
def parse_pawn(move, board):
    """Parse a pawn move.

    Given we know the string starts with a letter from a-h, and the length
    of move is >= 2"""
    ans = None
    start_col = COLUMN_CONVERT[move[0]]
    if move[1] == 'x': #Capture
        if len(move) < 4:
            print(f"invalid notation {move}")
            return
        ending_square = convert_coordinate(move[2:4])
        candidate_squares = [(start_col, ending_square[1]+1), (start_col, ending_square[1]-1)]
        for coord in candidate_squares:
            if board.can_move_piece(coord, ending_square):
                ans = (coord, ending_square, None)
                break
        if ans is None:
            return
        if len(move) == 4:
            return ans
        prom_valid_length = 6
    else:
        ending_square = convert_coordinate(move[0:2])
        if ending_square is None:
            return
        for i in [-2, -1, 1, 2]:
            coord = (start_col, ending_square[1]+i)
            if not strip_piece(board.get_square(coord)) == PAWN:
                continue
            if board.can_move_piece(coord, ending_square):
                ans = (coord, ending_square, None)
        if ans is None:
            return
        if len(move) == 2:
            return ans
        prom_valid_length = 4

    if len(move) == prom_valid_length:
        promotion, piece = move[-2:] #e.g '=Q'
        if promotion != '=' or piece not in PIECENAMES or piece == 'K':
            print(f"Invalid Promotion: {move}")
            return
        if ending_square[1] != 0 and ending_square[1] != 7:
            print(f"Invalid Promotion: {move}")
            return
        return (ans[0], ans[1], piece)
    else:
        print(f"Invalid Length: {move}")
        return
            

def get_moveset(piece_str, target_coords, board, start_coords=None):
    """return a moveset based on the arguments to the method

    A moveset is a triple containing:
        1. The coordinates of the piece to be moved
        2. The target coordinates for the piece
        3. Promotion indicator: the string representation of the piece to
        promote to, or None if we are not promoting

    Parameters:
        piece_str: a string representation of a piece
        target_coords: the coordinates of our target square
        board: an instance of Board
        start_coords: None if no disambiguation is given, else a set of
            coordinates where either row or collumn may be None. Indicates
            what we know about the starting square"""
    start_col, start_row = None, None

    if start_coords is not None:
        start_col, start_row = start_coords

    moveset = None
    for row in range(8):
        row = start_row if start_row is not None else row
        for col in range(8):
            col = start_col if start_col is not None else col
            square = board.get_square((col, row))
            if square == EMPTY:
                continue
            if (strip_piece(PIECES[piece_str]) == strip_piece(square)
            and board.can_move_piece((col, row), target_coords)):
                if moveset is not None:
                    print("Insufficient disambiguation")
                    return
                moveset = ((col, row), target_coords, None)
            if start_col is not None: #only check this collumn
                break
        if start_row is not None: #only check this row
            break
    if moveset is None:
        print(f"no piece {piece_str} able to move to {target_coords}\n Based on starting square: {start_coords}")
    print(moveset)
    return moveset

if __name__ == "__main__":
    s0 = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    s1 = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    s2 = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2"
    s3 = "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2"
    b0 = parse_FEN(s0)
    print(board_to_FEN(b0))
    print(s0)
    print()
    b1 =parse_FEN(s1)
    print(board_to_FEN(b1))
    print(s1)
    print()
    b2 =parse_FEN(s2)
    print(board_to_FEN(b2))
    print(s2)
    print()
    b3 =parse_FEN(s3)
    print(board_to_FEN(b3))
    print(s3)
    print()
    print(b0)
    print(b1)
    print(b2)
    print(b3)
