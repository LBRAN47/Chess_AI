from pieces import (tuple_add, out_of_bounds, Pawn, Knight, Bishop, Rook, King, Queen)
from parser import Parser
import time
import random

WHITE = "WHITE"
BLACK = "BLACK"

class Board():

    def __init__(self, board=None, turn=WHITE, prev_piece=None, wkp=(4,0), bkp=(4,7)):
        if board is None:
            self.make_board()
        else:
            self.board = board
        self.turn = turn
        self.prev_piece = prev_piece
        self.black_king_pos = bkp
        self.white_king_pos = wkp

    def make_board(self):
        """Generate the starting chess board"""
        board = []
        for i in range(8):
            row = []
            if i == 0 or i == 7:
                colour = WHITE if i == 0 else BLACK
                row.append(Rook((0, i), colour))
                row.append(Knight((1, i), colour))
                row.append(Bishop((2, i), colour))
                row.append(Queen((3, i), colour))
                row.append(King((4, i), colour))
                row.append(Bishop((5, i), colour))
                row.append(Knight((6, i), colour))
                row.append(Rook((7, i), colour))
            elif i == 1 or i == 6:
                colour = WHITE if i == 1 else BLACK
                for j in range(8):
                    row.append(Pawn((j,i), colour))
            else:
                for j in range(8):
                    row.append(None)
            board.append(row)
        self.board = board

    def print_board(self):
        print()
        for row in range(7, -1, -1):
            row_string = f"{row+1} |"
            for col in range(8):
                if self.board[row][col] is None:
                    row_string += " "
                else:
                    row_string += str(self.board[row][col])
                row_string += "|"
            print(row_string)
        print("   a b c d e f g h")

    def get_square(self, position):
        """Return the piece at position, or None if no piece is at position"""
        if out_of_bounds(position):
            return None
        return self.board[position[1]][position[0]]

    def replace_square(self, position, piece):
        """replace the postiion in board with piece"""
        self.board[position[1]][position[0]] = piece
        return

    def change_turn(self):
        """Swap Turns"""
        self.turn = BLACK if self.turn == WHITE else WHITE

    def valid_move(self, pos, new_pos):
        """Return True if there is a piece at pos that can move legally to new_pos

        Move order is not considered"""
        piece = self.get_square(pos)
        new_square = self.get_square(new_pos)

        if piece is None:
            return False

        assert piece.position == pos

        if not piece.can_move(new_pos):
            return False


        if new_square is not None:
            if new_square.colour == piece.colour:
                return False
        
        if isinstance(piece, Pawn):
            delta = get_delta(pos, new_pos)

            if (delta[0] == 0 and new_square is not None):
                return False
            if (delta[0] != 0 and new_square is None):
                return self.is_valid_enpessant(pos, new_pos) 

        if isinstance(piece, Knight):
            return True
        
        delta = get_delta(pos, new_pos)
        ghost_pos = tuple_add(pos, delta)
        while ghost_pos != new_pos:
            square = self.get_square(ghost_pos)
            if square is not None:
                return False
            ghost_pos = tuple_add(ghost_pos, delta)

        return True

    def is_valid_enpessant(self, pos, new_pos):
        """Return True if we can capture enpessant"""
        #move diagonally
        delta = get_delta(pos, new_pos)
        piece = self.get_square(pos)
        if not isinstance(piece, Pawn):
            return False
        if not (new_pos in piece.get_possible_moves() and abs(delta[0]) == 1):
            return False
        #piece next to us (opposite colour)
        op_position = tuple_add(pos, (delta[0], 0))
        op_piece = self.get_square(op_position)
        if op_piece is None or op_piece.colour == piece.colour:
            return False
        #piece has just moved.
        if self.prev_piece != op_piece:
            return False
        return True

    def is_enpessant(self, pos, new_pos):
        """Return True if the move is an enpessant"""
        piece = self.get_square(pos)
        delta = get_delta(pos, new_pos)
        return isinstance(piece, Pawn) and abs(delta[0]) == 1 and self.get_square(new_pos) is None
        
    def is_castle(self, pos, new_pos):
        """Return True if the move is a castle"""
        piece = self.get_square(pos)
        return (isinstance(piece, King) and not piece.has_moved
        and (new_pos[0] - pos[0], new_pos[1] - pos[1]) in [(2,0), (-2,0)])

    def king_castle_valid(self, king, pos, new_pos):
        """Return True if this king can move from pos to new_pos, in a way that
        satisfies the rules of castling."""
        return (not self.in_check(king.colour)
                and self.get_square(new_pos) is None
                and self.valid_move(pos, new_pos))

    def is_valid_castle(self, king, pos, new_pos):
        """Return True if we can castle from pos to new_pos"""
        delta = get_delta(pos, new_pos)
        og_pos = pos

        rook_pos = (0, pos[1]) if new_pos[0] == 2 else (7, pos[1])
        rook = self.get_square(rook_pos)
        if rook is None or rook.has_moved or rook.colour != king.colour:
            return False
        while pos != new_pos:
            target = tuple_add(pos, delta)
            if not self.king_castle_valid(king, pos, target):
                self.backtrack(king, og_pos, pos, None)
                return False
            self.change_piece_position(pos, target)
            pos = target

        if self.in_check(king.colour):
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
                if piece is None:
                    continue
                if piece.colour != player:
                    if self.valid_move(piece.position, king_pos):
                        return True
        return False

    def can_move_piece(self, pos, new_pos):
        """Attempt to move the piece if legal"""

        piece = self.get_square(pos)
        dest  = self.get_square(new_pos) #save this
        
        if not self.valid_move(pos, new_pos):
            return False

        if piece.colour != self.turn:
            return False


        if self.is_castle(pos, new_pos):
            return self.is_valid_castle(piece, pos, new_pos)

        if self.is_enpessant(pos, new_pos):
            #remove the piece we are capturing!!
            op_position = tuple_add(pos, (get_delta(pos, new_pos)[0], 0))
            op_piece = self.get_square(op_position)
            self.replace_square(op_position, None)

        #Move the piece
        self.change_piece_position(pos, new_pos)

        if self.in_check(self.turn):
            #backtrack
            self.backtrack(piece, pos, new_pos, dest)
            if self.is_enpessant(pos, new_pos):
            #put the captured piece back
                self.replace_square(op_position, op_piece)
            return False
        
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
        piece.position = pos
        self.replace_square(pos, piece)
        self.replace_square(new_pos, dest)
        if isinstance(piece, King):
            if piece.colour == WHITE:
                self.white_king_pos = piece.position
            else:
                self.black_king_pos = piece.position


    def change_piece_position(self, pos, new_pos, promotion=None):
        """move the piece w/o changing the turn"""

        piece = self.get_square(pos)
        piece.position = new_pos
        self.replace_square(pos, None)
        if promotion is not None:
            piece = self.get_promotion_piece(piece, promotion)
        self.replace_square(new_pos, piece)
        if isinstance(piece, King):
            if piece.colour == WHITE:
                self.white_king_pos = piece.position
            else:
                self.black_king_pos = piece.position


    def move_piece(self, moveset):
        """if we can move, perform the moveset, updating the game state accordingly"""

        pos, new_pos, promotion = moveset

        if not self.can_move_piece(pos, new_pos):
            return
        
        if self.is_castle(pos, new_pos):
            cur_rook = (0, pos[1]) if new_pos[0] == 2 else (7, pos[1])
            target_rook = (3, pos[1]) if new_pos[0] == 2 else (5, pos[1])
            self.change_piece_position(cur_rook, target_rook)
            self.get_square(target_rook).move_piece(target_rook)

        if self.is_enpessant(pos, new_pos):
            #capture the piece
            op_position = tuple_add(pos, (get_delta(pos, new_pos)[0], 0))
            self.replace_square(op_position, None)

        self.change_piece_position(pos, new_pos, promotion)
        piece = self.get_square(new_pos)
        piece.move_piece(new_pos)
        self.prev_piece = piece
        self.change_turn()

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
                if piece is None:
                    continue
                pos = piece.position
                if piece.colour == player:
                    moves = piece.get_possible_moves()
                    for move in moves:
                        if self.can_move_piece(pos, move):
                            return False
        return True

    def get_pieces(self):
        """Returns a list of every piece in the board"""
        ret = []
        for i in range(8):
            for j in range(8):
                piece = self.get_square((i,j))
                if piece is not None:
                    ret.append(piece)
        return ret

    def get_possible_moves(self):
        moves = []
        for piece in self.get_pieces():
            if piece.colour == self.turn:
                position = piece.position
                for move in piece.get_possible_moves():
                    if self.can_move_piece(position, move):
                        moveset = (position, move, None)
                        moves.append(moveset)
        return moves



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


if __name__ == "__main__":
    board = Board()
    while True:
        moveset = random.choice(board.get_possible_moves())
        ans = board.move_piece(moveset)
        board.print_board()
        time.sleep(1)
