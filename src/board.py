from pieces import (Pawn, Knight, Bishop, Rook, King, Queen)
import time
from util import (START_BOARD, WHITE, BLACK, PAWN, BISHOP, KNIGHT, ROOK, QUEEN, KING,
                  WHITE_Q_CASTLE, WHITE_K_CASTLE, BLACK_K_CASTLE, BLACK_Q_CASTLE,
                  Coordinate, ListBoard, Piece, ALL, coordinate_to_square, INV_PIECES,
                  EMPTY, get_colour, get_piece_name, strip_piece, tuple_add, tuple_diff, out_of_bounds,
                  WHITE_PAWN, BLACK_PAWN, WHITE_KING, BLACK_KING, get_delta, WHITE_KING_START, BLACK_KING_START)

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


    def show_board(self):
        ans = ""
        for row in range(8):
            row_string = f"{abs(row - 8)} |"
            for col in range(8):
                square = self.board.get(col, row)
                if square == EMPTY:
                    row_string += " "
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



    def get_square(self, position: Coordinate):
        """Return the piece at position, or None if no piece is at position"""
        if out_of_bounds(position):
            return None
        return self.board.get(position)

    def replace_square(self, position: Coordinate, piece: Piece):
        """replace the postiion in board with piece"""
        self.board.set(piece, position)
        return

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

    def update_castle_rights(self, pos, new_pos):
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
            self.castling &= (15 - castle)
        elif strip_piece(piece) == KING:
            if get_colour(piece) == WHITE:
                self.castling &= BLACK_K_CASTLE | BLACK_Q_CASTLE
            elif get_colour(piece) == BLACK:
                self.castling &= WHITE_K_CASTLE | WHITE_Q_CASTLE
            



    def generate_moves(self, position: Coordinate) -> list[Coordinate]:
        """generate possible moves for the piece at position."""
        piece = self.board.get(position)
        if piece == EMPTY:
            return []

        if piece == WHITE_PAWN:
            moves = [tuple_add(position, delta) for delta in [(-1, -1), (0,-1), (0,-2), (1,-1)]]
        elif piece == BLACK_PAWN:
            moves = [tuple_add(position, delta) for delta in [(-1, 1), (0,1), (0,2), (1,1)]]
        elif strip_piece(piece) == KNIGHT:
            deltas = [-2, -1, 1, 2]
            moves = [tuple_add(position, (x,y)) for x in deltas
                                                    for y in deltas
                                                    if abs(x) != abs(y)]
        elif strip_piece(piece) in [BISHOP, ROOK, QUEEN]: #sliders
            bishop_deltas = [(1,1), (1,-1), (-1, 1), (-1,-1)]
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
                    moves.append(move)
                    move = tuple_add(move, delta)
                move = position
        elif strip_piece(piece) == KING:
            deltas = [(x,y) for x in [1, 0, -1] for y in [1, 0, -1] if not (x==0 and y==0)]
            deltas = deltas + [(-2, 0), (2,0)] #castling is a king move
            moves = [tuple_add(position, delta) for delta in deltas]
        else:
            raise ValueError(f"invalid piece: {piece} at position {position}")

        return [move for move in moves if self.valid_move(position, move)]


    def valid_move(self, pos, new_pos):
        """Return True if there is a piece at pos that can move legally to new_pos

        Move order is not considered"""
        piece = self.get_square(pos)
        new_square = self.get_square(new_pos)

        if piece is None or new_square is None: #oob
            return False

        if piece == EMPTY:
            return False

        if new_square != EMPTY:
            if get_colour(new_square) == get_colour(piece):
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
        return (strip_piece(piece) == KING and self.right_to_castle(pos, new_pos)
        and tuple_diff(pos, new_pos) in [(2,0), (-2,0)])

    def king_castle_valid(self, king, pos, new_pos):
        """Return True if this king can move from pos to new_pos, in a way that
        satisfies the rules of castling."""
        return (not self.in_check(get_colour(king))
                and self.get_square(new_pos) == EMPTY
                and self.valid_move(pos, new_pos))

    def is_valid_castle(self, king, pos, new_pos):
        """Return True if we can castle from pos to new_pos"""
        delta = get_delta(pos, new_pos)
        og_pos = pos

        rook_pos = (0, pos[1]) if new_pos[0] == 2 else (7, pos[1])
        rook = self.get_square(rook_pos)
        if rook == EMPTY or get_colour(rook) != get_colour(king):
            return False
        while pos != new_pos:
            target = tuple_add(pos, delta)
            if not self.king_castle_valid(king, pos, target):
                self.backtrack(king, og_pos, pos, None)
                return False
            self.change_piece_position(pos, target)
            pos = target

        if self.in_check(get_colour(king)):
            self.backtrack(king, og_pos, pos, None)
            return False

        self.backtrack(king, og_pos, pos, None)
        return True


    def in_check(self, player):
        """return True if the player is in check, otherwise False

        Where player is either 'WHITE' or 'BLACK' """

        king_pos = self.black_king_pos if player == BLACK else self.white_king_pos
        for row in range(8):
            for collumn in range(8):
                piece = self.get_square((collumn, row))
                if piece == EMPTY or piece is None:
                    continue
                if get_colour(piece) != player:
                    if self.valid_move((collumn, row), king_pos):
                        print(f"the checking move is coming from {(collumn, row)} attacking {king_pos}")
                        return True
        return False

    def can_move_piece(self, pos, new_pos):
        """Attempt to move the piece if legal"""
        if not (self.valid_move(pos, new_pos) and self.turn == get_colour(self.get_square(pos))):
            return False

        piece = self.get_square(pos)
        dest  = self.get_square(new_pos) #save this
        
        if self.is_castle(pos, new_pos):
            return self.is_valid_castle(piece, pos, new_pos)


        if self.is_enpessant(pos, new_pos):
            #remove the piece we are capturing!!
            op_position = tuple_add(pos, (get_delta(pos, new_pos)[0], 0))
            op_piece = self.get_square(op_position)
            self.replace_square(op_position, EMPTY)

        #Move the piece
        self.change_piece_position(pos, new_pos)

        print()
        print("THE BOARD IF THE MOVE WAS PLAYED")
        print(self.board.board)
        print(self)
        print()


        if self.in_check(self.turn):
            print("in check after this!!!")
            #backtrack
            self.backtrack(piece, pos, new_pos, dest)
            if self.is_enpessant(pos, new_pos):
            #put the captured piece back
                self.replace_square(op_position, op_piece)
            return False
        print("not in check: returning to old board")
        
        self.backtrack(piece, pos, new_pos, dest)

        if self.is_enpessant(pos, new_pos):
            #put the captured piece back
            self.replace_square(op_position, op_piece)

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

        if not self.can_move_piece(pos, new_pos):
            print("cannot move piece")
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
            self.update_castle_rights(pos, new_pos)

        self.change_piece_position(pos, new_pos, promotion)
        self.change_turn()

    def is_double_pawn_move(self, pos, new_pos):
        """Return true if this is a pawn moving two squares"""
        return strip_piece(self.get_square(pos)) == PAWN and abs(pos[1] - new_pos[1]) == 2

    def get_promotion_piece(self, piece, promotion):
        """Return a new piece of type promotion w/ piece's attributes

        Assuming promotion in ['B', 'N', 'R', 'Q']"""
        pos = piece.position
        colour = piece.colour
        promotions = {'B': Bishop(pos, colour), 'N' : Knight(pos, colour),
                      'R' : Rook(pos, colour), 'Q': Queen(pos, colour)}
        return promotions[promotion]
        
    
    def in_checkmate(self, player):
        """Return True if the player is in checkmate, otherwise False"""
        if not self.in_check(player):
            return False
        
        for row in range(8):
            for collumn in range(8):
                piece = self.get_square((collumn, row))
                if piece == EMPTY or piece is None:
                    continue
                pos = (collumn, row)
                if get_colour(piece) == player:
                    moves = self.generate_moves(pos)
                    for move in moves:
                        if self.can_move_piece(pos, move):
                            return False
        return True


if __name__ == "__main__":
    game = Game()
    for col in range(8):
        for row in range(8):
            pos = (col, row)
            if game.board.get(pos) == EMPTY:
                continue
            print(pos)
            moves = game.generate_moves(pos)
            #make into recognisable words
            start = get_piece_name(game.board.get(pos))
            pos = coordinate_to_square(pos)
            moves = [coordinate_to_square(p) for p in moves]
            print(f"piece {start} at square {pos} can move to {moves}")
