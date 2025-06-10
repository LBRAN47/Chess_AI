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

