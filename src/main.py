from board import Game
from parser import (parse_PGN, parse_move)
from util import WHITE
import argparse


def game_loop(board, file=None):
    if file is not None:
        with open(file) as f:
            moves = parse_PGN(f.read())
        print(f"Generating game from {file}...")
        #print(f"\n{parser.headers['White']} vs. {parser.headers['Black']}\n")
        print("Press ENTER to show next move")
    while True:
            print(board)
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
                if info is None:
                    continue
                np, old_ep, old_cr = info
                print(board)
                board.unmove_piece(moveset, np, old_ep, old_cr)
                print("\nundo...")
                print(board)
                board.move_piece(moveset)
                if board.in_checkmate(board.turn):
                    board.change_turn()
                    print(f"CHECKMATE. {board.turn} wins")
                    break

if __name__ == "__main__":
    cmd_parser = argparse.ArgumentParser() 
    cmd_parser.add_argument("file", nargs='?', default=None, help="specify a PGN file to run")
    args = cmd_parser.parse_args()
    while True:
        board = Game()
        game_loop(board, args.file)
        ans = input("Play Again? ")
        if ans not in ['y', 'Y', 'yes']:
            break
