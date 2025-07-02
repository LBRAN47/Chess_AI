from board import Board
from view import View
from parser import Parser
import argparse
import pygame as pg

def game_loop(board, view, file=None):
    parser = Parser()
    if file is not None:
        with open(file) as f:
            moves = parser.parse_PGN(f.read())
        print(f"Generating game from {file}...")
        print(f"\n{parser.headers['White']} vs. {parser.headers['Black']}\n")
        print("Press ENTER to show next move")
    while True:
            board.print_board()
            view.show_board(board, None)
            if file is None:
                print(f"Turn: {board.turn}")
                move = input("Make a move: ")
            else:
                if len(moves) == 0:
                    print("\nGame Over! The Game ends in a Draw")
                    break
                move = moves.pop(0)
                print(move)
                input() #wait for enter

            moveset = parser.parse_move(move, board)
            if moveset is not None:
                board.move_piece(moveset)

                if board.in_checkmate(board.turn):
                    board.change_turn()
                    print(f"CHECKMATE. {board.turn} wins")
                    break

class Main():

    def __init__(self, board, view):
        self.board = board
        self.view = view
        self.piece_held = None

        while True:
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.left_click_handler(event)

            view.show_board(self.board, self.piece_held)



    def left_click_handler(self, event):
        x, y = event.pos
        if self.piece_held:
            target = self.view.get_piece(x,y)
            if self.board.can_move_piece(self.piece_held, target):
                moveset = (self.piece_held, target, None)
                self.board.move_piece(moveset)
                self.piece_held = None
                return
        coords = self.view.get_piece(x,y)
        self.piece_held = coords if self.board.get_square(coords) is not None else None






if __name__ == "__main__":
    cmd_parser = argparse.ArgumentParser() 
    cmd_parser.add_argument("file", nargs='?', default=None, help="specify a PGN file to run")
    cmd_parser.add_argument("--GUI", action="store_true", help="run GUI")
    args = cmd_parser.parse_args()
    view = View()
    board = Board()
    if args.GUI:
        Main(board, view)
    else:
        while True:
            game_loop(board, view, args.file)
            ans = input("Play Again? ")
            if ans not in ['y', 'Y', 'yes']:
                break
