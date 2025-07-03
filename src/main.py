from board import Game
from parser import (parse_PGN, parse_move)
from util import WHITE
from view import View
import argparse
import pygame as pg


def game_loop(board, view, file=None):
    if file is not None:
        with open(file) as f:
            moves = parse_PGN(f.read())
        print(f"Generating game from {file}...")
        #print(f"\n{parser.headers['White']} vs. {parser.headers['Black']}\n")
        print("Press ENTER to show next move")
    while True:
            board.show_board()
            view.show_board(board, None)
            view.update_board()
            if file is None:
                move = input("Make a move: ")
            else:
                if len(moves) == 0:
                    if board.in_checkmate(board.turn):
                        board.change_turn()
                        print(f"CHECKMATE. {board.turn} wins")
                    else:
                        print("\nGame Over! The Game ends in a Draw")
                    break
                move = moves.pop(0)
                print(move)
                input() #wait for enter

            moveset = parse_move(move, board)
            if moveset is not None:
                info = board.move_piece(moveset)
                print(board)

                if board.in_checkmate(board.turn):
                    board.change_turn()
                    print(f"CHECKMATE. {board.turn} wins")
                    break

class Main():

    def __init__(self, board: Game, view: View):
        self.board = board
        self.view = view
        self.piece_held = None
        self.piece_selected = None
        self.piece_x = 0
        self.piece_y = 0
        clock = pg.time.Clock()
        while True:
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.left_click_handler(event)
                elif event.type == pg.MOUSEBUTTONUP:
                    self.left_click_up_handler(event)
                elif event.type == pg.MOUSEMOTION:
                    self.mouse_movement_handler(event)

            self.view.show_board(self.board, self.piece_selected, self.piece_held)

            if self.is_piece_held():
                self.view.show_held_piece(self.piece_x,
                                          self.piece_y,
                                          self.piece_held)

            self.view.update_board()
            clock.tick(100)
            
            if self.board.in_checkmate(self.board.turn):
                break



    def is_piece_held(self):
        return False if self.piece_held is None else True
    
    def is_piece_selected(self):
        return False if self.piece_selected is None else True


    def left_click_handler(self, event):
        x, y = event.pos
        target = self.view.get_piece_coords(x,y)
        if self.piece_selected and target != self.piece_selected:
            if self.board.legal_move(self.piece_selected, target):
                moveset = (self.piece_selected, target, None)
                self.board.move_piece(moveset)
                self.piece_selected = None
                self.piece_held = None
                return
            elif self.board.is_empty(target):
                return
        coords = self.view.get_piece_coords(x,y)
        self.piece_held = coords if not self.board.is_empty(coords) else None
        self.piece_selected = self.piece_held

    def mouse_movement_handler(self, event):
        self.piece_x, self.piece_y = event.pos


    def left_click_up_handler(self, event):
        if self.piece_held:
            x, y = event.pos
            target = self.view.get_piece_coords(x,y)
            if self.board.legal_move(self.piece_held, target):
                moveset = (self.piece_held, target, None)
                self.board.move_piece(moveset)
                self.piece_held = None
                self.piece_selected = None
                return
        self.piece_held = None
            




if __name__ == "__main__":
    cmd_parser = argparse.ArgumentParser() 
    cmd_parser.add_argument("file", nargs='?', default=None, help="specify a PGN file to run")
    cmd_parser.add_argument("--GUI", action="store_true", help="run GUI")
    args = cmd_parser.parse_args()
    view = View()
    board = Game()
    if args.GUI:
        Main(board, view)
    else:
        while True:
            game_loop(board, view, args.file)
            ans = input("Play Again? ")
            if ans not in ['y', 'Y', 'yes']:
                break
