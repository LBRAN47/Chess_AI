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
            view.show_board(board.board)
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

if __name__ == "__main__":
    cmd_parser = argparse.ArgumentParser() 
    cmd_parser.add_argument("file", nargs='?', default=None, help="specify a PGN file to run")
    args = cmd_parser.parse_args()
    view = View()
    while True:
        board = Board()
        game_loop(board, view, args.file)
        ans = input("Play Again? ")
        if ans not in ['y', 'Y', 'yes']:
            break
