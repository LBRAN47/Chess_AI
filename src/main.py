from board import Game
from parser import (parse_PGN, parse_move, parse_FEN)
from util import WHITE, BISHOP, KNIGHT, QUEEN, ROOK
from view import View
import argparse
import pygame as pg
import time

KEY_TO_PIECE = {pg.K_b : BISHOP, pg.K_r : ROOK, pg.K_k : KNIGHT, pg.K_q : QUEEN}
NO_PROMOTION = None

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
                board.move_if_legal(moveset)
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
        self.promoting = False
        self.promoting_move = None
        self.in_checkmate = False

        self.game_loop()

    def game_loop(self):
        clock = pg.time.Clock()

        if self.board.in_check(self.board.turn):
            print("IN CHECKKKKKKK")
        while True:
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.left_click_handler(event)
                elif event.type == pg.MOUSEBUTTONUP:
                    self.left_click_up_handler(event)
                elif event.type == pg.MOUSEMOTION:
                    self.mouse_movement_handler(event)
                elif event.type == pg.KEYDOWN:
                    self.key_press_handler(event)

            self.view.show_board(self.board, self.piece_selected, self.piece_held)

            if self.is_piece_held():
                self.view.show_held_piece(self.piece_x,
                                          self.piece_y,
                                          self.piece_held)


            self.view.update_board()
            clock.tick(100)
            
            if self.in_checkmate:
                break



    def is_piece_held(self):
        return False if self.piece_held is None else True
    
    def is_piece_selected(self):
        return False if self.piece_selected is None else True

    def key_press_handler(self, event):
        if not self.promoting:
            return
        key = event.key
        if key in KEY_TO_PIECE.keys():
            piece = KEY_TO_PIECE[key] | self.board.turn
            self.move_piece(self.promoting_move, piece)
            self.promoting = False


    def left_click_handler(self, event):
        if self.promoting:
            return 
        x, y = event.pos
        target = self.view.get_piece_coords(x,y)
        if self.piece_selected and target != self.piece_selected:
            if self.board.legal_move(self.piece_selected, target):
                if self.board.is_promotion_move(target, self.board.get_square(self.piece_selected)):
                    self.promoting = True
                    self.promoting_move = target
                    return
                self.move_piece(target, NO_PROMOTION)
                return
            elif self.board.is_empty(target):
                return
        coords = self.view.get_piece_coords(x,y)
        self.piece_held = coords if not self.board.is_empty(coords) else None
        self.piece_selected = self.piece_held

    def mouse_movement_handler(self, event):
        self.piece_x, self.piece_y = event.pos


    def left_click_up_handler(self, event):
        if self.promoting:
            return
        if self.piece_held:
            x, y = event.pos
            target = self.view.get_piece_coords(x,y)
            if self.piece_selected and self.piece_selected != target and self.board.legal_move(self.piece_held, target):
                if self.board.is_promotion_move(target, self.board.get_square(self.piece_selected)):
                    self.promoting = True
                    self.promoting_move = target
                    self.piece_held = None
                    return
                self.move_piece(target, NO_PROMOTION)
                return
        self.piece_held = None

    def move_piece(self, target, promotion_piece):
        moveset = (self.piece_selected, target, promotion_piece)
        self.board.move_piece(moveset)
        self.piece_selected = None
        self.piece_held = None
        if self.board.in_checkmate(self.board.turn):
            self.in_checkmate = True
            




if __name__ == "__main__":
    cmd_parser = argparse.ArgumentParser() 
    cmd_parser.add_argument("--GUI", action="store_true", help="run GUI")
    cmd_parser.add_argument("--FEN", required=False, default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", help="provide the FEN")

    subparsers = cmd_parser.add_subparsers(dest="command", required=False)
    
    file_parser = subparsers.add_parser("file")
    file_parser.add_argument("file", default=None, help="specify a PGN file to run")

    perft = subparsers.add_parser("perft")
    perft.add_argument("--comp", help="textfile from stockfish to compare our output to")
    perft.add_argument("depth", type=int, default=5, help="specify depth of perft search")

    args = cmd_parser.parse_args()

    if args.command == "perft":
        game = parse_FEN(args.FEN)
        start = time.time()
        moves, num = game.show_split_perft(args.depth)
        end = time.time()
        print(f"number of moves at depth {args.depth} = {num} in {end - start}s")

        if args.comp is not None:
            with open(args.comp, 'r') as f:
                for line in f:
                    line = line[3:]
                    line = line.split()
                    if len(line) == 0:
                        continue
                    if line[0][-1] == ":":
                        move = line[0][:-1]
                        num = int(line[1])
                        if move in moves.keys() and moves[move] != num:
                            print(f"move {move} was said to have {moves[move]}, actually has {num}")
                            a, b, c = game.move_piece(move)
                            game.show_split_perft(args.depth - 1)
                            game.unmove_piece(move, a, b, c)
    else:
        view = View()
        board = parse_FEN(args.FEN)
        if args.GUI:
            Main(board, view)
        else:
            while True:
                if args.command == "file":
                    game_loop(board, view, args.file)
                else:
                    game_loop(board, view)
                ans = input("Play Again? ")
                if ans not in ['y', 'Y', 'yes']:
                    break
