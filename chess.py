class Piece:

    def __init__(self, position, colour):
        self.position = position
        self.colour = colour

    def move_piece(self, new_position):
        self.position = new_position




class Knight(Piece):
    pass


class Rook(Piece):

    def __init__(self, position, colour):
        super().__init__(position, colour)

    def move_piece(self, new_position):
        difference = (new_position[0] - self.position[0], new_position[1] - self.position[1])
        if difference[0] == 0 or difference[1] == 0:
            print("This move is valid!!!")
            self.position = new_position
        else:
            print("This move is invalid")




my_piece = Piece((2, 4), "White")

print(f" first position: {my_piece.position}")
my_piece.move_piece((3, 4))
print(f" new position: {my_piece.position}")

rook = Rook((0, 0), "White")
print(rook.position, rook.colour)

