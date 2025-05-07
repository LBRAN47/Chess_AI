import pygame as pg

pg.init()

window = pg.display.set_mode((200, 200))
r = pg.Rect(100, 100, 50, 50)
pg.draw.rect(window, "blue", r)
white_king = pg.image.load("PIECES/KW.png")
window.blit(white_king, (100, 100))
pg.display.update()
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.WINDOWCLOSE:
            running = False