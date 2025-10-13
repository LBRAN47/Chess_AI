from math import e, pi, remainder
from typing import List, Tuple
import copy
import random
from eval import evaluate_board

from pygame.event import get
from util import (BLACK_BISHOP, START_BOARD, WHITE, BLACK, PAWN, BISHOP, KNIGHT, ROOK, QUEEN, KING,
                  WHITE_Q_CASTLE, WHITE_K_CASTLE, BLACK_K_CASTLE, BLACK_Q_CASTLE,
                  ListBoard, ALL, coordinate_to_square, INV_PIECES,
                  EMPTY, get_colour, get_piece_name, strip_piece, tuple_add, tuple_diff, out_of_bounds,
                  WHITE_PAWN, BLACK_PAWN, WHITE_KING, BLACK_KING, WHITE_KING_START, BLACK_KING_START,
                  make_bit_board, print_bit_board,  check_bit_board, set_bit_board, PIECES, SLIDING_PIECES,
                  WHITE_PIECES, BLACK_PIECES, ALL, assemble_start_board)

type Bitboard = int
type Ray = list[int]
EMPTY_BITBOARD = 0

ROOK_DIRS = [(0, 1), (0, -1), (1, 0), (-1, 0)]
BISHOP_DIRS = [(1,1), (1,-1), (-1, 1), (-1,-1)]

START = 0
END = 1 
PIECE = 2 
CAPTURED_PIECE = 3 
CAPTURED_SQUARE = 4 
CASTLING = 5
EP_TARGET = 6
HALFS = 7
FULLS = 8
TURN = 9
PROMOTION = 10
CASTLE = 11

