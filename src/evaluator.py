from pieces import tuple_add
from board import Board

WHITE = "WHITE"
BLACK = "BLACK"
class Evaluator():

    def evaluate(self, board: Board):
        """board is an instance of the Board class. Returns the heuristic for this position"""
        evaluation = 0

        values = {"P" : 100, "N" : 300, "B" : 300, "R" : 500, "Q" : 900, "K" : 0}
        colours = {WHITE: 1, BLACK: -1}
        for piece in board.get_pieces():
            value = values[str(piece)] * colours[piece.colour]
            evaluation += value

        return evaluation

    def eval_minmax(self, board: Board, depth=4):
        player = board.turn
        if depth == 0 or board.in_checkmate(board.turn):
            return self.evaluate(board)

        if player == "WHITE":
            maxEval = -float('inf')
            for moveset in board.get_possible_moves():
                state = copy_board(board)
                state.move_piece(moveset)
                eval = self.eval_minmax(state, depth-1)
                maxEval = max(maxEval, eval)
            return maxEval
        else:
            minEval = float('inf')
            for moveset in board.get_possible_moves():
                state = copy_board(board)
                state.move_piece(moveset)
                eval = self.eval_minmax(state, depth-1)
                minEval = min(minEval, eval)
            return minEval





def copy_board(board: Board) -> Board:
    """creates a replica board instance"""
    return Board(board.board, board.turn, board.prev_piece, board.white_king_pos, board.black_king_pos)
