
import pygame as pg
import os

directory = os.path.dirname(os.path.abspath(__file__))
GREEN = (118, 150, 86)
CREAM = (238,238,210)

def get_piece_filename(piece):
    """assumes piece is a Piece instance"""
    piece_file = str(piece) + piece.colour + ".png"
    return os.path.join(directory, "PIECES", piece_file)
    

class BoardView(pg.Surface):

    def __init__(self, dims, flags=0):
        super().__init__(dims, flags)
        width, height = dims
        self.square_dims = (width // 8, height // 8)
        self.square_width, self.square_height = self.square_dims
        self.img_cache = {}

    def make_board(self, board):
        """draws the board and pieces onto the surface, where board is a 2D array of pieces"""
        rows, cols = len(board), len(board[0])
        self.board = [[None]*cols for _ in range(rows)]
        for row in range(rows):
            y = row * self.square_height
            row = 7 - row #ensuring we print rows in the correct order
            for col in range(cols):
                x = col * self.square_width
                square = board[row][col]
                self.draw_square(x, y, row, col)
                self.draw_piece(square, x, y, row, col)

    def draw_square(self, x, y, row, col):
        color = CREAM if (row + col) % 2 == 0 else GREEN
        pg.draw.rect(self, color, pg.Rect(x, y, self.square_width, self.square_height))

    def draw_piece(self, square, x, y, row, col): 
        if square is None:
            return None
        filepath = get_piece_filename(square)
        if filepath in self.img_cache.keys():
            img = self.img_cache[filepath]
        else:
            img = pg.image.load(get_piece_filename(square))
            img = pg.transform.scale(img, self.square_dims)
            self.img_cache[filepath] = img
        self.blit(img, (x,y))
        self.board[row][col] = img

