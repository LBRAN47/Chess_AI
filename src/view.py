
import pygame as pg
from board import Game
import os
from util import get_piece_name, get_colour, EMPTY 

directory = os.path.dirname(os.path.abspath(__file__))
GREEN = pg.Color(118, 150, 86)
CREAM = pg.Color(238,238,210)
WHITE = pg.Color(255,255,255)
BLACK = pg.Color(0,0,0)

GREY = pg.Color(220,220,220)
BLUE = pg.Color(0,76,153)

def get_piece_filename(piece):
    """assumes piece is a Piece instance"""
    piece_file = get_piece_name(piece) +  ".png"
    return os.path.join(directory, "PIECES", piece_file)
    

class BoardView(pg.Surface):

    def __init__(self, dims, flags=0):
        super().__init__(dims, flags)
        width, height = dims
        self.square_dims = (width // 8, height // 8)
        self.square_width, self.square_height = self.square_dims
        self.img_cache = {}
        self.selected = None
        self.held = None

    def get_piece(self, row, col):
        """return the piece img at row and column"""
        return self.board[row][col]

    def make_board(self, board):
        """draws the board and pieces onto the surface, where board is a 2D array of pieces"""
        rows, cols = 8, 8
        self.board = [[None]*cols for _ in range(rows)]
        for row in range(rows):
            y = row * self.square_height
            for col in range(cols):
                x = col * self.square_width
                square = board[row][col]
                self.draw_square(x, y, row, col)
                if square != EMPTY:
                    self.draw_piece(square, x, y, row, col)

    def draw_square(self, x, y, row, col):

        color = CREAM if (row + col) % 2 == 0 else GREEN
        pg.draw.rect(self, color, pg.Rect(x, y, self.square_width, self.square_height))

        if self.is_selected_piece(row, col):
            s = pg.Surface(self.square_dims)
            s.set_alpha(64)
            s.fill(BLUE)
            self.blit(s, (x,y))
            pg.draw.rect(self, WHITE, pg.Rect(x, y, self.square_width, self.square_height), 5)

    def save_image(self, square, row, col):
        filepath = get_piece_filename(square)
        if filepath in self.img_cache.keys():
            img = self.img_cache[filepath]
        else:
            img = pg.image.load(get_piece_filename(square))
            img = pg.transform.scale(img, self.square_dims)
            self.img_cache[filepath] = img
        self.board[row][col] = img


    def draw_piece(self, square, x, y, row, col): 
        self.save_image(square, row, col)
        if (col, row) != self.held:
            self.blit(self.get_piece(row, col), (x,y))

    def is_held_piece(self, row, col):
        return self.held is not None and self.held == (col, row)

    def is_selected_piece(self, row, col):
        return self.selected is not None and self.selected == (col, row)

    def show_possible_moves(self, board_obj: Game):
        if self.selected is None or board_obj.is_empty(self.selected):
            return
        for moveset in board_obj.generate_legal_moves(self.selected):
                _, coords, _ = moveset
                coords = ((coords[0]) * self.square_width + (self.square_width // 2),
                          (coords[1]) * self.square_width + (self.square_width // 2))
                pg.draw.circle(self, GREY, coords, self.square_width // 5)

class View():
    """composite class that instantiates all view objects + the game window"""
    def __init__(self):
        self.SCREEN_SIZE = (900, 900)
        self.BOARD_LOC = (self.SCREEN_SIZE[0] * 0.05, self.SCREEN_SIZE[1] * 0.05) 
        self.BOARD_SIZE = min(self.SCREEN_SIZE) * 0.75
        self.window = pg.display.set_mode(self.SCREEN_SIZE)
        self.board = BoardView((self.BOARD_SIZE, self.BOARD_SIZE)) #board is half the size of screen

    def update_board(self):
        pg.display.update(pg.Rect(self.BOARD_LOC, (self.BOARD_SIZE, self.BOARD_SIZE)))

    def clear(self):
        self.window.fill(BLACK)

    def show_board(self, board_obj, selected=None, held=None):
        board = board_obj.board
        self.board.held = held
        self.board.selected = selected
        self.board.make_board(board)
        self.board.show_possible_moves(board_obj)
        self.window.blit(self.board, self.BOARD_LOC)


    def show_held_piece(self, x, y, piece_held):
        col, row = piece_held
        piece = self.board.get_piece(row, col)
        if piece is None:
            return
        x = x - (self.board.square_width // 2)
        y = y - (self.board.square_height // 2)
        self.window.blit(piece, (x, y))

    def get_piece(self, x, y):
        coords = self.get_piece_coords(x,y)
        if coords is None:
            return
        col, row = coords
        return self.board.get_piece(row, col)

    def get_piece_coords(self, x, y):
        """return board coordinates based on x and y"""
        if x < self.BOARD_LOC[0] or x > self.BOARD_LOC[0] + self.BOARD_SIZE:
            return None

        if y < self.BOARD_LOC[1] or x > self.BOARD_LOC[1] + self.BOARD_SIZE:
            return None

        x = (x - self.BOARD_LOC[0]) // (self.BOARD_SIZE // 8)
        y = (y - self.BOARD_LOC[1]) // (self.BOARD_SIZE // 8)
        
        return (int(x), int(y))



