
import pygame as pg
from board import Game
import os
from util import get_piece_name, get_colour, EMPTY, get_real_index, BLACK, WHITE, PIECE_FILENAMES, count_value

pg.init()

directory = os.path.dirname(os.path.abspath(__file__))
GREEN = pg.Color(118, 150, 86)
CREAM = pg.Color(238,238,210)
WHITE_COLOUR = pg.Color(255,255,255)
BLACK_COLOUR = pg.Color(0,0,0)
BROWN = pg.Color(140,110,59)

GREY = pg.Color(220,220,220)
BLUE = pg.Color(0,76,153)

def get_piece_filename(piece):
    """assumes piece is a Piece instance"""
    piece_file = PIECE_FILENAMES[piece] +  ".png"
    return os.path.join(directory, "PIECES", piece_file)
    

class BoardView(pg.Surface):

    def __init__(self, dims, imgs, flags=pg.SRCALPHA):
        self.surface = pg.Surface(dims, flags)
        self.resize_board(dims)
        self.img_cache = imgs
        self.selected = None
        self.selected_possible_moves = None
        self.held = None

    def resize_board(self, size):
        self.surface = pg.Surface(size, pg.SRCALPHA)
        width, height = size
        self.square_dims = (width / 8, height / 8)
        self.square_width, self.square_height = self.square_dims

    def get_piece(self, row, col):
        """return the piece img at row and column"""
        return self.board[row][col]

    def draw_bg(self, size):
        pg.draw.rect(self.surface, WHITE, pg.Rect((0, 0), size))

    def make_board(self, board_obj):
        """draws the board and pieces onto the surface, where board is a 2D array of pieces"""
        rows, cols = 8, 8
        self.board = [[None]*cols for _ in range(rows)]
        for row in range(rows):
            y = row * self.square_height
            for col in range(cols):
                x = col * self.square_width
                square = board_obj.get_square(row*8 + col)
                self.draw_square(x, y, row, col)
                if square != EMPTY and not self.is_selected_piece(row, col):
                    self.draw_piece(square, x, y, row, col)

        self.draw_selected_piece(board_obj)

    def draw_square(self, x, y, row, col):

        color = CREAM if (row + col) % 2 == 0 else GREEN
        pg.draw.rect(self.surface, color, pg.Rect(x, y, self.square_width, self.square_height))

    def draw_selected_piece(self, board_obj):
        if self.selected is None:
            return 
        col, row = self.selected
        x, y = col * self.square_width, row * self.square_height
        s = pg.Surface(self.square_dims)
        s.set_alpha(64)
        s.fill(BLUE)
        self.surface.blit(s, (x,y))
        border = pg.Surface((self.square_width * 1.05, self.square_height * 1.05))
        rect = border.get_rect(center=(x + self.square_width / 2, y + self.square_height / 2))
        pg.draw.rect(self.surface, WHITE_COLOUR, rect, 5)
        self.draw_piece(board_obj.get_square(row*8 + col), x, y, row, col)


    def save_image(self, square, row, col):
        filepath = get_piece_filename(square)
        assert(filepath in self.img_cache.keys())
        img = self.img_cache[filepath]
        img = pg.transform.scale(img, self.square_dims)
        self.board[row][col] = img


    def draw_piece(self, square, x, y, row, col): 
        self.save_image(square, row, col)
        if (col, row) != self.held:
            self.surface.blit(self.get_piece(row, col), (x,y))

    def is_held_piece(self, row, col):
        return self.held is not None and self.held == (col, row)

    def is_selected_piece(self, row, col):
        return self.selected is not None and self.selected == (col, row)

    def update_selection(self, selected, board_obj):
        if selected is None:
            self.selected = selected
            return
        if selected is not None and selected != self.selected:
            self.selected = selected
            self.selected_possible_moves = board_obj.piece_legal_moves(get_real_index(self.selected))

    def show_possible_moves(self, board_obj: Game):
        if self.selected is None or self.selected_possible_moves is None or board_obj.is_empty(get_real_index(self.selected)):
            return
        for moveset in self.selected_possible_moves:
                _, coords, _ = moveset
                coords = (coords % 8, coords // 8) #convert back
                coords = ((coords[0]) * self.square_width + (self.square_width // 2),
                          (coords[1]) * self.square_width + (self.square_width // 2))
                pg.draw.circle(self.surface, GREY, coords, self.square_width // 5)

class StartScreen():

    def __init__(self, dims, flags=pg.SRCALPHA):
        self.surface = pg.Surface(dims, flags)
        self.width, self.height = dims
        self.logo = pg.image.load(os.path.join(directory, "Images", "logo.png"))

    def resize(self, size):
        self.surface = pg.Surface(size, pg.SRCALPHA)
        self.width, self.height = size

    def draw_bg(self, size):
        print(self.width, self.height)
        pg.draw.rect(self.surface, BROWN, pg.Rect((0, 0), (self.width, self.height)))


    def draw_logo(self):
        self.surface.blit(self.logo, ((self.width * 0.5) - (self.logo.get_width() * 0.5), self.height * 0.1))

    def draw_buttons(self):
        d = 25
        font = pg.font.Font(None, int(self.width * 0.04))
        title_font = pg.font.Font(None, 72)
        width, height = self.width // 6, self.height // 12

        title = title_font.render("Choose Your Side!", True, BLACK_COLOUR)
        title_rect = title.get_rect(center=(self.width // 2, self.height // 2))
        self.surface.blit(title, title_rect)


        x, y = (self.width * 0.5) - width - d , self.height * 0.65
        pg.draw.rect(self.surface, WHITE_COLOUR, pg.Rect(x, y, width, height), border_radius=20)
        text = font.render("WHITE", True, BLACK_COLOUR)
        text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
        self.surface.blit(text, text_rect)
        self.white_button_pos = (x, y)
        

        x = (self.width // 2)  + d
        pg.draw.rect(self.surface, BLACK_COLOUR, pg.Rect(x, y, width, height), border_radius=20)
        text = font.render("BLACK", True, WHITE_COLOUR)
        text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
        self.surface.blit(text, text_rect)
        self.black_button_pos = (x, y)

        self.button_width, self.button_height = width, height

    def get_colour_selection(self, pos):
        x, y = pos
        if x >= self.black_button_pos[0] and x <= self.black_button_pos[0] + self.button_width and y >= self.black_button_pos[1] and y <= self.black_button_pos[1] + self.button_height:
            return BLACK
        elif x >= self.white_button_pos[0] and x <= self.white_button_pos[0] + self.button_width and y >= self.white_button_pos[1] and y <= self.white_button_pos[1] + self.button_height:
            return WHITE
        else:
            return




class View():
    """composite class that instantiates all view objects + the game window"""
    def __init__(self):
        self.SCREEN_SIZE = (900, 900)
        self.BOARD_SIZE = min(self.SCREEN_SIZE) * 0.75
        self.BOARD_LOC = (self.SCREEN_SIZE[0] * 0.05, (self.SCREEN_SIZE[1] * 0.5) - (self.BOARD_SIZE * 0.5))
        self.window = pg.display.set_mode(self.SCREEN_SIZE, pg.RESIZABLE)

        self.img_cache = dict()
        for piece in PIECE_FILENAMES.keys():
            filename = get_piece_filename(piece)
            self.img_cache[filename] = pg.image.load(filename)

        self.start = StartScreen(self.SCREEN_SIZE)
        self.board = BoardView((self.BOARD_SIZE, self.BOARD_SIZE), imgs=self.img_cache) #board is half the size of screen

    def resize_board(self, screen_size):
        self.SCREEN_SIZE = screen_size
        self.BOARD_SIZE = min(screen_size) * 0.75
        self.BOARD_LOC = (screen_size[0] * 0.05, (screen_size[1] * 0.5) - (self.BOARD_SIZE * 0.5))
        self.start.resize(self.SCREEN_SIZE)
        self.board.resize_board((self.BOARD_SIZE, self.BOARD_SIZE))

    def draw_bg(self):
        pg.draw.rect(self.window, BROWN, pg.Rect((0, 0), self.SCREEN_SIZE))

    def update_screen(self):
        pg.display.update(pg.Rect((0, 0), self.SCREEN_SIZE))

    def clear(self):
        self.window.fill(BLACK_COLOUR)

    def show_start_screen(self):
        self.draw_bg()
        self.start.surface.fill((0,0,0,0))
        self.start.draw_buttons()
        self.start.draw_logo()
        self.window.blit(self.start.surface, (0, 0))

    def show_board(self, board_obj, selected=None, held=None):
        board = board_obj.board
        self.board.held = held
        self.draw_bg()
        self.start.surface.fill((0,0,0,0))
        self.board.update_selection(selected, board_obj)
        self.board.make_board(board_obj)
        self.board.show_possible_moves(board_obj)
        self.show_pieces_captured(board_obj)
        self.window.blit(self.board.surface, self.BOARD_LOC)


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

    def show_pieces_captured(self, board_obj):
        IMG_WIDTH, IMG_HEIGHT = 40, 40
        font = pg.font.Font(None, 36)
        white_pieces = board_obj.white_captured_list
        white_val = count_value(white_pieces)
        black_pieces = board_obj.black_captured_list
        black_val = count_value(black_pieces)
        val_diff = abs(white_val - black_val)

        for pieces in [white_pieces, black_pieces]:
            if pieces == black_pieces:
                x, y = self.BOARD_LOC[0], self.BOARD_LOC[1] + self.BOARD_SIZE + 10
            else:
                x, y = self.BOARD_LOC[0], self.BOARD_LOC[1] - 50
            prev_piece = None
            for piece in pieces:
                if prev_piece is not None:
                    if piece == prev_piece:
                        x += IMG_WIDTH * 0.5
                    else:
                        x += IMG_WIDTH * 0.7
                fn = get_piece_filename(piece)
                if fn in self.img_cache.keys():
                    img = self.img_cache[fn]
                    img = pg.transform.scale(img, (IMG_WIDTH, IMG_HEIGHT))
                else:
                    return
                self.window.blit(img, (x, y))
                prev_piece = piece

            val = count_value(pieces)
            if val >= white_val and val >= black_val and val_diff != 0:
                text = font.render(f"+{val_diff}", True, WHITE_COLOUR)
                text_rect = text.get_rect(center=(x + IMG_WIDTH // 2 + IMG_WIDTH, y + IMG_HEIGHT // 2))
                self.window.blit(text, text_rect)







