
import pygame as pg
import os

directory = os.path.dirname(os.path.abspath(__file__))
GREEN = (118, 150, 86)
CREAM = (238,238,210)
WHITE = (255,255,255)

BLUE = pg.Color(0,76,153)
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
        self.selected = None

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

        if self.is_selected_piece(row, col):
            s = pg.Surface(self.square_dims)
            s.set_alpha(64)
            s.fill(BLUE)
            self.blit(s, (x,y))
            pg.draw.rect(self, WHITE, pg.Rect(x, y, self.square_width, self.square_height), 5)

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

    def is_selected_piece(self, row, col):
        return self.selected is not None and self.selected == (col, row)

class View():
    """composite class that instantiates all view objects + the game window"""
    def __init__(self):
        self.SCREEN_SIZE = (900, 900)
        self.BOARD_LOC = (self.SCREEN_SIZE[0] * 0.05, self.SCREEN_SIZE[1] * 0.05) 
        self.BOARD_SIZE = self.SCREEN_SIZE[0] * 0.75
        self.window = pg.display.set_mode(self.SCREEN_SIZE)
        self.board = BoardView((self.BOARD_SIZE, self.BOARD_SIZE)) #board is half the size of screen

    def show_board(self, board, selected):
        self.board.selected = selected
        self.board.make_board(board)
        self.window.blit(self.board, self.BOARD_LOC)
        pg.display.flip()

    def get_piece(self, x, y):
        if x < self.BOARD_LOC[0] or x > self.BOARD_LOC[0] + self.BOARD_SIZE:
            return None

        if y < self.BOARD_LOC[1] or x > self.BOARD_LOC[1] + self.BOARD_SIZE:
            return None

        x = (x - self.BOARD_LOC[0]) // (self.BOARD_SIZE // 8)
        y = 7 - (y - self.BOARD_LOC[1]) // (self.BOARD_SIZE // 8)
        
        return (int(x), int(y))