class Game():
    """Simulates a chess game. Keeps track of the game state and calculates
    legal moves. Also handles move generation and lookahead"""

    def __init__(self, board=None, turn: int=WHITE,
                 castling: int=ALL, ep_target: Tuple[int, int] | None=None,
                 halfs: int=0, fulls: int=0):

        if board is None:
            self.board = START_BOARD
        else:
            self.board = board
        self.turn: int = turn

        #1st bit (MSB): set if white can Kingside castle
        #2nd bit: set if white can Queenside castle
        #3rd bit: set if black can Kingside castle
        #4th bit: set if black can Queenside castle
        self.castling: int = castling

        self.ep_target = None if ep_target is None else ep_target[1]*8 + ep_target[0]
        self.halfs: int= halfs #number of half moves (for 50 move rule)
        self.fulls: int = fulls#number of full moves (increments after black moves)

        self.white_pieces: Bitboard = EMPTY_BITBOARD
        self.black_pieces: Bitboard = EMPTY_BITBOARD
        self.white_pawns: Bitboard = EMPTY_BITBOARD
        self.white_knights: Bitboard = EMPTY_BITBOARD
        self.white_bishops: Bitboard = EMPTY_BITBOARD
        self.white_rooks: Bitboard = EMPTY_BITBOARD
        self.white_queens: Bitboard = EMPTY_BITBOARD
        self.white_king: int = -1
        self.black_pawns: Bitboard = EMPTY_BITBOARD
        self.black_knights: Bitboard = EMPTY_BITBOARD
        self.black_bishops: Bitboard = EMPTY_BITBOARD
        self.black_rooks: Bitboard = EMPTY_BITBOARD
        self.black_queens: Bitboard = EMPTY_BITBOARD
        self.black_king: int = -1

        for square in range(64):
                piece = self.board[square]
                if piece != EMPTY:
                    self.set_piece(square, piece)

        self.knight_moves: list[Bitboard] = self.get_knight_moves()
        self.king_moves: list[Bitboard] = self.get_king_moves()
        self.pawn_pushes_white: list[int] = self.get_white_pawn_pushes() #list of squares
        self.pawn_pushes_black: list[int] = self.get_black_pawn_pushes() #list of squares
        self.pawn_double_pushes_white: list[int] = self.get_white_double_pawn_pushes()
        self.pawn_double_pushes_black: list[int] = self.get_black_double_pawn_pushes()
        self.pawn_attacks_white: list[Bitboard] = self.get_white_pawn_attacks()
        self.pawn_attacks_black: list[Bitboard] = self.get_black_pawn_attacks()
        self.bishop_rays: list[list[Ray]] = self.get_bishop_rays()
        self.rook_rays: list[list[Ray]] = self.get_rook_rays()
        self.queen_rays: list[list[Ray]] = [self.rook_rays[square] + self.bishop_rays[square] for square in range(64)]

        self.white_captured_list = []
        self.black_captured_list = []

    def reset_board(self):
        self.board = assemble_start_board()

        self.white_pieces: Bitboard = EMPTY_BITBOARD
        self.black_pieces: Bitboard = EMPTY_BITBOARD
        self.white_pawns: Bitboard = EMPTY_BITBOARD
        self.white_knights: Bitboard = EMPTY_BITBOARD
        self.white_bishops: Bitboard = EMPTY_BITBOARD
        self.white_rooks: Bitboard = EMPTY_BITBOARD
        self.white_queens: Bitboard = EMPTY_BITBOARD
        self.white_king: int = -1
        self.black_pawns: Bitboard = EMPTY_BITBOARD
        self.black_knights: Bitboard = EMPTY_BITBOARD
        self.black_bishops: Bitboard = EMPTY_BITBOARD
        self.black_rooks: Bitboard = EMPTY_BITBOARD
        self.black_queens: Bitboard = EMPTY_BITBOARD
        self.black_king: int = -1

        for square in range(64):
                piece = self.board[square]
                if piece != EMPTY:
                    self.set_piece(square, piece)

        self.white_captured_list = []
        self.black_captured_list = []
        self.ep_target = None
        self.turn = WHITE
        self.castling = ALL



    def set_bitboards(self):
        self.white_pieces = (self.white_pawns | self.white_bishops
        | self.white_knights | self.white_rooks | self.white_king)
        self.black_pieces = (self.black_pawns | self.black_bishops
        | self.black_knights | self.black_rooks | self.black_king)
        self.pieces = self.white_pieces | self.black_pieces

    def get_knight_moves(self):
        knight_moves = [EMPTY_BITBOARD] * 64
        for square in range(64):
            attacks = EMPTY_BITBOARD
            row, col = divmod(square, 8)
            for drow, drcol in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (2, -1), (2, 1), (1, -2), (1, 2)]:
                r, c = row + drow, col + drcol
                if 0 <= r < 8 and 0 <= c < 8:
                    attacks |= 1 << (r*8 + c)
            knight_moves[square] = attacks
        return knight_moves

    def get_king_moves(self):
        king_moves = [EMPTY_BITBOARD] * 64
        for square in range(64):
            attacks = EMPTY_BITBOARD
            row, col = divmod(square, 8)
            for drow, drcol in [(-1, 1), (0, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (0, -1), (1, -1)]:
                r, c = row + drow, col + drcol 
                if 0 <= r < 8 and 0 <= c < 8:
                    attacks |= 1 << (r*8 + c)
            king_moves[square] = attacks
        return king_moves

    def get_white_pawn_attacks(self):
        pawn_moves = [EMPTY_BITBOARD] * 64
        for square in range(64):
            attacks = EMPTY_BITBOARD
            row, col = divmod(square, 8)

            if row > 0 and col < 7:
                attacks |= 1 << ((row-1)*8 + (col+1))
            if row > 0 and col > 0:
                attacks |= 1 << ((row-1)*8 + (col-1))

            pawn_moves[square] = attacks
        return pawn_moves
    
    def get_black_pawn_attacks(self):
        pawn_moves = [EMPTY_BITBOARD] * 64
        for square in range(64):
            attacks = EMPTY_BITBOARD
            row, col = divmod(square, 8)

            if row < 7 and col < 7:
                attacks |= 1 << ((row+1)*8 + (col+1))
            if row < 7 and col > 0:
                attacks |= 1 << ((row+1)*8 + (col-1))

            pawn_moves[square] = attacks
        return pawn_moves

    def get_white_pawn_pushes(self):
        moves = [-1] * 64
        for square in range(64):
            row, col = divmod(square, 8)
            if row > 0:
                moves[square] = (row-1)*8 + col
        return moves

    def get_black_pawn_pushes(self):
        moves = [-1] * 64
        for square in range(64):
            row, col = divmod(square, 8)
            if row < 7:
                moves[square] = (row+1)*8 + col
        return moves

    def get_white_double_pawn_pushes(self):
        moves = [-1] * 64
        for square in range(64):
            row, col = divmod(square, 8)
            if row == 6:
                moves[square] = (row-2)*8 + col
        return moves

    def get_black_double_pawn_pushes(self):
        moves = [-1] * 64
        for square in range(64):
            row, col = divmod(square, 8)
            if row == 1:
                moves[square] = (row+2)*8 + col
        return moves


    def set_piece(self, square: int, piece: int):
        if piece == EMPTY:
            return
        colour = get_colour(piece)
        piece_type = strip_piece(piece)
        place = 1 << square
        if colour == WHITE:
            self.white_pieces |= place

            if piece_type == PAWN:
                self.white_pawns |= place 
            elif piece_type == BISHOP:
                self.white_bishops |= place 
            elif piece_type == KNIGHT:
                self.white_knights |= place
            elif piece_type == ROOK:
                self.white_rooks |= place 
            elif piece_type == QUEEN:
                self.white_queens |= place
            else:
                self.white_king = square
        else:
            self.black_pieces |= place
            if piece_type == PAWN:
                self.black_pawns |= place 
            elif piece_type == BISHOP:
                self.black_bishops |= place 
            elif piece_type == KNIGHT:
                self.black_knights |= place
            elif piece_type == ROOK:
                self.black_rooks |= place 
            elif piece_type == QUEEN:
                self.black_queens |= place
            else:
                self.black_king = square

        self.board[square] = piece


    def bb_iterate(self, bb: Bitboard):
        while bb:
            sq = (bb & -bb).bit_length() - 1 # finds the lsb set to 1
            yield sq
            bb &= bb - 1 # clear that bit


    def __str__(self):
        ans = ""
        ans += self.show_board()
        ans += f"Turn: {'white' if self.turn == WHITE else 'black'}\n"
        castle_strs = []
        if self.castling & WHITE_K_CASTLE:
            castle_strs.append("White Kingside")
        if self.castling & WHITE_Q_CASTLE:
            castle_strs.append("White Queenside")
        if self.castling & BLACK_K_CASTLE:
            castle_strs.append("Black Kingside")
        if self.castling & BLACK_Q_CASTLE:
            castle_strs.append("Black Queenside")
        ans += "Castling: \n"
        for castle in castle_strs:
            ans += castle + '\n'
        ep = '-' if self.ep_target is None else divmod(self.ep_target, 8)
        ans += f"ep target square: {ep}\n"
        ans += f"moves til 50 move rule: {self.halfs}\n"
        ans += f"move: {self.fulls}\n"

        
        print("WHITE PIECES\n ", print_bit_board(self.white_pieces))
        print("WHITE PAWNS\n ", print_bit_board(self.white_pawns))
        print("WHITE BISHOPS\n ", print_bit_board(self.white_bishops))
        print("WHITE KNIGHTS\n ", print_bit_board(self.white_knights))
        print("WHITE ROOKS\n ", print_bit_board(self.white_rooks))
        print("WHITE QUEENS\n ", print_bit_board(self.white_queens))
        print("WHITE KING\n ", print_bit_board(self.white_king))
        print("black PIECES\n ", print_bit_board(self.black_pieces))
        print("black PAWNS\n ", print_bit_board(self.black_pawns))
        print("black BISHOPS\n ", print_bit_board(self.black_bishops))
        print("black KNIGHTS\n ", print_bit_board(self.black_knights))
        print("black ROOKS\n ", print_bit_board(self.black_rooks))
        print("black QUEENS\n ", print_bit_board(self.black_queens))
        print("black KING\n ", print_bit_board(self.black_king))
        return ans

    def __eq__(self, other):
        return (self.castling == other.castling
                and self.white_pieces == other.white_pieces
                and self.black_pieces == other.black_pieces
                and self.ep_target == other.ep_target
                and self.halfs == other.halfs
                and self.fulls == other.fulls
                and self.board == other.board
                and self.turn == other.turn)

    def get_sliding_mask(self, square, piece_type):
        mask = EMPTY_BITBOARD
        dirs = BISHOP_DIRS if piece_type == BISHOP else ROOK_DIRS
        row, col = divmod(square, 8)
        for dr, dc in dirs:
            r, c = row, col
            while True:
                r += dr
                c += dc
                if not (0 <= r <= 7 and 0 <= c <= 7):
                    break
                mask |= 1 << (r*8 + c)
        return mask

    def get_rook_rays(self) -> List[List[List[int]]]:
        rook_rays = [[] for _ in range(64)]
        for square in range(64):
            row, col = divmod(square, 8)

            ray = []
            for r in range(row-1, -1, -1):
                ray.append(r*8 + col)
            rook_rays[square].append(ray)

            ray = []
            for r in range(row+1, 8):
                ray.append(r*8 + col)
            rook_rays[square].append(ray)

            ray = []
            for c in range(col-1, -1, -1):
                ray.append(row*8 + c)
            rook_rays[square].append(ray)

            ray = []
            for c in range(col+1, 8):
                ray.append(row*8 + c)
            rook_rays[square].append(ray)

        return rook_rays
    
    def get_bishop_rays(self) -> List[List[List[int]]]:
        bishop_rays = [[] for _ in range(64)]
    
        for square in range(64):
            row, col = divmod(square, 8)

            #NE
            ray = []
            r, c = row + 1, col + 1
            while (r < 8 and c < 8):
                ray.append(r*8 + c)
                r += 1 
                c += 1
            bishop_rays[square].append(ray)

            #SE
            ray = []
            r, c = row - 1, col + 1
            while (r >= 0 and c < 8):
                ray.append(r*8 + c)
                r -= 1 
                c += 1
            bishop_rays[square].append(ray)
            
            #SW
            ray = []
            r, c = row - 1, col - 1
            while (r >= 0 and c >= 0):
                ray.append(r*8 + c)
                r -= 1 
                c -= 1
            bishop_rays[square].append(ray)

            #NW
            ray = []
            r, c = row + 1, col - 1
            while (r < 8 and c >= 0):
                ray.append(r*8 + c)
                r += 1 
                c -= 1
            bishop_rays[square].append(ray)

        return bishop_rays

    def get_sliding_moves(self, square, rays):
        moves = []
        piece = self.board[square]
        colour = get_colour(piece)
        for ray in rays[square]:
            for target in ray:
                tp = self.board[target]
                if tp == EMPTY:
                    moves.append(target)
                else:
                    if get_colour(tp) != colour:
                        moves.append(target)
                    break
        return moves

    def show_board(self):
        """print the board for text-based display"""
        ans = ""
        for row in range(8):
            row_string = f"{abs(row - 8)} |"
            for col in range(8):
                square = self.board[8*row + col]
                if square == EMPTY:
                    row_string += " "
                elif square is None:
                    row_string += "X"
                else:
                    row_string += INV_PIECES[square]
                row_string += "|"
            ans += row_string + '\n'
        ans += "   a b c d e f g h\n"
        return ans


    def get_pieces(self) -> Bitboard:
        """Return the positions of every piece in the board who can move on this turn"""
        return self.black_pieces if self.turn == BLACK else self.white_pieces


    def get_square(self, position: int) -> int:
        """Return the piece at position, or None if an out of bounds coordinate 
        is provided"""
        return self.board[position]
        

    def get_colour(self, square: int):
        if (1 << square) & self.white_pieces:
            return WHITE
        elif (1 << square) & self.black_pieces:
            return BLACK
        else:
            return EMPTY

    def remove_piece(self, square: int):
        place = 1 << square

        #remove it from all
        self.white_pieces &= ~place
        self.black_pieces &= ~place
        self.white_pawns &= ~place 
        self.black_pawns &= ~place 
        self.white_bishops &= ~place 
        self.black_bishops &= ~place 
        self.white_knights &= ~place
        self.black_knights &= ~place
        self.white_rooks &= ~place 
        self.black_rooks &= ~place 
        self.white_queens &= ~place
        self.black_queens &= ~place

        self.board[square] = EMPTY

    def change_turn(self):
        """Swap Turns"""
        self.turn = BLACK if self.turn == WHITE else WHITE

    def right_to_castle(self, pos, new_pos):
        """checks if we have the right to peform the particular castling move"""
        if pos != self.black_king and pos != self.white_king:
            return False
        colour = self.get_colour(pos)
        if not ((colour == WHITE and pos == WHITE_KING_START) or
                (colour == BLACK and pos == BLACK_KING_START)):
            return False
        diff = new_pos - pos
        if diff == 2:
            castle = WHITE_K_CASTLE if colour == WHITE else BLACK_K_CASTLE
        elif diff == -2:
            castle = WHITE_Q_CASTLE if colour == WHITE else BLACK_Q_CASTLE
        else:
            return False
        return self.castling & castle

    def update_castle_rights(self, pos):
        """Based on the move update the castling rights"""
        colour = self.get_colour(pos)
        piece = self.board[pos]
        if piece == colour | ROOK:
            if colour == WHITE:
                if pos == 63:
                    castle = WHITE_K_CASTLE
                elif pos == 56:
                    castle = WHITE_Q_CASTLE
                else:
                    return
            elif colour == BLACK:
                if pos == 0:
                    castle = BLACK_Q_CASTLE
                elif pos == 7:
                    castle = BLACK_K_CASTLE
                else:
                    return
            else:
                raise ValueError("invalid colour")
            self.castling &= ~castle
        elif pos == self.white_king:
            self.castling &= ~(WHITE_K_CASTLE | WHITE_Q_CASTLE)
        elif pos == self.black_king:
                self.castling &= ~(BLACK_K_CASTLE | BLACK_Q_CASTLE)


#PSEUDO LEGAL MOVE GENERATION ################################################
    def generate_white_pawn_moves(self):
        moves = []
        occupied = self.white_pieces | self.black_pieces
        opponents = self.black_pieces

        for square in self.bb_iterate(self.white_pawns):
            target = self.pawn_pushes_white[square]
            if target != -1 and not (occupied & (1 << target)):
                targ_row = target // 8
                if targ_row == 0:
                    for promotion in [BISHOP, KNIGHT, ROOK, QUEEN]:
                        moves.append((square, target, promotion | WHITE))
                else:
                    moves.append((square, target, None))
                    dtarget = self.pawn_double_pushes_white[square]
                    if dtarget != -1 and not (occupied & (1 << dtarget)):
                        moves.append((square, dtarget, None))

            #captures 
            caps = self.pawn_attacks_white[square] & opponents 
            for target in self.bb_iterate(caps):
                targ_row = target // 8
                if targ_row == 0:
                    for promotion in [BISHOP, KNIGHT, ROOK, QUEEN]:
                        moves.append((square, target, promotion | WHITE))
                else:
                    moves.append((square, target, None))

            #enpessant
            if self.ep_target is not None:
                ep_bit = 1 << self.ep_target
                if (self.pawn_attacks_white[square] & ep_bit) != 0:
                    moves.append((square, self.ep_target, None))
        return moves

    def generate_black_pawn_moves(self):
        moves = []
        occupied = self.white_pieces | self.black_pieces
        opponents = self.white_pieces

        for square in self.bb_iterate(self.black_pawns):
            target = self.pawn_pushes_black[square]
            if target != -1 and not (occupied & (1 << target)):
                targ_row = target // 8
                if targ_row == 7:
                    for promotion in [BISHOP, KNIGHT, ROOK, QUEEN]:
                        moves.append((square, target, promotion | BLACK))
                else:
                    moves.append((square, target, None))
                    dtarget = self.pawn_double_pushes_black[square]
                    if dtarget != -1 and not (occupied & (1 << dtarget)):
                        moves.append((square, dtarget, None))

            #captures 
            caps = self.pawn_attacks_black[square] & opponents
            for target in self.bb_iterate(caps):
                targ_row = target // 8
                if targ_row == 7:
                    for promotion in [BISHOP, KNIGHT, ROOK, QUEEN]:
                        moves.append((square, target, promotion | BLACK))
                else:
                    moves.append((square, target, None))

            #enpessant
            if self.ep_target is not None:
                ep_bit = 1 << self.ep_target
                if (self.pawn_attacks_black[square] & ep_bit) != 0:
                    moves.append((square, self.ep_target, None))
        return moves


    def generate_knight_moves(self, colour):
        moves = []
        my_bb = self.white_pieces if colour == WHITE else self.black_pieces
        knights = self.white_knights if colour == WHITE else self.black_knights
        for square in self.bb_iterate(knights):
            targets = self.knight_moves[square] & ~my_bb #cancel out own squares
            for target in self.bb_iterate(targets):
                moves.append((square, target, None))
        return moves

    def generate_king_moves(self, colour):
        moves = []
        my_bb = self.white_pieces if colour == WHITE else self.black_pieces
        king = self.white_king if colour == WHITE else self.black_king
        targets = self.king_moves[king] & ~my_bb
        for target in self.bb_iterate(targets):
            moves.append((king, target, None))

        return moves
    
    def generate_sliding_moves(self, square, rays, my_bb):
        moves = []
        occupied = self.black_pieces | self.white_pieces
        for ray in rays[square]:
            for target in ray:
                bit = 1 << target
                if (my_bb & bit) == 0: #if the square is not occupied by our own we can take
                    moves.append((square, target, None))
                if (occupied & bit): #if the square is non empty, we cannot go further
                    break
        return moves
    
    def generate_bishop_moves(self, colour):
        moves = []
        bishops = self.white_bishops if colour == WHITE else self.black_bishops
        own = self.white_pieces if colour == WHITE else self.black_pieces
        for square in self.bb_iterate(bishops):
            moves.extend(self.generate_sliding_moves(square, self.bishop_rays, own))
        return moves

    def generate_rook_moves(self, colour):
        moves = []
        rooks = self.white_rooks if colour == WHITE else self.black_rooks
        own = self.white_pieces if colour == WHITE else self.black_pieces
        for square in self.bb_iterate(rooks):
            moves.extend(self.generate_sliding_moves(square, self.rook_rays, own))
        return moves
    
    def generate_queen_moves(self, colour):
        moves = []
        queens = self.white_queens if colour == WHITE else self.black_queens
        occ = self.white_pieces | self.black_pieces
        own = self.white_pieces if colour == WHITE else self.black_pieces
        for square in self.bb_iterate(queens):
            moves.extend(self.generate_sliding_moves(square, self.queen_rays, own))
        return moves

    def generate_castling_moves(self, colour):
        moves = []
        king_square = self.white_king if colour == WHITE else self.black_king
        row = 7 if colour == WHITE else 0
        oposite_colour = WHITE if colour == BLACK else BLACK

        # King-side castling
        if self.right_to_castle(king_square, king_square + 2):
            squares_between = [king_square + 1, king_square + 2]
            if self.board[king_square + 3] == ROOK | colour and all(self.board[sq] == EMPTY for sq in squares_between):
                if not any(self.is_square_attacked(sq, oposite_colour) for sq in [king_square, king_square + 1, king_square + 2]):
                    moves.append((king_square, king_square + 2, None))

        # Queen-side castling
        if self.right_to_castle(king_square, king_square - 2):
            squares_between = [king_square - 1, king_square - 2, king_square - 3]
            if self.board[king_square - 4] == ROOK | colour and all(self.board[sq] == EMPTY for sq in squares_between):  # last square can hold rook
                if not any(self.is_square_attacked(sq, oposite_colour) for sq in [king_square, king_square - 1, king_square - 2]):
                    moves.append((king_square, king_square - 2, None))

        return moves

    def generate_all_moves(self, colour):
        moves = []
        if colour == WHITE:
            moves.extend(self.generate_white_pawn_moves())
        else:
            moves.extend(self.generate_black_pawn_moves())

        moves.extend(self.generate_bishop_moves(colour))
        moves.extend(self.generate_knight_moves(colour))
        moves.extend(self.generate_rook_moves(colour))
        moves.extend(self.generate_queen_moves(colour))
        moves.extend(self.generate_king_moves(colour))
        moves.extend(self.generate_castling_moves(colour))

        return moves

    def is_square_attacked(self, square, opp_colour):

        #pawn attacks
        if opp_colour == WHITE:
            if (self.pawn_attacks_black[square] & self.white_pawns) != 0:
                return True
        if opp_colour == BLACK:
            if (self.pawn_attacks_white[square] & self.black_pawns) != 0:
                return True

        #knight attacks
        if (self.knight_moves[square] & (self.white_knights if opp_colour == WHITE else self.black_knights)) != 0:
            return True

        #king attacks
        if (self.king_moves[square] & ( (1 << self.white_king) if opp_colour == WHITE else (1 << self.black_king)) != 0):
            return True

        occupied = self.white_pieces | self.black_pieces
        #diagonal attacks
        for ray in self.bishop_rays[square]:
            for target in ray:
                bit = 1 << target
                if (occupied & bit):
                    options = (self.white_bishops | self.white_queens) if opp_colour == WHITE else (self.black_bishops | self.black_queens)
                    if (options & bit):
                        return True
                    break
        #orthogonal attacks
        for ray in self.rook_rays[square]:
            for target in ray:
                bit = 1 << target
                if (occupied & bit):
                    options = (self.white_rooks | self.white_queens) if opp_colour == WHITE else (self.black_rooks | self.black_queens)
                    if (options & bit):
                        return True
                    break

        return False

    
    def get_attack_rays(self, square, opp_colour):
        """
        returns a list of rays. This represents the squares that, if they 
        become occupied by another piece, will block an attack on the piece 
        occupying square.
        """
        rays = []

        # pawn attacks
        if opp_colour == WHITE:
            if (bb := self.pawn_attacks_black[square] & self.white_pawns) != 0:
                rays.append(bb) # the square number
        if opp_colour == BLACK:
            if (bb := self.pawn_attacks_white[square] & self.black_pawns) != 0:
                rays.append(bb)

        # knight attacks
        if (bb := self.knight_moves[square] & (self.white_knights if opp_colour == WHITE else self.black_knights)) != 0:
            rays.append(bb)

        # king attacks
        if (bb := self.king_moves[square] & ((1 << self.white_king) if opp_colour == WHITE else (1 << self.black_king))) != 0:
            rays.append(bb)


        occupied = self.white_pieces | self.black_pieces
        # diagonal attacks
        for ray in self.bishop_rays[square]:
            for idx, target in enumerate(ray):
                bit = 1 << target
                if (occupied & bit):
                    options = (self.white_bishops | self.white_queens) if opp_colour == WHITE else (self.black_bishops | self.black_queens)
                    if (options & bit):
                        rays.append(make_bit_board(*ray[:idx+1]))
                    break

        # orthogonal attacks
        for ray in self.rook_rays[square]:
            for idx, target in enumerate(ray):
                bit = 1 << target
                if (occupied & bit):
                    options = (self.white_rooks | self.white_queens) if opp_colour == WHITE else (self.black_rooks | self.black_queens)
                    if (options & bit):
                        rays.append(make_bit_board(*ray[:idx+1]))
                    break

        return rays
    
    def move_piece(self, move):
        start, end, promotion = move
        piece = self.board[start]
        piece_type = strip_piece(piece)

        #if enpessant:
        if piece_type == PAWN and self.ep_target is not None and end == self.ep_target:
            cap_row = end // 8 + (1 if self.turn == WHITE else -1)
            captured_square = cap_row * 8 + (end % 8)
            captured_piece = self.board[captured_square]
        else:
            captured_piece = self.board[end]
            captured_square = end if captured_piece != EMPTY else None


        castling = self.castling
        ep_target = self.ep_target
        halfs = self.halfs
        fulls = self.fulls
        turn = self.turn
        castle = None

        self.update_castle_rights(start)

        if captured_square is not None:
            self.remove_piece(captured_square)

        self.remove_piece(start)

        #promotions
        self.set_piece(end, promotion) if promotion else self.set_piece(end, piece)

        if captured_piece is not None and captured_piece != EMPTY:
            if get_colour(captured_piece) == WHITE:
                self.white_captured_list.append(captured_piece)
                self.white_captured_list.sort()
            else:
                self.black_captured_list.append(captured_piece)
                self.black_captured_list.sort()


        #castles
        if piece_type == KING and (end - start) == 2:
            castle = 'K_CASTLE'
            if self.turn == WHITE:
                self.set_piece(WHITE_KING_START + 1, ROOK | WHITE)
                self.remove_piece(WHITE_KING_START + 3)
            else:
                self.set_piece(BLACK_KING_START + 1, ROOK | BLACK)
                self.remove_piece(BLACK_KING_START + 3)
        elif piece_type == KING and (end - start) == -2:
            castle = 'Q_CASTLE'
            if self.turn == WHITE:
                self.set_piece(WHITE_KING_START - 1, ROOK | WHITE)
                self.remove_piece(WHITE_KING_START - 4)
            else:
                self.set_piece(BLACK_KING_START - 1, ROOK | BLACK)
                self.remove_piece(BLACK_KING_START - 4)

        self.ep_target = None
        if piece_type == PAWN and abs(end - start) == 16:
            self.ep_target = (start + end) // 2

        self.change_turn()

        return (start, end, piece, captured_piece, captured_square, castling, ep_target, halfs, fulls, turn, promotion, castle)


    def unmake_move(self, move, old_state):
        """
        Restore board to previous state using the dictionary returned by move_piece.
        """
        start, end, piece, captured_piece, captured_square, castling, ep_target, halfs, fulls, old_turn, promotion, castle = old_state

        self.remove_piece(end)
        self.set_piece(start, piece)

        if captured_square is not None and captured_piece != EMPTY:
            self.set_piece(captured_square, captured_piece)

        #castling
        if castle == 'K_CASTLE':
            if old_turn == WHITE:
                self.remove_piece(WHITE_KING_START + 1)  # clear f1
                self.set_piece(WHITE_KING_START + 3, ROOK | WHITE)  # put rook back on h1
            else:
                self.remove_piece(BLACK_KING_START + 1)
                self.set_piece(BLACK_KING_START + 3, ROOK | BLACK)
        elif castle == 'Q_CASTLE':
            if old_turn == WHITE:
                self.remove_piece(WHITE_KING_START - 1)  # clear d1
                self.set_piece(WHITE_KING_START - 4, ROOK | WHITE)  # put rook back on a1
            else:
                self.remove_piece(BLACK_KING_START - 1)
                self.set_piece(BLACK_KING_START - 4, ROOK | BLACK)

        if captured_piece in self.white_captured_list:
            self.white_captured_list.remove(captured_piece)
        elif captured_piece in self.black_captured_list:
            self.black_captured_list.remove(captured_piece)


        # Restore meta state
        self.castling = castling
        self.ep_target = ep_target
        self.halfs = halfs
        self.fulls = fulls
        self.turn = old_turn

    def check_legality(self, move, king_threats, attacks, pins, opp_colour):
        """
        In move generation, we can perform a number of legality checks which allow 
        us to skip a move, speeding up runtime.
        """
        start, end, prom = move
        piece = self.board[start]

        #if we are the king, we cannot move into an attack, but any other move is fine
        if piece == (self.turn | KING):
            if attacks & (1 << end):
                return False
        
        elif start in pins:
            if not ((1 << end) & pins[start]):
                return False

        #if we are in check but not moving the king, we need to block the attack:
        if king_threats:
            #block the attack
            n = len(king_threats)
            assert (n >= 1) #this should be true as there should be some attack on the king because of the outer if
            if not (n == 1 and ((1 << end) & king_threats[0])):
                return False
        
        return True # passed: for now

    def generate_legal_moves(self, colour):
        pseudo_moves = self.generate_all_moves(colour)

        legal_moves = []
        king = self.white_king if colour == WHITE else self.black_king
        attacks = self.get_attack_map(self.get_inverse_turn())
        pins = self.get_pins(king, colour)
        king_threats = self.get_attack_rays(king, self.get_inverse_turn())

        for move in pseudo_moves:
            start, end, prom = move
            piece = self.board[start]

            #if we are the king, we cannot move into an attack, but any other move is fine
            if start == king:
                if attacks & (1 << end):
                    continue
            
            elif start in pins:
                if not (pins[start] & (1 << end)):
                    continue

            #if we are in check but not moving the king, we need to block the attack:
            elif king_threats:
                #block the attack
                n = len(king_threats)
                if not (n == 1 and ((1 << end) & king_threats[0])):
                    continue
            
            legal_moves.append(move)

        return legal_moves
    
    def piece_legal_moves(self, square):
        piece = self.board[square]
        colour = get_colour(piece)
        return [move for move in self.generate_legal_moves(colour) if move[0] == square]

    def is_checkmate(self, colour):
        if not self.generate_legal_moves(colour):
            king_square = self.white_king if colour == WHITE else self.black_king
            if self.is_square_attacked(king_square, BLACK if colour == WHITE else WHITE):
                return True
        return False

    def is_stalemate(self, colour):
        if not self.generate_legal_moves(colour):
            king_square = self.white_king if colour == WHITE else self.black_king
            if not self.is_square_attacked(king_square, BLACK if colour == WHITE else WHITE):
                return True
        return False

    # These are helper functions for our GUI/parser

    def legal_move(self, start, end):
        start = start[1]*8 + start[0]
        end = end[1]*8 + end[0]

        if self.is_promotion_move(end, start):
            colour = get_colour(self.board[start])
            return (start, end, BISHOP | colour) in self.generate_legal_moves(self.turn)
        return (start, end, None) in self.generate_legal_moves(self.turn)

    def is_empty(self, square):
        return self.board[square] == EMPTY

    def is_promotion_move(self, target, square):
        piece = self.board[square]
        colour = get_colour(piece)
        if strip_piece(piece) != PAWN:
            return False
        if colour == WHITE:
            return target // 8 == 0
        if colour == BLACK:
            return target // 8 == 7

    def get_king(self):
        return self.white_king if self.turn == WHITE else self.black_king

    def get_inverse_turn(self):
        return WHITE if self.turn == BLACK else BLACK

    def get_sliding_attack_map(self, square, colour, rays, occupied):
        my_bb = self.white_pieces if colour == WHITE else self.black_pieces
        king = self.white_king if colour == BLACK else self.black_king
        bb = 0
        for ray in rays[square]:
            for target in ray:
                if target == king:
                    continue
                bit = 1 << target
                if (my_bb & bit) == 0: #if the square is not occupied by our own we can take
                    bb |= bit
                if (occupied & bit): #if the square is non empty, we cannot go further
                    bb |= bit
                    break
        return bb


    def get_attack_map(self, colour):
        map = EMPTY_BITBOARD

        #Knight moves
        for square in self.bb_iterate(self.white_knights if colour == WHITE else self.black_knights):
            map |= self.knight_moves[square]

        #King moves
        map |= self.king_moves[self.white_king if colour == WHITE else self.black_king]

        #Pawn attacks
        for square in self.bb_iterate(self.white_pawns if colour == WHITE else self.black_pawns):
            map |= self.pawn_attacks_white[square] if colour == WHITE else self.pawn_attacks_black[square]

        #sliders
        occupied = self.white_pieces | self.black_pieces

        for square in self.bb_iterate(self.white_bishops if colour == WHITE else self.black_bishops):
            map |= self.get_sliding_attack_map(square, colour, self.bishop_rays, occupied)

        for square in self.bb_iterate(self.white_rooks if colour == WHITE else self.black_rooks):
            map |= self.get_sliding_attack_map(square, colour, self.rook_rays, occupied)

        for square in self.bb_iterate(self.white_queens if colour == WHITE else self.black_queens):
            map |= self.get_sliding_attack_map(square, colour, self.bishop_rays, occupied)
            map |= self.get_sliding_attack_map(square, colour, self.rook_rays, occupied)

        return map

    def get_pins(self, king_square, colour):
        """
        Return a dict of pinned pieces -> allowed ray squares.
        Uses sliding attacks from opponent towards king.
        """
        pins = {}
        occupied = self.white_pieces | self.black_pieces

        def get_blockers(piece_type, rays):
            for ray in rays:
                blockers = []
                for square in ray:
                    piece = self.board[square]
                    bit = 1 << square
                    if occupied & bit:
                        if get_colour(piece) == colour:
                            blockers.append(square)
                        else:
                            # enemy piece
                            if strip_piece(piece) in (piece_type, QUEEN) and len(blockers) == 1:
                                # we found a pin
                                pinned_sq = blockers[0]
                                if pinned_sq in pins:
                                    pins[pinned_sq] &= make_bit_board(*ray[:ray.index(square)+1])
                                else:
                                    pins[pinned_sq] = make_bit_board(*ray[:ray.index(square)+1])
                            break

        get_blockers(BISHOP, self.bishop_rays[king_square])
        get_blockers(ROOK, self.rook_rays[king_square])
        return pins

    def is_capture(self, move):
        start, end, _ = move
        return self.board[end] != EMPTY

    def op_turn(self):
        return WHITE if self.turn == BLACK else BLACK

    def is_checking_move(self, move):
        start, end, promotion = move
        moving_piece = self.board[start]
        moving_piece_type = strip_piece(moving_piece)
        colour = get_colour(moving_piece)
        opp_king = self.white_king if colour == BLACK else self.black_king

        if moving_piece_type == KING:
            return False
        if moving_piece_type == BISHOP:
            my_bb = self.white_pieces if colour == WHITE else self.black_pieces
            moves = self.generate_sliding_moves(end, self.bishop_rays, my_bb)
        elif moving_piece_type == ROOK:
            my_bb = self.white_pieces if colour == WHITE else self.black_pieces
            moves = self.generate_sliding_moves(end, self.rook_rays, my_bb)
        elif moving_piece_type == QUEEN:
            my_bb = self.white_pieces if colour == WHITE else self.black_pieces
            moves = self.generate_sliding_moves(end, self.bishop_rays, my_bb)
            moves.extend(self.generate_sliding_moves(end, self.rook_rays, my_bb))
        elif moving_piece_type == KNIGHT:
            row, col = divmod(end, 8)
            for drow, drcol in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (2, -1), (2, 1), (1, -2), (1, 2)]:
                r, c = row + drow, col + drcol
                if 0 <= r < 8 and 0 <= c < 8:
                    if opp_king == r*8 + c:
                        return True
            return False
        elif moving_piece_type == PAWN:
            if colour == WHITE:
                return opp_king in self.bb_iterate(self.pawn_attacks_white[end])
            else:
                return opp_king in self.bb_iterate(self.pawn_attacks_black[end])

        return opp_king in [new_pos for (pos, new_pos, prom) in moves]


        return False

    
    def make_move_adversary(self):
        legal_moves = self.generate_legal_moves(self.turn)
        move, _ = find_best_move(self, 5)
        self.move_piece(move)

