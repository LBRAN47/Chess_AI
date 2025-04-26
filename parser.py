from pieces import Pawn

        
        

class Parser():
    """Convert Chess Notation into usable board Coordinates"""


    def __init__(self):
        self.PIECES  = ['B', 'N', 'R', 'Q', 'K']
        self.COLUMNS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        self.ROWS    = [1, 2, 3, 4, 5, 6, 7, 8]
        self.COLUMN_CONVERT = dict(zip(self.COLUMNS, map(lambda x : x-1, self.ROWS)))


    def parse_PGN(self, pgn):
        """Given a string of a PGN (Portable Game Notation) file, return a list
        of parsable moves"""
        MOVE_START_SET = self.PIECES + self.COLUMNS + ["O"]
        idx = 0

        #skip headers
        while pgn[idx] == '[':
            idx += 1
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

        return moves

    def convert_coordinate(self, coord):
        """Convert from Chess Coordinate to tuple"""

        if len(coord) != 2:
            print("Invalid Coordinate")
            return
        col = coord[0]
        try:
            row = int(coord[1])
        except ValueError:
            print("ValueError")
            return
        if col not in self.COLUMNS or row not in self.ROWS:
            print("Invalid Coordinate")
            return
        return (self.COLUMN_CONVERT[col], row-1)


    def parse_move(self, move, board):
        """Convert a move in Chess Notation into the form used by the board

        parameters:
            move : String in the form of Standard Chess Notation
            board: Instance of the class Board

        Returns: two sets of coordinates, the first being the square to move from
        and the second to move to."""
        

        move = move.strip("+#")

        if move == "":
            print("empty move")
            return

        if len(move) < 2:
            print(f"invalid notation {move}")
            return

        if move[0] == '0' or move[0] == 'O':
            return self.parse_castle(move, board)

        if move[0] in self.COLUMNS:
            return self.parse_pawn(move, board)

        elif move[0] in self.PIECES: #Basic Move
            if len(move) < 3:
                print(f"invalid length notation {move}")
                return
            piece_str, move = move[0], move[1:] #cut off processed characters
            row, col = None, None
            if move[0].isdigit() and int(move[0]) in self.ROWS:
                row, move = int(move[0]) - 1, move[1:] 
            elif move[0] in self.COLUMNS:
                col, move = self.COLUMN_CONVERT[move[0]], move[1:]
                if move[0].isdigit() and int(move[0]) in self.ROWS:
                    row, move = int(move[0]) - 1, move[1:]
                    if len(move) == 0:
                        return self.get_moveset(piece_str, (col, row), board)
                    else:
                        print(f"Invalid trailing characters: {move}")
                        return

            if len(move) != 0 and move[0] == 'x':
                move = move[1:]

            start_coords = col, row

            if len(move) < 2:
                print("invalid length notation")
                return
            if move[0] not in self.COLUMNS:
                print("Invalid Notation: incorrect coordinate")
                return
            target_col = self.COLUMN_CONVERT[move[0]]
            try:
                target_row = int(move[1])
            except ValueError:
                print("Expected number in move")
                return
            if target_row not in self.ROWS:
                print("Invalid Notation: incorrect coordinate")
                return

            move = move[2:]
            target_coords = (target_col, target_row - 1)
            if len(move) == 0:
                return self.get_moveset(piece_str, target_coords, board, start_coords)
            else:
                print(f"Invalid trailing characters: {move}")
                return


    def parse_castle(self, move, board):
        """Return the castling moveset represented by move"""
        row = 0 if board.turn == "WHITE" else 7
        if move in ['0-0', 'O-O']: #short castle
            return ((4,row), (6,row), None)
        elif move in ['0-0-0', 'O-O-O']: #long castle
            return ((4,row), (2,row), None)
        else:
            print("invalid move: did you mean castle?")
            


        
    def parse_pawn(self, move, board):
        """Parse a pawn move.

        Given we know the string starts with a letter from a-h, and the length
        of move is >= 2"""
        ans = None
        start_col = self.COLUMN_CONVERT[move[0]]
        if move[1] == 'x': #Capture
            if len(move) < 4:
                print(f"invalid notation {move}")
                return
            ending_square = self.convert_coordinate(move[2:4])
            candidate_squares = [(start_col, ending_square[1]+1), (start_col, ending_square[1]-1)]
            for coord in candidate_squares:
                if board.try_move_piece(coord, ending_square):
                    ans = (coord, ending_square, None)
                    break
            if ans is None:
                print(f"No valid move in Board for {move}")
                return
            if len(move) == 4:
                return ans
            valid_length = 6
        else:
            ending_square = self.convert_coordinate(move)
            if ending_square is None:
                return
            for i in [-2, -1, 1, 2]:
                coord = (start_col, ending_square[1]+i)
                if not isinstance(board.get_square(coord), Pawn):
                    continue
                if board.try_move_piece(coord, ending_square):
                    ans =  (coord, ending_square, None)
            if ans is None:
                print(f"No valid move in Board for {move}")
                return
            if len(move) == 2:
                return ans
            valid_length = 4

        if len(move) == valid_length:
            promotion, piece = move[-2:] #e.g '=Q'
            if promotion != '=' or piece not in self.PIECES or piece == 'K':
                print(f"Invalid Promotion: {move}")
                return
            if ending_square[1] != 0 and ending_square[1] != 7:
                print(f"Invalid Promotion: {move}")
                return
            return (ans[0], ans[1], piece)
        else:
            print(f"Invalid Length: {move}")
            return
                

    def get_moveset(self, piece_str, target_coords, board, start_coords=None):
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
                if square is None:
                    continue
                if str(square) == piece_str and board.try_move_piece((col, row), target_coords):
                    if moveset is not None:
                        print("Insufficient disambiguation")
                        return
                    moveset = ((col, row), target_coords, None)
                if start_col is not None: #only check this collumn
                    break
            if start_row is not None: #only check this row
                break
        if moveset is None:
                print(f"no piece {piece_str} at starting coordinates {start_coords}")
        return moveset

if __name__ == "__main__":
    parser = Parser()
    with open("file.pgn") as f:
        print(parser.parse_PGN(f.read()))
