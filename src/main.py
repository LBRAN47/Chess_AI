from pygame.event import get
from board import Game, perft, show_split_perft
from parser import (parse_PGN, parse_move, parse_FEN)
from util import WHITE, BISHOP, KNIGHT, QUEEN, ROOK, get_real_index
import pygame as pg
from view import View
import argparse
import time
import subprocess

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
            view.update_screen()
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
                if moveset in board.generate_legal_moves(board.turn):
                    board.move_piece(moveset)
                print(board)

                if board.is_checkmate(board.turn):
                    board.change_turn()
                    print(f"CHECKMATE. {board.turn} wins")
                    break
                if board.is_stalemate(board.turn):
                    print(f"STALEMATE, Its a draw!")

class Main():

    def __init__(self, board, view, multiplayer=False):
        self.board = board
        self.view = view
        self.piece_held = None
        self.piece_selected = None
        self.piece_x = 0
        self.piece_y = 0
        self.promoting = False
        self.promoting_move = None
        self.in_checkmate = False
        self.player_colour = None
        self.multiplayer = multiplayer

        if not multiplayer:
            self.start_screen()
        self.game_loop()

    def start_screen(self):
        choice = None
        while choice is None:
            self.view.show_start_screen()
            self.view.update_screen()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    colour = self.view.start.get_colour_selection(event.pos)
                    if colour is not None:
                        self.player_colour = colour
                        return

    def game_loop(self):
        while True:


            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.left_click_handler(event)
                elif event.type == pg.MOUSEBUTTONUP:
                    self.left_click_up_handler(event)
                elif event.type == pg.MOUSEMOTION:
                    self.mouse_movement_handler(event)
                elif event.type == pg.KEYDOWN:
                    self.key_press_handler(event)


            if self.in_checkmate:
                quit()

            self.view.show_board(self.board, self.piece_selected, self.piece_held)

            if self.is_piece_held():
                self.view.show_held_piece(self.piece_x,
                                          self.piece_y,
                                          self.piece_held)


            self.view.update_screen()

            if not self.multiplayer and self.board.turn != self.player_colour:
                self.board.make_move_adversary()
            



    def is_piece_held(self):
        return False if self.piece_held is None else True
    
    def is_piece_selected(self):
        return False if self.piece_selected is None else True

    def key_press_handler(self, event):
        if not self.promoting:
            return
        key = event.key
        KEY_TO_PIECE = {pg.K_b : BISHOP, pg.K_r : ROOK, pg.K_k : KNIGHT, pg.K_q : QUEEN}
        if key in KEY_TO_PIECE.keys():
            piece = KEY_TO_PIECE[key] | self.board.turn
            self.move_piece(self.promoting_move, piece)
            self.promoting = False


    def left_click_handler(self, event):
        if self.promoting:
            return 
        x, y = event.pos
        target = self.view.get_piece_coords(x,y)
        if target is None:
            return
        if self.piece_selected and target != self.piece_selected:
            if self.board.legal_move(self.piece_selected, target):
                if self.board.is_promotion_move(get_real_index(target), self.board.get_square(get_real_index(self.piece_selected))):
                    self.promoting = True
                    self.promoting_move = target
                    return
                self.move_piece(target, NO_PROMOTION)
                return
            elif self.board.is_empty(get_real_index(target)):
                return
        coords = self.view.get_piece_coords(x,y)
        if coords is None:
            return
        self.piece_held = coords if not self.board.is_empty(get_real_index(coords)) else None
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
                if self.board.is_promotion_move(get_real_index(target), get_real_index(self.piece_selected)):
                    self.promoting = True
                    self.promoting_move = target
                    self.piece_held = None
                    return
                self.move_piece(target, NO_PROMOTION)
                return
        self.piece_held = None

    def move_piece(self, target, promotion_piece):
        moveset = (get_real_index(self.piece_selected), get_real_index(target), promotion_piece)
        self.board.move_piece(moveset)
        self.piece_selected = None
        self.piece_held = None
        if self.board.is_checkmate(self.board.turn):
            self.in_checkmate = True


#prepare subprocess for stockfish comparision
stockfish = subprocess.Popen([
    'stockfish'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    universal_newlines=True,
    bufsize=1)

def read():
    stockfish.stdin.write("isready\n")
    stockfish.stdin.flush()
    while True:
        line = stockfish.stdout.readline().strip()
        if line and line !="readyok":
            print(line)
        if line == "readyok":
            break

def drain():
    stockfish.stdin.write("isready\n")
    stockfish.stdin.flush()
    while True:
        line = stockfish.stdout.readline().strip()
        if line == "readyok":
            break

def main():
    cmd_parser = argparse.ArgumentParser() 
    cmd_parser.add_argument("--GUI", action="store_true", help="run GUI")
    cmd_parser.add_argument("--FEN", required=False, default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", help="provide the FEN")
    cmd_parser.add_argument("--mp", action="store_true", help="play against a friend")

    subparsers = cmd_parser.add_subparsers(dest="command", required=False)
    
    file_parser = subparsers.add_parser("file")
    file_parser.add_argument("file", default=None, help="specify a PGN file to run")

    perft_parse = subparsers.add_parser("perft")
    perft_parse.add_argument("--comp", action="store_true", help="run stockfish on same position and compare output")
    perft_parse.add_argument("--no_moves", action="store_true", help="hide number of moves in each submove")
    perft_parse.add_argument("depth", type=int, default=5, help="specify depth of perft search")

    args = cmd_parser.parse_args()

    if args.command == "perft":
        game = parse_FEN(args.FEN)
        if args.no_moves:
            start = time.time()
            num = perft(game, args.depth)
            end = time.time()
            secs = end - start
        else:
            start = time.time()
            num = show_split_perft(game, args.depth)
            end = time.time()
            secs = end - start
        print(f"perft1: number of moves at depth {args.depth} = {num} in {secs}s")
        

        if args.comp:
            drain()
            stockfish.stdin.write("position fen " + args.FEN + '\n')
            stockfish.stdin.flush()
            drain()
            stockfish.stdin.write("go perft " + str(args.depth) + '\n')
            read()
    else:
        view = View()
        board = parse_FEN(args.FEN)
        if args.GUI:
            if args.mp:
                Main(board, view, multiplayer=True)
            else:
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

if __name__ == "__main__":
    main()