def alphabeta(board, depth, alpha, beta, maximizing):
    # Base case
    if depth == 0:
        return evaluate_board(board), None
    if board.is_checkmate(board.turn):
        print("CHECKMATE FOUND")
        if maximizing:
            return -100000 - depth, None
        else:
            return 100000 + depth, None
    if board.is_stalemate(board.turn):
        return 0, None

    best_move = None
    legal_moves = board.generate_legal_moves(board.turn)
    #do the captures first
    legal_moves.sort(key=lambda m : board.is_capture(m) or board.is_checking_move(m), reverse=True)

    if maximizing:
        value = -float('inf')
        for move in legal_moves:
            old_state = board.move_piece(move)
            score, _ = alphabeta(board, depth - 1, alpha, beta, False)
            board.unmake_move(move, old_state)

            if score > value:
                value = score
                best_move = move

            alpha = max(alpha, value)
            if beta <= alpha:
                break  # Beta cutoff
        return value, best_move

    else:
        value = float('inf')
        for move in legal_moves:
            old_state = board.move_piece(move)
            score, _ = alphabeta(board, depth - 1, alpha, beta, True)
            board.unmake_move(move, old_state)

            if score < value:
                value = score
                best_move = move

            beta = min(beta, value)
            if beta <= alpha:
                break  # Alpha cutoff
        return value, best_move

def find_best_move(board, depth):
    maximizing = (board.turn == WHITE)
    score, best_move = alphabeta(board, depth, -float('inf'), float('inf'), maximizing)
    return best_move, score

def perft(board, depth):
    """Count leaf nodes at a given depth using make/unmake moves."""
    if depth == 0:
        return 1

    total = 0
    moves = board.generate_legal_moves(board.turn)
    for move in moves:
        old_state = board.move_piece(move)
        total += perft(board, depth-1)
        board.unmake_move(move, old_state)


    return total

def show_split_perft(board, depth):
    legal_moves = board.generate_legal_moves(board.turn)
    total = 0
    for move in legal_moves:
        old_state = board.move_piece(move)
        count = perft(board, depth-1)
        print(f"{coordinate_to_square(move[0])}{coordinate_to_square(move[1])}: {count}")
        total += count
        board.unmake_move(move, old_state)
        
    print(f"Total nodes: {total}")
    return total

if __name__ == "__main__":
    game = Game()
    print(get_piece_name(game.board[61]))
    print(get_piece_name(game.board[62]))
    moves = game.generate_legal_moves(game.turn)
    for move in moves:
        start, end, _ = move
        print(coordinate_to_square(start), coordinate_to_square(end))
