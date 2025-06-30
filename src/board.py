from pieces import (Pawn, Knight, Bishop, Rook, King, Queen)
import time
from util import (START_BOARD, WHITE, BLACK, PAWN, BISHOP, KNIGHT, ROOK, QUEEN, KING,
                  WHITE_Q_CASTLE, WHITE_K_CASTLE, BLACK_K_CASTLE, BLACK_Q_CASTLE,
                  ListBoard, ALL, coordinate_to_square, INV_PIECES,
                  EMPTY, get_colour, get_piece_name, strip_piece, tuple_add, tuple_diff, out_of_bounds,
                  WHITE_PAWN, BLACK_PAWN, WHITE_KING, BLACK_KING, get_delta, WHITE_KING_START, BLACK_KING_START,
                  make_bit_board, print_bit_board,  check_bit_board, set_bit_board, PIECES,
                    )

type Coordinate = tuple[int, int]
type Piece = int
type Moveset = tuple[Coordinate, Coordinate, Piece|None]


class Game():

    def __init__(self, board: ListBoard=START_BOARD, turn: int=WHITE,
                 castling: int=ALL, ep_target: Coordinate | None=None,
                 halfs: int=0, fulls: int=0):
        self.board = board
        self.turn = turn
        self.castling = castling
        #1st bit (MSB): set if white can Kingside castle
        #2nd bit: set if white can Queenside castle
        #3rd bit: set if black can Kingside castle
        #4th bit: set if black can Queenside castle
        self.ep_target = ep_target
        self.halfs = halfs
        self.fulls = fulls
        
        for col in range(8):
            for row in range(8):
                if self.get_square((col, row)) == WHITE_KING:
                    self.white_king_pos = (col, row)
                elif self.get_square((col, row)) == BLACK_KING:
                    self.black_king_pos = (col, row)

        self.white_pieces = set()
        self.black_pieces = set()
        for col in range(8):
            for row in range(8):
                piece = self.get_square((col, row))
                if piece != EMPTY and piece is not None:
                    if get_colour(piece) == WHITE:
                        self.white_pieces.add((col,row))
                    elif get_colour(piece) == BLACK:
                        self.black_pieces.add((col,row))
                    else:
                        raise ValueError("Piece has invalid colour")

        self.squares_attacked = make_bit_board(self.generate_all_attacking_moves())


    def show_piece_positions(self):
        """print every position that is said to hold a piece"""
        for pos in self.white_pieces:
            if self.get_square(pos) == EMPTY or self.get_square(pos) is None:
                print(f"{pos} said to house piece but does not")
        for pos in self.black_pieces:
            if self.get_square(pos) == EMPTY or self.get_square(pos) is None:
                print(f"{pos} said to house piece but does not")



    def show_board(self):
        ans = ""
        for row in range(8):
            row_string = f"{abs(row - 8)} |"
            for col in range(8):
                square = self.board.get(col, row)
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

    def generate_all_possible_moves(self):
        """generates a list of all moves that are strictly legal"""
        return [(pos, new_pos, prom) for (pos, new_pos, prom) in self.generate_all_moves() if self.can_move_piece(pos, new_pos)]

    def get_pieces(self):
        """Return the positions of every piece in the board who can move on this turn"""
        return self.black_pieces if self.turn == BLACK else self.white_pieces


    def get_square(self, position: Coordinate):
        """Return the piece at position, or None if no piece is at position"""
        if out_of_bounds(position):
            return None
        return self.board.get(position)

    def replace_square(self, position: Coordinate, piece: Piece):
        """replace the postiion in board with piece"""
        self.board.set(piece, position)
        if piece == EMPTY:
            self.white_pieces.discard(position)
            self.black_pieces.discard(position)
        else: 
            if get_colour(piece) == WHITE:
                self.white_pieces.add(position)
            elif get_colour(piece) == BLACK:
                self.black_pieces.add(position)

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
        if piece is None:
            return
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
            self.castling &= (15 - castle)
        elif strip_piece(piece) == KING:
            if get_colour(piece) == WHITE:
                self.castling &= BLACK_K_CASTLE | BLACK_Q_CASTLE
            elif get_colour(piece) == BLACK:
                self.castling &= WHITE_K_CASTLE | WHITE_Q_CASTLE
            

    def generate_all_attacking_moves(self) -> set[Coordinate]:
        """generates every possible ATTACKING move in the board at this state"""
        ans = set()
        pieces = self.black_pieces if self.turn == WHITE else self.white_pieces
        for pos in pieces:
            ans.update(self.generate_attacking_moves(pos))
        return ans

    def generate_all_moves(self) -> set[Moveset]:
        """generates every possible move in the board at this state"""
        ans = set()
        for pos in self.get_pieces():
            piece = self.get_square(pos)
            if piece is None:
                raise Exception("piece is said to exist but has empty")
            for move in self.generate_moves(pos):
                if strip_piece(piece) == PAWN and move[1] == 0:
                    colour = get_colour(piece)
                    for prom_piece in [BISHOP, KNIGHT, ROOK, QUEEN]:
                        ans.add((pos, move, prom_piece | colour))
                else:
                    ans.add((pos, move, None))
        return ans

    def generate_attacking_moves(self, position: Coordinate) -> list[Coordinate]:
        """generate all possible ATTACKING moves for the piece at position"""
        piece = self.board.get(position)
        if piece == EMPTY or piece is None:
            return []
        if get_colour(piece) == self.turn:
            return []
        if piece == WHITE_PAWN:
            return [tuple_add(position, delta) for delta in [(-1, -1), (1,-1)]
                    if self.valid_move(position, tuple_add(position, delta))]
        elif piece == BLACK_PAWN:
            return [tuple_add(position, delta) for delta in [(-1, 1), (1,1)]
                    if self.valid_move(position, tuple_add(position, delta))]
        elif strip_piece(piece) in [BISHOP, ROOK, QUEEN]:
            bishop_deltas =  [(1,1), (1,-1), (-1, 1), (-1,-1)]
            rook_deltas = [(1,0), (0,1), (-1,0), (0,-1)]
            if strip_piece(piece) == BISHOP:
                deltas = bishop_deltas
            elif strip_piece(piece) == ROOK:
                deltas = rook_deltas
            else:
                deltas = bishop_deltas + rook_deltas
            moves = []
            for delta in deltas:
                move = tuple_add(position, delta)
                while not out_of_bounds(move):
                    square = self.get_square(move)
                    if square is None:
                        break
                    if square != EMPTY:
                        moves.append(move)
                        if not (strip_piece(square) == KING and get_colour(square) != get_colour(piece)):
                            break
                    moves.append(move)
                    move = tuple_add(move, delta)
                move = position
            return moves
        else:
            return self.generate_valid_moves(position)

    def white_pawn_deltas(self, position: Coordinate) -> list[Coordinate]:
        return [tuple_add(position, delta) for delta in [(-1, -1), (0,-1), (0,-2), (1,-1)]]

    def black_pawn_deltas(self, position: Coordinate) -> list[Coordinate]:
        return [tuple_add(position, delta) for delta in [(-1, 1), (0,1), (0,2), (1,1)]]

    def knight_deltas(self, position: Coordinate) -> list[Coordinate]:
        deltas = [-2, -1, 1, 2]
        return [tuple_add(position, (x,y)) for x in deltas
                                                for y in deltas
                                                if abs(x) != abs(y)]
    def bishop_deltas(self, position: Coordinate) -> list[Coordinate]:
        deltas =  [(1,1), (1,-1), (-1, 1), (-1,-1)]
        return self.get_sliding_deltas(position, deltas)

    def rook_deltas(self, position: Coordinate) -> list[Coordinate]:
        deltas = [(1,0), (0,1), (-1,0), (0,-1)]
        return self.get_sliding_deltas(position, deltas)

    def get_sliding_deltas(self, position: Coordinate, deltas: list[Coordinate]):
        moves = []
        for delta in deltas:
            move = tuple_add(position, delta)
            while not out_of_bounds(move):
                if self.get_square(move) != EMPTY:
                    moves.append(move)
                    break
                moves.append(move)
                move = tuple_add(move, delta)
            move = position
        return moves

    def king_deltas(self, position):
        deltas = [(x,y) for x in [1, 0, -1] for y in [1, 0, -1] if not (x==0 and y==0)]
        deltas = deltas + [(-2, 0), (2,0)] #castling is a king move
        return [tuple_add(position, delta) for delta in deltas]

    def generate_moves(self, position: Coordinate) -> list[Coordinate]:
        """generate possible moves for the piece at position."""
        piece = self.board.get(position)
        if piece == EMPTY:
            return []

        if piece == WHITE_PAWN:
            return self.white_pawn_deltas(position)
        elif piece == BLACK_PAWN:
            return self.black_pawn_deltas(position)
        elif strip_piece(piece) == KNIGHT:
            return  self.knight_deltas(position)
        elif strip_piece(piece) == BISHOP:
            return self.bishop_deltas(position)
        elif strip_piece(piece) == ROOK:
            return self.rook_deltas(position)
        elif strip_piece(piece) == QUEEN:
            return self.bishop_deltas(position) + self.rook_deltas(position)
        elif strip_piece(piece) == KING:
            return self.king_deltas(position)
        else:
            raise ValueError(f"invalid piece: {piece} at position {position}")


    def generate_valid_moves(self, position: Coordinate):
        """generate all possible moves that are also valid"""
        return [move for move in self.generate_moves(position) if self.can_move_piece(position, move)]

    def valid_move(self, pos, new_pos):
        """Return True if there is a piece at pos that can move legally to new_pos

        Move order is not considered"""
        piece = self.get_square(pos)
        new_square = self.get_square(new_pos)

        if piece is None or new_square is None: #oob
            return False

        if piece == EMPTY:
            return False

        
        if strip_piece(piece) == PAWN:
            return self.validate_pawn(pos, new_pos)

        elif strip_piece(piece) == KNIGHT:
            return self.validate_knight(pos, new_pos)

        elif strip_piece(piece) == BISHOP:
            return self.validate_bishop(pos, new_pos)

        elif strip_piece(piece) == ROOK:
            return self.validate_rook(pos, new_pos)

        elif strip_piece(piece) == QUEEN:
            return self.validate_queen(pos, new_pos)

        elif strip_piece(piece) == KING:
            return self.validate_king(pos, new_pos)


    def check_slide(self, pos: Coordinate, new_pos: Coordinate):
        """Checks that a sliding piece can move from pos to new_pos without
        colliding with another piece."""

        delta = get_delta(pos, new_pos)
        ghost_pos = tuple_add(pos, delta)
        while ghost_pos != new_pos:
            square = self.get_square(ghost_pos)
            if square != EMPTY:
                return False
            ghost_pos = tuple_add(ghost_pos, delta)
        return True

    def validate_pawn(self, pos: Coordinate, new_pos: Coordinate):
        """Validate pawn move from pos to new_pos, in the context of this board"""
        piece = self.get_square(pos)
        new_square = self.get_square(new_pos)
        delta = get_delta(pos, new_pos)
        diff = tuple_diff(pos, new_pos)

        #Pawns by nature can move in the following ways:
        # 1. One space forward
        # 2. One space forward diagonally
        # 3. Two spaces forward (given it is on the starting square)
        #we check these are first satisfied
        if get_colour(piece) == WHITE:
            if diff[1] == -1:
                if diff[0] not in [-1, 0, 1]:
                    return False
            elif diff[1] == -2:
                if pos[1] != 6: #i.e not on starting square
                    return False
            else:
                return False
        elif get_colour(piece) == BLACK:
            if diff[1] == 1:
                if diff[0] not in [-1, 0, 1]:
                    return False
            elif diff[1] == 2:
                if pos[1] != 1:
                    return False
            else:
                return False
        else:
            raise ValueError(f"malformed piece {piece} at {pos}")

        #now check that the move is valid in the context of the board. 
        #The following rules apply:
        # 1. If a pawn moves forward diagonally, it must be capturing a piece
        # 2. If a pawn moves forward straight, there must be no piece in front of it
        if (diff[0] == 0):
            if new_square != EMPTY:
                return False
            #check inbetween square
            if (abs(diff[1]) == 2):
                inbetween = -1 if diff[1] == -2 else 1
                if self.board.get((pos[0], pos[1] + inbetween)) != EMPTY:
                    return False
        if (delta[0] != 0 and new_square == EMPTY):
            return self.is_valid_enpessant(pos, new_pos) 

        return True

    def validate_knight(self, pos, new_pos):
        diff = tuple_diff(pos, new_pos)
        return (abs(diff[0]) == 1 and abs(diff[1]) == 2) or (abs(diff[0]) == 2 and abs(diff[1]) == 1)

    def validate_bishop(self, pos, new_pos):
        delta = get_delta(pos, new_pos)
        return abs(delta[0]) == 1 and abs(delta[1]) == 1 and self.check_slide(pos, new_pos)

    def validate_rook(self, pos, new_pos):
        delta = get_delta(pos, new_pos)
        return (abs(delta[0]) + abs(delta[1]) == 1) and self.check_slide(pos, new_pos)

    def validate_queen(self, pos, new_pos):
        return self.validate_rook(pos, new_pos) or self.validate_bishop(pos, new_pos)

    def validate_king(self, pos, new_pos):
        delta = tuple_diff(pos, new_pos)
        return delta in [(x,y) for x in [1, 0, -1] for y in [1, 0, -1] if not (x==0 and y==0)] + [(2, 0), (-2, 0)]


    def is_valid_enpessant(self, pos, new_pos):
        """Return True if we can capture enpessant"""
        delta = get_delta(pos, new_pos)
        piece = self.get_square(pos)
        #piece next to us (opposite colour)
        target_position = tuple_add(pos, (delta[0], 0))
        target_piece = self.get_square(target_position)
        if target_piece != PAWN or get_colour(target_piece) == get_colour(piece):
            return False
        #piece has just moved.
        if self.ep_target != target_position:
            return False
        return True


    def is_enpessant(self, pos, new_pos):
        """Return True if the move is an enpessant"""
        piece = self.get_square(pos)
        delta = get_delta(pos, new_pos)
        return strip_piece(piece) == PAWN and abs(delta[0]) == 1 and self.get_square(new_pos) == EMPTY
        
    def is_castle(self, pos, new_pos):
        """Return True if the move is a castle"""
        piece = self.get_square(pos)
        return (strip_piece(piece) == KING and tuple_diff(pos, new_pos) in [(2,0), (-2,0)])

    def king_castle_valid(self, king, pos, new_pos):
        """Return True if this king can move from pos to new_pos, in a way that
        satisfies the rules of castling."""
        return (not self.in_check(get_colour(king))
                and self.get_square(new_pos) == EMPTY
                and self.valid_move(pos, new_pos)
                and self.right_to_castle(pos, new_pos))

    def is_valid_castle(self, king, pos, new_pos):
        """Return True if we can castle from pos to new_pos"""
        delta = get_delta(pos, new_pos)
        
        if not self.right_to_castle(pos, new_pos):
            return False

        if self.in_check(get_colour(king)):
            return False

        target = pos
        while target != new_pos:
            target = tuple_add(target, delta)
            if (self.is_attacked(target)
                or self.get_square(target) != EMPTY):
                return False

        rook_pos = (0, pos[1]) if new_pos[0] == 2 else (7, pos[1])
        rook = self.get_square(rook_pos)
        if rook == EMPTY or get_colour(rook) != get_colour(king) or self.is_attacked(rook_pos):
            return False

        return True

    def is_attacked(self, pos):
        """check if the position can be attacked by the player opposite to the current turn"""
        return check_bit_board(self.squares_attacked, pos)

    def in_check(self, player):
        """return True if the player is in check, otherwise False

        Where player is either 'WHITE' or 'BLACK' """

        king_pos = self.black_king_pos if player == BLACK else self.white_king_pos
        return self.is_attacked(king_pos)

    def generate_blockable_squares(self, target: Coordinate):
        """return the bitboard representing the squares that can
        be visited to BLOCK a check. If None is returned, there is a double
        check, meaning no block is possible"""
        target_colour = get_colour(self.get_square(target))
        color = BLACK if target_colour == WHITE else WHITE
        piece_coords = None
        for row in range(8):
            for col in range(8):
                pos = (col, row)
                if color != get_colour(self.get_square(pos)):
                    continue
                if self.valid_move(pos, target):
                    if piece_coords is None:
                        piece_coords = pos
                    else:
                        return None
        if piece_coords is None:
            return 0 #empty bit_board
        piece = self.get_square(piece_coords)
        bb = 0
        if strip_piece(piece) == KNIGHT or strip_piece(piece) == PAWN:
            return set_bit_board(bb, piece_coords)
        if strip_piece(piece) in [QUEEN, BISHOP, ROOK]:
            delta = get_delta(piece_coords, target)
            while piece_coords != target:
                bb = set_bit_board(bb, piece_coords)
                piece_coords = tuple_add(piece_coords, delta)
            return bb





    def can_move_piece(self, pos, new_pos):
        """Attempt to move the piece if legal"""
        piece = self.get_square(pos)
        dest  = self.get_square(new_pos) #save this

        if not (self.valid_move(pos, new_pos) and self.turn == get_colour(self.get_square(pos))):
            return False

        if dest != EMPTY:
            if get_colour(dest) == get_colour(piece):
                return False


        if self.in_check(self.turn):
            #option 1: move the king out of the way of attack
            if strip_piece(piece) == KING:
                if tuple_diff(pos, new_pos) in [(2,0), (-2,0)]: #cannot castle out of check
                    return False
                if not self.is_attacked(new_pos):
                    return True
                return False
            #option 2: block the attacking piece with one of our own
            king_pos = self.white_king_pos if self.turn == WHITE else self.black_king_pos
            bb_blockables = self.generate_blockable_squares(king_pos)
            if bb_blockables is None:
                return False
            if check_bit_board(bb_blockables, new_pos):
                return True
            return False
        
        if self.is_castle(pos, new_pos):
            return self.is_valid_castle(piece, pos, new_pos)


        if self.is_enpessant(pos, new_pos):
            return self.is_valid_enpessant(pos, new_pos)

        return True

    
    def backtrack(self, piece, pos, new_pos, dest):
        """Given a piece, pos, new_pos and dest:

        1. Move piece back to pos
        2. Move dest back to new_pos
        3. Reset king_position"""
        self.replace_square(pos, piece)
        self.replace_square(new_pos, dest)
        if strip_piece(piece) == KING:
            if get_colour(piece) == WHITE:
                self.white_king_pos = pos
            else:
                self.black_king_pos = pos


    def change_piece_position(self, pos, new_pos, promotion=None):
        """move the piece w/o changing the turn"""

        piece = self.get_square(pos)
        self.replace_square(pos, EMPTY)
        if promotion is not None:
            piece = self.get_promotion_piece(piece, promotion)
        self.replace_square(new_pos, piece)
        if piece == WHITE_KING:
            self.white_king_pos = new_pos
        elif piece == BLACK_KING:
            self.black_king_pos = new_pos


    def move_piece(self, moveset):
        """if we can move, perform the moveset, updating the game state accordingly"""

        pos, new_pos, promotion = moveset
        #save these for undoing a move later
        dest = self.get_square(new_pos)
        old_ep = self.ep_target
        old_cr = self.castling

        if not self.can_move_piece(pos, new_pos):
            return
        
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
        self.squares_attacked = make_bit_board(self.generate_all_attacking_moves())
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
        self.squares_attacked = make_bit_board(self.generate_all_attacking_moves())

    def is_double_pawn_move(self, pos, new_pos):
        """Return true if this is a pawn moving two squares"""
        return strip_piece(self.get_square(pos)) == PAWN and abs(pos[1] - new_pos[1]) == 2

    def get_promotion_piece(self, piece, promotion):
        """Return a new piece of type promotion w/ piece's attributes

        Assuming promotion in ['B', 'N', 'R', 'Q']"""
        colour = get_colour(piece)
        promotions = {'B': BISHOP | colour, 'N' : KNIGHT | colour,
                      'R' : ROOK | colour, 'Q': QUEEN | colour}
        return promotions[promotion]
        
    
    def in_checkmate(self, player):
        """Return True if the player is in checkmate, otherwise False"""
        for pos, target, _ in self.generate_all_possible_moves():
            piece = self.get_square(pos)
            if piece is None:
                raise Exception("Got a possible move that starts at an empty square")
            if get_colour(piece) == player and self.can_move_piece(pos, target) and not self.is_castle(pos, target):
                return False
        return True

    def perft(self, depth, prev_moves=[]):

        if depth == 0:
            return 1

        moves = self.generate_all_possible_moves()

        num_moves = 0
        for move in moves:
            info = self.move_piece(move)
            if info is None:
                print(f"unable to move piece which is said to be possible: {prev_moves + [move]}")
                print(self)
            else:
                dest, old_ep, old_cr = info
                num_moves += self.perft(depth-1, prev_moves + [move])
                self.unmove_piece(move, dest, old_ep, old_cr)

        return num_moves




        


if __name__ == "__main__":
    game = Game()
    ans = ""
    for i in range(7):
        print(f"at depth {i}: {game.perft(i)}")

