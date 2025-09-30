from math import pi
from typing import List, Tuple
from util import (START_BOARD, WHITE, BLACK, PAWN, BISHOP, KNIGHT, ROOK, QUEEN, KING,
                  WHITE_Q_CASTLE, WHITE_K_CASTLE, BLACK_K_CASTLE, BLACK_Q_CASTLE,
                  ListBoard, ALL, coordinate_to_square, INV_PIECES,
                  EMPTY, get_colour, get_piece_name, strip_piece, tuple_add, tuple_diff, out_of_bounds,
                  WHITE_PAWN, BLACK_PAWN, WHITE_KING, BLACK_KING, get_delta, WHITE_KING_START, BLACK_KING_START,
                  make_bit_board, print_bit_board,  check_bit_board, set_bit_board, PIECES, SLIDING_PIECES,
                    )

EMPTY_BITBOARD = 0


class Game():
    """Simulates a chess game. Keeps track of the game state and calculates
    legal moves. Also handles move generation and lookahead"""

    def __init__(self, board: ListBoard=START_BOARD, turn: int=WHITE,
                 castling: int=ALL, ep_target: Tuple[int, int] | None=None,
                 halfs: int=0, fulls: int=0):

        self.board: ListBoard = board
        self.turn: int = turn

        #1st bit (MSB): set if white can Kingside castle
        #2nd bit: set if white can Queenside castle
        #3rd bit: set if black can Kingside castle
        #4th bit: set if black can Queenside castle
        self.castling: int = castling

        self.ep_target: Tuple[int, int] = ep_target
        self.halfs: int= halfs #number of half moves (for 50 move rule)
        self.fulls: int = fulls#number of full moves (increments after black moves)

        get_square = self.get_square
        for col in range(8):
            for row in range(8):
                coords = (col, row)
                square = get_square(coords)
                if square == WHITE_KING:
                    self.white_king_pos: Tuple[int, int] = coords
                elif square == BLACK_KING:
                    self.black_king_pos: Tuple[int, int] = coords

        self.white_pieces: set[Tuple[int, int]] = set()
        self.black_pieces: set[Tuple[int, int]] = set()
        for col in range(8):
            for row in range(8):
                coords = (col, row)
                square = self.get_square(coords)
                if square != EMPTY:
                    if get_colour(square) == WHITE:
                        self.white_pieces.add(coords)
                    elif get_colour(square) == BLACK:
                        self.black_pieces.add(coords)
                    else:
                        raise ValueError("int has invalid colour")



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
        ep = '-' if self.ep_target is None else coordinate_to_square(self.ep_target)
        ans += f"ep target square: {ep}\n"
        ans += f"moves til 50 move rule: {self.halfs}\n"
        ans += f"move: {self.fulls}\n"
        return ans

    def __eq__(self, other):
        return (self.castling == other.castling
                and self.black_king_pos == other.black_king_pos
                and self.white_king_pos == other.white_king_pos
                and self.white_pieces == other.white_pieces
                and self.black_pieces == other.black_pieces
                and self.ep_target == other.ep_target
                and self.halfs == other.halfs
                and self.fulls == other.fulls
                and self.board == other.board
                and self.turn == other.turn)

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
            while (row >= 0 and c < 8):
                ray.append(r*8 + c)
                r -= 1 
                col += 1
            bishop_rays[square].append(ray)
            
            #SW
            ray = []
            r, c = row - 1, col - 1
            while (row >= 0 and c >= 0):
                ray.append(r*8 + c)
                r -= 1 
                col -= 1
            bishop_rays[square].append(ray)

            #NW
            r, c = row + 1, col - 1
            while (row < 8 and c >= 0):
                ray.append(r*8 + c)
                r += 1 
                col -= 1
            bishop_rays[square].append(ray)

        return bishop_rays

    def show_piece_positions(self):
        """print every position that is said to hold a piece"""
        print("White pieces")
        get_square = self.get_square
        for pos in self.white_pieces:
            print(get_piece_name(get_square(pos)))
        print("black pieces")
        for pos in self.black_pieces:
            print(get_piece_name(get_square(pos)))

    def show_board(self):
        """print the board for text-based display"""
        ans = ""
        get = self.board.get
        for row in range(8):
            row_string = f"{abs(row - 8)} |"
            for col in range(8):
                square = get(col, row)
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


    def get_pieces(self):
        """Return the positions of every piece in the board who can move on this turn"""
        return self.black_pieces if self.turn == BLACK else self.white_pieces


    def get_square(self, position: Tuple[int, int]) -> int:
        """Return the piece at position, or None if an out of bounds coordinate 
        is provided"""
        if out_of_bounds(position):
            raise Exception("piece oob")
        return self.board.get(position)

    def replace_square(self, position: Tuple[int, int], piece: int):
        """replace the position in board with piece"""
        if position in self.white_pieces:
            self.white_pieces.remove(position)
        elif position in self.black_pieces:
            self.black_pieces.remove(position)

        self.board.set(piece, position)
        if piece == EMPTY:
            return

        if get_colour(piece) == WHITE:
            self.white_pieces.add(position)
        elif get_colour(piece) == BLACK:
            self.black_pieces.add(position)
    
    def is_empty(self, position):
        """if the position holds no piece, return True, else False"""
        if self.get_square(position) == EMPTY:
            return True
        return False

    def change_turn(self):
        """Swap Turns"""
        self.turn = BLACK if self.turn == WHITE else WHITE

    def right_to_castle(self, pos, new_pos):
        """checks if we have the right to peform the particular castling move"""
        piece = self.get_square(pos)
        if not ((piece == WHITE_KING and pos == WHITE_KING_START) or
                (piece == BLACK_KING and pos == BLACK_KING_START)):
            return False
        diff = tuple_diff(pos, new_pos)
        if diff == (2,0):
            castle = WHITE_K_CASTLE if get_colour(piece) == WHITE else BLACK_K_CASTLE
        elif diff == (-2,0):
            castle = WHITE_Q_CASTLE if get_colour(piece) == WHITE else BLACK_Q_CASTLE
        else:
            return False
        return self.castling & castle

    def update_castle_rights(self, pos):
        """Based on the move update the castling rights"""
        piece = self.get_square(pos)
        if strip_piece(piece) == ROOK:
            if get_colour(piece) == WHITE:
                if pos == (7,7):
                    castle = WHITE_K_CASTLE
                elif pos == (0,7):
                    castle = WHITE_Q_CASTLE
                else:
                    return
            elif get_colour(piece) == BLACK:
                if pos == (0,0):
                    castle = BLACK_Q_CASTLE
                elif pos == (7,0):
                    castle = BLACK_K_CASTLE
                else:
                    return
            else:
                raise ValueError("invalid colour")
            self.castling &= (15 - castle)
        elif strip_piece(piece) == KING:
            if get_colour(piece) == WHITE:
                self.castling &= ~(WHITE_K_CASTLE | WHITE_Q_CASTLE)
            elif get_colour(piece) == BLACK:
                self.castling &= ~(BLACK_K_CASTLE | BLACK_Q_CASTLE)

    def correct_move(self, pos, new_pos):
        """A move is considered correct it can be performed on an empty 8x8
        board. Returns True if the move is correct and False otherwise"""

        piece = self.get_square(pos)
        new_square = self.get_square(new_pos)


        if piece == EMPTY:
            return False

        if strip_piece(piece) == PAWN:
            return self.correct_pawn(pos, new_pos)

        elif strip_piece(piece) == KNIGHT:
            return self.correct_knight(pos, new_pos)

        elif strip_piece(piece) == BISHOP:
            return self.correct_bishop(pos, new_pos)

        elif strip_piece(piece) == ROOK:
            return self.correct_rook(pos, new_pos)

        elif strip_piece(piece) == QUEEN:
            return self.correct_queen(pos, new_pos)

        elif strip_piece(piece) == KING:
            return self.correct_king(pos, new_pos)

    def correct_pawn(self, pos: Tuple[int, int], new_pos: Tuple[int, int]):
        """correct pawn move from pos to new_pos"""
        piece = self.get_square(pos)
        diff = tuple_diff(pos, new_pos)

        if get_colour(piece) == WHITE:
            direction = -1
            start_square = 6
        elif get_colour(piece) == BLACK:
            direction = 1
            start_square = 1
        else:
            raise ValueError("invalid colour")

        if diff[1] == 1 * direction:
            if diff[0] not in [-1, 0, 1]:
                return False
        elif diff[1] == 2 * direction:
            if not (pos[1] == start_square and diff[0] == 0):
                return False
        else:
            return False

        return True

    def correct_knight(self, pos, new_pos):
        """correct knight move from pos to new_pos"""
        diff = tuple_diff(pos, new_pos)
        return ((abs(diff[0]) == 1 and abs(diff[1]) == 2) or
            (abs(diff[0]) == 2 and abs(diff[1]) == 1))

    def correct_bishop(self, pos, new_pos):
        """correct bishop move from pos to new_pos"""
        delta = tuple_diff(pos, new_pos)
        return abs(delta[0]) ==  abs(delta[1])

    def correct_rook(self, pos, new_pos):
        """correct rook move from pos to new_pos"""
        delta = get_delta(pos, new_pos)
        return (abs(delta[0]) + abs(delta[1]) == 1)

    def correct_queen(self, pos, new_pos):
        """correct queen move from pos to new_pos"""
        return self.correct_rook(pos, new_pos) or self.correct_bishop(pos, new_pos)

    def correct_king(self, pos, new_pos):
        """correct king move from pos to new_pos"""
        delta = tuple_diff(pos, new_pos)
        return delta in [(x,y) for x in [1, 0, -1] for y in [1, 0, -1] if not (x==0 and y==0)] + [(2, 0), (-2, 0)]

    def valid_move(self, pos, new_pos):
        """A move is considered valid if it is both correct and can be
        performed without colliding with another piece. Returns True if the
        move is valid and False otherwise"""
        
        piece = self.get_square(pos)
        base_piece = strip_piece(piece)
        if not self.correct_move(pos, new_pos):
            return False
        opp = self.get_square(new_pos)
        if opp != EMPTY and get_colour(opp) == get_colour(piece):
            return False
        if base_piece == PAWN:
            diff = tuple_diff(pos, new_pos)
            direction = -1 if get_colour(piece) == WHITE else 1 
            if diff[1] == 2 * direction:
                inbetween_square = self.get_square(tuple_add(pos, (0, 1 * direction)))
                return inbetween_square == EMPTY
            return True
        if base_piece in SLIDING_PIECES:
            return self.check_slide(pos, new_pos)
        return True

    def check_slide(self, pos: Tuple[int, int], new_pos: Tuple[int, int]):
        """Checks that a sliding piece can move from pos to new_pos without
        colliding with another piece."""
        delta = get_delta(pos, new_pos)
        pos = tuple_add(pos, delta)
        while pos != new_pos:
            square = self.get_square(pos)
            if square != EMPTY:
                return False
            pos = tuple_add(pos, delta)
        return True

    def legal_pawn(self, pos: Tuple[int, int], new_pos: Tuple[int, int]):
        """checks the legality of the pawn move"""

        diff = tuple_diff(pos, new_pos)
        new_square = self.get_square(new_pos)
        delta = get_delta(pos, new_pos)

        #The following rules apply:
        # 1. If a pawn moves forward diagonally, it must be capturing a piece
        # 2. If a pawn moves forward straight, there must be no piece in front of it
        if diff[0] == 0 and new_square != EMPTY:
            return False
        if (delta[0] != 0 and new_square == EMPTY):
            return self.is_legal_enpessant(pos, new_pos) 
        return True

    def is_legal_enpessant(self, pos, new_pos):
        """Return True if the move is a legal enpessant"""
        delta = get_delta(pos, new_pos)
        piece = self.get_square(pos)

        #piece next to us is the target
        target_position = tuple_add(pos, (delta[0], 0))
        target_piece = self.get_square(target_position)
        if strip_piece(target_piece) != PAWN or get_colour(target_piece) == get_colour(piece):
            return False
        #make sure our target has just moved
        if self.ep_target != target_position:
            return False
        #finally, check that performing the enpessant will not reveal checks
        if self.is_pinned(piece, pos, new_pos, ignore=self.ep_target):
            return False
        return True

    def is_enpessant(self, pos, new_pos):
        """Return True if the move can be classified as an enpessant"""
        piece = self.get_square(pos)
        delta = get_delta(pos, new_pos)
        return strip_piece(piece) == PAWN and abs(delta[0]) == 1 and self.get_square(new_pos) == EMPTY
        
    def is_castle(self, pos, new_pos):
        """Return True if the move can be classified as a castle"""
        piece = self.get_square(pos)
        return (strip_piece(piece) == KING and tuple_diff(pos, new_pos) in [(2,0), (-2,0)])

    def is_legal_castle(self, king, pos, new_pos):
        """Return True if we can castle from pos to new_pos"""
        colour = get_colour(king)
        delta = get_delta(pos, new_pos)
        
        if not self.right_to_castle(pos, new_pos):
            return False

        if self.in_check(get_colour(king)):
            return False

        target = pos
        while target != new_pos:
            target = tuple_add(target, delta)
            if (self.is_under_attack(target, colour)
                or self.get_square(target) != EMPTY):
                return False

        rook_pos = (0, pos[1]) if new_pos[0] == 2 else (7, pos[1])
        target = tuple_add(target, delta)
        while target != rook_pos:
            if self.get_square(target) != EMPTY:
                return False
            target = tuple_add(target, delta)
        rook = self.get_square(rook_pos)
        if rook == EMPTY or get_colour(rook) != get_colour(king):
            return False

        return True

    def piece_can_attack(self, attacker:Tuple[int, int], target:Tuple[int, int]):
        """return True if the piece at attacker can reach the target"""
        attacker_piece = self.get_square(attacker)
        piece_type = strip_piece(attacker_piece)
        if piece_type == PAWN:
            if self.is_pawn_attack(attacker, target):
                return True
            else:
                return False
        elif target != attacker and self.valid_move(attacker, target):
            return True
        else:
            return False

    
    def is_under_attack(self, target, colour_attacked):
        """return True if the target square is reachable by the opponent of 
        colour_attacked."""
        pieces = self.black_pieces if colour_attacked == WHITE else self.white_pieces
        
        for attacker in pieces:
            if self.piece_can_attack(attacker, target):
                return True
        return False
    
    def will_be_attacked(self, pos, new_pos, colour_attacked):
        """Return True if new_pos will be attackable by the opponent of 
        colour_attacked following a move from pos to new_pos"""

        pieces = self.black_pieces if colour_attacked == WHITE else self.white_pieces

        for attacker in pieces:
            if self.piece_can_attack(attacker, new_pos):
                return True
            #also check whether the new_pos will be attackable following the move
            attacking_piece = self.get_square(attacker)
            if self.is_pinning_piece(strip_piece(attacking_piece)):
                if (self.valid_move(attacker, pos) and new_pos != attacker
                    and self.all_on_same_line(attacker, pos, new_pos)):
                    return True
        return False

    def is_pinning_piece(self, piece):
        return piece == BISHOP or piece == ROOK or piece == QUEEN
    
    def is_pawn_attack(self, pos, new_pos):
        """return true if the piece at pos is a Pawn and the new_position is
        a single square away on a diagonal. Assumes that the peice at pos is a pawn"""
        colour = get_colour(self.get_square(pos))
        diff = tuple_diff(pos, new_pos)
        direction = -1 if colour == WHITE else 1
        return diff[1] == direction and abs(diff[0]) == 1

    def in_check(self, player):
        """return True if the player is in check, otherwise False

        Where player is either 'WHITE' or 'BLACK' """

        king_pos = self.black_king_pos if player == BLACK else self.white_king_pos
        return self.is_under_attack(king_pos, player)

    def generate_blockable_squares(self, target: Tuple[int, int]) -> int:
        """return the bitboard representing the squares that can
        be visited to BLOCK a check. If there is a double
        check, an empty bitboard is returned"""
        dest = self.get_square(target)
        target_colour = get_colour(dest)
        color = BLACK if target_colour == WHITE else WHITE


        get_square = self.get_square
        piece_coords = None
        for row in range(8):
            for col in range(8):
                pos = (col, row)
                piece = get_square(pos)
                if color != get_colour(piece):
                    continue
                if self.valid_move(pos, target):
                    if piece_coords is None:
                        piece_coords = pos
                    else:
                        return EMPTY_BITBOARD
        if piece_coords is None:
            return EMPTY_BITBOARD
        piece = get_square(piece_coords)
        bb = EMPTY_BITBOARD
        if strip_piece(piece) == KNIGHT or strip_piece(piece) == PAWN:
            return set_bit_board(bb, piece_coords)
        elif strip_piece(piece) in [QUEEN, BISHOP, ROOK]:
            delta = get_delta(piece_coords, target)
            while piece_coords != target:
                bb = set_bit_board(bb, piece_coords)
                piece_coords = tuple_add(piece_coords, delta)
            return bb
        else:
            raise Exception("malformed piece")

    def on_same_line(self, piece_pos, other):
        """return true if the two pieces are on the same line"""
        if piece_pos[0] == other[0]:
            return True
        if piece_pos[1] == other[1]:
            return True
        return abs(piece_pos[0] - other[0]) == abs(piece_pos[1] - other[1])

    def get_line(self, piece_pos, other):
        """get the line that the pieces occupy, assuming the pieces 'see'
        eachother (i.e. exist on the same diagonal, row or collumn. A line
        is a Tuple representing the direction of the line. -1 represents the 
        a left diagonal, or upward."""
        if piece_pos[1] > other[1]:
            delta = get_delta(piece_pos, other)
        else:
            delta = get_delta(other, piece_pos)
        return delta

    def all_on_same_line(self, piece_pos:Tuple[int, int], other:Tuple[int, int], *args):
        """return True if every piece is on the same line, False otherwise"""
        if not self.on_same_line(piece_pos, other):
            return False
        cur_line = self.get_line(piece_pos, other)
        for arg in args:
            if not self.on_same_line(arg, other) or self.get_line(arg, other) != cur_line:
                return False
        return True

    def is_pinned(self, piece, position, new_pos, ignore=None):
        """return True if the piece at position is pinned to its own king, False otherwise.
        If ignore is specified, we treat the piece at that position as if its
        wasn't there (this is for enpessant)"""
        colour = get_colour(piece)
        king_pos = self.white_king_pos if colour == WHITE else self.black_king_pos
        king_col, king_row = king_pos
        col, row = position
        #get the direction from the king to the piece in question
        if king_col == col:
            direction = (0,-1) if row < king_row else (0,1)
        elif king_row == row:
            direction = (-1,0) if col < king_col else (1,0)
        elif abs(col - king_col) == abs(row - king_row):
            direction = get_delta(king_pos, position)
        else:
            return False
        #one square at a time, move in that direction
        running_pos = king_pos
        running_pos = tuple_add(running_pos, direction)
        get_square = self.get_square
        while running_pos != position and not out_of_bounds(running_pos):
            if ignore is not None and running_pos == ignore:
                running_pos = tuple_add(running_pos, direction)
                continue
            if get_square(running_pos) != EMPTY:
                return False
            running_pos = tuple_add(running_pos, direction)
        running_pos = tuple_add(running_pos, direction)
        while not out_of_bounds(running_pos):
            if ignore is not None and running_pos == ignore:
                running_pos = tuple_add(running_pos, direction)
                continue
            square = get_square(running_pos)
            if square != EMPTY:
                if get_colour(square) != colour:
                    return self.correct_move(running_pos, king_pos) and running_pos != new_pos and strip_piece(square) != PAWN
                else:
                    return False
            running_pos = tuple_add(running_pos, direction)
        return False

    def legal_move(self, pos, piece, new_pos, perft=None):
        """Attempt to move the piece if legal. A legality check enusres that
        the move is valid (see valid_move) and also ensures all the rules of 
        chess are upheld. These include check rules, pawn movement rules,
        enpessant, castling, and turns."""

        if out_of_bounds(pos) or out_of_bounds(new_pos):
            return False


        colour = get_colour(piece)

        if self.turn != colour:
            return False

        dest  = self.get_square(new_pos) #save this

        if not self.valid_move(pos, new_pos):
            return False
        
        if strip_piece(piece) == PAWN and not self.legal_pawn(pos, new_pos):
            return False

        if strip_piece(piece) == KING:
            if self.is_castle(pos, new_pos):
                return self.is_legal_castle(piece, pos, new_pos)
            elif self.will_be_attacked(pos, new_pos, colour):
                return False
            else:
                return True

        #ensure we are not revealing a check
        king_pos = self.white_king_pos if self.turn == WHITE else self.black_king_pos
        if self.on_same_line(pos, king_pos) and self.is_pinned(piece, pos, new_pos):
            #i.e. if we are pinned, we must REMAIN on the same line
            if strip_piece(piece) == KING or not self.all_on_same_line(pos, king_pos, new_pos):
                return False

        cur_in_check = perft if perft is not None else self.in_check(self.turn)

        if cur_in_check:
            #block the attacking piece with one of our own (we already checked king moves)
            bb_blockables = self.generate_blockable_squares(king_pos)
            return check_bit_board(bb_blockables, new_pos)




        return True

    def change_piece_position(self, pos, new_pos, promotion=None):
        """move the piece w/o changing the turn"""

        piece = self.get_square(pos)
        self.replace_square(pos, EMPTY)
        if promotion is not None:
            piece = promotion
        self.replace_square(new_pos, piece)
        if piece == WHITE_KING:
            self.white_king_pos = new_pos
        elif piece == BLACK_KING:
            self.black_king_pos = new_pos


    def move_piece(self, moveset):
        """perform the moveset (assuming legality), updating the game state accordingly"""
        pos, new_pos, promotion = moveset
        #save these for undoing a move later
        dest = self.get_square(new_pos)
        old_ep = self.ep_target
        old_cr = self.castling
        
        if self.is_castle(pos, new_pos):
            cur_rook = (0, pos[1]) if new_pos[0] == 2 else (7, pos[1])
            target_rook = (3, pos[1]) if new_pos[0] == 2 else (5, pos[1])
            self.change_piece_position(cur_rook, target_rook)

        if self.is_enpessant(pos, new_pos):
            #capture the piece
            op_position = tuple_add(pos, (get_delta(pos, new_pos)[0], 0))
            self.replace_square(op_position, EMPTY)

        if self.is_double_pawn_move(pos, new_pos):
            self.ep_target = new_pos
        else:
            self.ep_target = None

        if strip_piece(self.get_square(pos)) in [KING, ROOK]:
            self.update_castle_rights(pos)

        self.change_piece_position(pos, new_pos, promotion)
        self.change_turn()
        return dest, old_ep, old_cr 

    def unmove_piece(self, moveset, old_new_pos, old_ep, old_cr):
        """reverse the most recent move"""
        pos, new_pos, promotion = moveset
        piece = self.get_square(new_pos)


        if strip_piece(piece) == KING and tuple_diff(pos, new_pos) in [(2,0), (-2,0)]:
            cur_rook = (3, pos[1]) if new_pos[0] == 2 else (5, pos[1])
            old_rook = (0, pos[1]) if new_pos[0] == 2 else (7, pos[1])
            self.replace_square(old_rook, self.get_square(cur_rook))
            self.replace_square(cur_rook, EMPTY)

        if old_ep is not None and self.get_square(old_ep) == EMPTY: #we just did an enpessant
            colour = WHITE if get_colour(piece) == BLACK else BLACK
            self.replace_square(old_ep, PAWN | colour)

        self.ep_target = old_ep
        self.castling = old_cr

        if promotion is not None:
            colour = get_colour(piece)
            self.replace_square(pos, PAWN | colour)
        else:
            self.change_piece_position(new_pos, pos)
        self.replace_square(new_pos, old_new_pos)
        if piece == BLACK_KING:
            self.black_king_pos = pos
        if piece == WHITE_KING:
            self.white_king_pos = pos
        self.change_turn()
        
    def move_if_legal(self, moveset):
        """if the move is legal, move the piece, else return None"""
        pos, new_pos, prom = moveset
        piece = self.get_square(pos)
        if self.legal_move(pos, piece, new_pos):
            return self.move_piece(moveset)
        return None


    def is_double_pawn_move(self, pos, new_pos):
        """Return true if this is a pawn moving two squares"""
        piece = self.get_square(pos)
        return strip_piece(piece) == PAWN and abs(pos[1] - new_pos[1]) == 2

    def is_promotion_move(self, new_pos, piece):
        """return true if the piece is a pawn moving onto the last rank"""
        colour = get_colour(piece)
        return (strip_piece(piece) == PAWN and
                ((new_pos[1] == 0 and colour == WHITE) or
                 (new_pos[1] == 7 and colour == BLACK)))


    def get_promotion_piece(self, piece, promotion):
        """Return a new piece of type promotion w/ piece's attributes

        Assuming promotion in ['B', 'N', 'R', 'Q']"""
        colour = get_colour(piece)
        promotions = {'B': BISHOP | colour, 'N' : KNIGHT | colour,
                      'R' : ROOK | colour, 'Q': QUEEN | colour}
        return promotions[promotion]
        
    
    def in_checkmate(self, player):
        """Return True if the player is in checkmate, otherwise False"""
        return self.generate_all_legal_moves() == []


    def white_pawn_deltas(self, position: Tuple[int, int]):
        deltas = [(-1, -1), (0,-1), (0,-2), (1,-1)]
        for delta in deltas:
            move = tuple_add(position, delta)
            if not out_of_bounds(move):
                yield move

    def black_pawn_deltas(self, position: Tuple[int, int]):
        deltas = [(-1, 1), (0,1), (0,2), (1,1)]
        for delta in deltas:
            move = tuple_add(position, delta)
            if not out_of_bounds(move):
                yield move


    def knight_deltas(self, position: Tuple[int, int]):
        deltas = [-2, -1, 1, 2]
        for x in deltas:
            for y in deltas:
                if abs(x) == abs(y):
                    continue
                move = tuple_add(position, (x, y))
                if not out_of_bounds(move):
                    yield move

    def bishop_deltas(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        return self.get_sliding_deltas(position, [(1, 1), (1, -1), (-1, -1), (-1, 1)])

    def rook_deltas(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        return self.get_sliding_deltas(position, [(1, 0), (0, -1), (-1, 0), (0, 1)])

    def king_deltas(self, position):
        deltas = [(-1, 1), (0, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (0, -1), (1, -1), (-2, 0), (2,0)]
        for delta in deltas:
            move = tuple_add(position, delta)
            if not out_of_bounds(move):
                yield move

    def get_sliding_deltas(self, position: Tuple[int, int], deltas: List[Tuple[int, int]]):
        moves = []
        get_square = self.get_square
        for delta in deltas:
            move = tuple_add(position, delta)
            while not out_of_bounds(move):
                if get_square(move) != EMPTY:
                    moves.append(move)
                    break
                moves.append(move)
                move = tuple_add(move, delta)
            move = position
        return moves


    def generate_moves(self, position: Tuple[int, int], piece) -> List[Tuple[int, int]]:
        """generate possible moves for the piece at position."""
        if piece == EMPTY:
            return []

        base_piece = strip_piece(piece)
        if piece == WHITE_PAWN:
            return list(self.white_pawn_deltas(position))
        elif piece == BLACK_PAWN:
            return  list(self.black_pawn_deltas(position))
        elif base_piece == KNIGHT:
            return  list(self.knight_deltas(position))
        elif base_piece == BISHOP:
            return self.bishop_deltas(position)
        elif base_piece == ROOK:
            return self.rook_deltas(position)
        elif base_piece == QUEEN:
            return self.bishop_deltas(position) + self.rook_deltas(position)
        elif base_piece == KING:
            return  list(self.king_deltas(position))
        else:
            raise ValueError(f"invalid piece: {piece} at position {position}")
    

    def generate_valid_moves(self, position: Tuple[int, int]):
        piece = self.get_square(position)
        return [move for move in self.generate_moves(position, piece) if self.valid_move(position, move)]
    
    def generate_legal_moves(self, position: Tuple[int, int]):
        """return a List of movesets, that is all the legal moves possible in
        this board from the starting position"""
        ans = []
        piece = self.get_square(position)
        colour = get_colour(piece)
        append = ans.append
        for move in self.generate_moves(position, piece):
            if not self.legal_move(position, piece, move):
                continue
            if self.is_promotion_move(move, piece):
                for prom_piece in [BISHOP, KNIGHT, ROOK, QUEEN]:
                    append((position, move, prom_piece | colour))
            else:
                append((position, move, None))
        return ans

    def generate_attacking_moves(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """generate all valid ATTACKING moves for the piece at position"""
        piece = self.board.get(position)
        if piece == EMPTY:
            return []
        if get_colour(piece) == self.turn:
            return []

        ans = []
        append = ans.append
        for target in self.white_pieces:
            if self.valid_move(position, target) and position != target:
                append((position, target))
        for target in self.black_pieces:
            if self.valid_move(position, target) and position != target:
                append((position, target))
        return ans

    def generate_all_moves(self):
        """generates every possible moveset in the board at this state"""
        ans = []
        append = ans.append
        get_square = self.get_square
        for pos in self.get_pieces():
            piece = get_square(pos)
            if piece == EMPTY:
                raise Exception("piece is said to exist but has empty")
            for move in self.generate_moves(pos, piece):
                if strip_piece(piece) == PAWN and move[1] == 0:
                    colour = get_colour(piece)
                    for prom_piece in [BISHOP, KNIGHT, ROOK, QUEEN]:
                        append((pos, move, prom_piece | colour))
                else:
                    append((pos, move, None))
        return ans

    def generate_all_legal_moves(self, perft=None):
        """generates a List of all moves that are strictly legal"""
        ans = []
        append = ans.append
        pieces = self.white_pieces if self.turn == WHITE else self.black_pieces
        get_square = self.get_square
        for pos in pieces:
            piece = get_square(pos)
            for move in self.generate_moves(pos, piece):
                if not self.legal_move(pos, piece, move, perft):
                    continue
                if self.is_promotion_move(move, piece):
                    colour = get_colour(piece)
                    for prom_piece in [BISHOP, KNIGHT, ROOK, QUEEN]:
                        append((pos, move, prom_piece | colour))
                else:
                    append((pos, move, None))
        return ans

    def generate_all_attacking_moves(self) -> List[Tuple[int, int]]:
        """generates every valid ATTACKING move in the board at this state"""
        ans = []
        pieces = self.black_pieces if self.turn == WHITE else self.white_pieces
        extend = ans.extend
        for pos in pieces:
            extend(self.generate_attacking_moves(pos))
        return ans

    def is_pawn_move_promoting(self, pos: Tuple[int, int], colour: int):
        """based on the colour moving, and the position, tells us if we are 
        moving to a promotion square"""
        return (colour == WHITE and pos[1] == 0) or (colour == BLACK and pos[1] == 7)

    def generate_pseudo_legal_moves(self, pos: Tuple[int, int]):
        """generate all pseudo legal moves from pos in this position
        Pseudo Legal = any move that is valid, and doesn't leave the king in
        check (though it may still result in a check"""

        piece = self.get_square(pos)
        colour = get_colour(piece)
        moves = self.generate_moves(pos, piece)

        ans = []
        append = ans.append

        if piece is None:
            raise ValueError("big boo boo")
        elif strip_piece(piece) == PAWN:
            for move in moves:
                if not (self.valid_move(pos, move) and self.legal_pawn(pos, move)):
                    continue
                if self.is_pawn_move_promoting(move, colour):
                    for prom_piece in [BISHOP, KNIGHT, ROOK, QUEEN]:
                        append((pos, move, prom_piece | colour))
                else:
                    append((pos, move, None))
        else:
            for move in moves:
                if self.valid_move(pos, move):
                    append((pos, move, None))
        return ans

    def generate_all_pseudo_legal_moves(self):
        """Reutrns a list of all pseudolegal moves possible in this board"""
        ans = []
        pieces = self.black_pieces if self.turn == WHITE else self.white_pieces
        extend = ans.extend
        for piece in pieces:
            ans.extend(self.generate_pseudo_legal_moves(piece))
        return ans


    def perft(self, depth, prev_moves=None):
        """Run perft at the given depth on this board"""
        if prev_moves is None:
            prev_moves = []

        if depth == 0:
            return 1
        

        in_check = self.in_check(self.turn)

        moves = self.generate_all_legal_moves(in_check)

        num_moves = 0
        for move in moves:
            info = self.move_piece(move)
            if info is None:
                continue
            dest, old_ep, old_cr = info
            num_moves += self.perft(depth-1, prev_moves + [move])
            self.unmove_piece(move, dest, old_ep, old_cr)

        return num_moves
    
    def show_split_perft(self, depth):
        """do perft and print each path"""
        depth = depth - 1
        count = 0
        moves = dict()
        for move in self.generate_all_legal_moves():
            pos, new_pos, prom = move
            movestring = coordinate_to_square(pos) + coordinate_to_square(new_pos)
            info = self.move_if_legal(move)
            if info is not None:
                num = self.perft(depth)
                print(f"{movestring}: {num}")
                dest, old_ep, old_cr = info
                self.unmove_piece(move, dest, old_ep, old_cr)
                count += num
                moves[movestring] = num
        return moves, count

    def perft2(self, depth, prev_moves=None):
        if prev_moves is None:
            prev_moves = []

        if depth == 0:
            return 1

        moves = self.generate_all_pseudo_legal_moves()

        num_moves = 0
        for move in moves:
            info = self.move_piece(move)
            if self.in_check(self.turn):
                self.unmove_piece(move, *info)
            else:
                num_moves += self.perft(depth-1, prev_moves + [move])
                self.unmove_piece(move, *info)

        return num_moves


    def show_perft2(self, depth):
        depth = depth - 1 
        count = 0
        moves = dict()
        for move in self.generate_all_pseudo_legal_moves():
            pos, new_pos, prom = move
            movestring = coordinate_to_square(pos) + coordinate_to_square(new_pos)
            info = self.move_piece(move)
            if self.in_check(self.turn):
                self.unmove_piece(move, *info)
            else:
                num = self.perft2(depth)
                print(f"{movestring}: {num}")
                self.unmove_piece(move, *info)
                count += num
                moves[movestring] = num
        return moves, count






if __name__ == "__main__":
    game = Game()
    #game.move_piece(((1,7), (2,5), None))
    #game.move_piece(((4,1), (4,3), None))
    #game.show_split_perft(1)


