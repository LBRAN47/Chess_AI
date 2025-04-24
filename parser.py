
class Parser():
    """Convert Chess Notation into usable board Coordinates"""


    def __init__(self):
        self.COLUMNS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        self.ROWS    = [1, 2, 3, 4, 5, 6, 7, 8]
        self.COLUMN_CONVERT = dict(zip(self.COLUMNS, map(lambda x : x-1, self.ROWS)))

    def convert_coordinate(self, coord):
        """Convert from Chess Coordinate to tuple"""
        if len(coord) != 2:
            print("Invalid Coordinate")
            return
        col = coord[0]
        try:
            row = int(coord[1]) - 1
        except ValueError:
            print("ValueError")
            return
        if col not in self.COLUMNS or row not in self.ROWS:
            print("Invalid Coordinate")
            return
        return (self.COLUMN_CONVERT[col], row)


    def parse_move(self, move, board):
        """Convert a move in Chess Notation into the form used by the board

        parameters:
            move : String in the form of Standard Chess Notation

        Returns: two sets of coordinates, the first being the square to move from
        and the second to move to."""

        if move == "":
            print("empty move")
            return

        if move[0] in self.COLUMNS:
            return self.parse_pawn(move, board)
        
    def parse_pawn(self, move, board):
        """Parse a pawn move.

        Given we know the string starts with a letter from a-h"""
        if len(move) < 2:
            print(f"invalid notation {move}")
            return
        start_col = self.COLUMN_CONVERT[move[0]]
        if move[1] == 'x':
            if len(move) != 4:
                print(f"invalid notation {move}")
                return
            ending_square = self.convert_coordinate(move[2:])
            candidate_squares = [(start_col, ending_square[1]+1), (start_col, ending_square[1]-1)]
            for coord in candidate_squares:
                square = board.get_square(coord)
                if square is None:
                    continue
                if square.colour == board.turn and square.can_move(ending_square):
                    return coord, ending_square
            print(f"No valid move in Board for {move}")
            return
        else:
            if len(move) != 2:
                print(f"invalid notation {move}")
                return
            ending_square = self.convert_coordinate(move)
            for i in [-2, -1, 1, 2]:
                coord = (start_col, ending_square[1]+i)
                if board.try_move_piece(coord, ending_square):
                    return coord, ending_square
                

            



            
        




