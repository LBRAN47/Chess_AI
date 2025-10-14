import enum
import unittest
from parser import parse_FEN, board_to_FEN
from board import Game, WHITE, BLACK, EMPTY, PAWN, KNIGHT, KING, QUEEN, perft
from eval import evaluate_board

class BaseTest(unittest.TestCase):

    def setUp(self):
        # Standard starting position
        self.start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.game = parse_FEN(self.start_fen)

    def test_initial_board_setup(self):
        # Check turn
        self.assertEqual(self.game.turn, WHITE)
        # Check white pawns
        for i in range(8, 16):
            self.assertEqual(self.game.get_square(i), PAWN)
        # Check white king
        self.assertTrue(self.game.white_king > -1)
        # Check black king
        self.assertTrue(self.game.black_king > -1)
        # check eval is equal 
        self.assertTrue(evaluate_board(self.game) == 0)

    def test_fen_roundtrip(self):
        # Convert back to FEN
        fen_back = board_to_FEN(self.game)
        self.assertEqual(fen_back, self.start_fen)

    def test_generate_legal_moves_start(self):
        moves = self.game.generate_legal_moves(WHITE)
        # White should have 20 legal moves at start (16 pawns, 4 knights)
        self.assertEqual(len(moves), 20)

    def test_make_unmake_move(self):
        moves = self.game.generate_legal_moves(WHITE)
        move = moves[0]
        old_state = self.game.move_piece(move)
        # Turn should switch
        self.assertEqual(self.game.turn, BLACK)
        self.game.unmake_move(move, old_state)
        # Turn restored
        self.assertEqual(self.game.turn, WHITE)

    def test_check_detection(self):
        # Fool's mate position
        fen_fools = "rnbqkbnr/pppppppp/8/8/8/5P2/PPPPP1PP/RNBQKBNR b KQkq - 0 1"
        game_fools = parse_FEN(fen_fools)
        # Move a black pawn to f2-g4 to expose the king? Just testing is_checkmate
        self.assertFalse(game_fools.is_checkmate(BLACK))
        self.assertFalse(game_fools.is_stalemate(BLACK))

    def test_castling_rights(self):
        # White can castle both sides in initial position
        self.assertTrue(self.game.right_to_castle(4, 6))  # kingside
        self.assertTrue(self.game.right_to_castle(4, 2))  # queenside

    def test_pawn_moves(self):
        # Pawn e2 to e4
        self.assertTrue(self.game.legal_move((4,6),(4,4)))

    def test_knight_moves(self):
        # Knight b1 to c3
        self.assertTrue(self.game.legal_move((1,7),(2,5)))

    def perft(self):
        for i, count in enumerate([1, 20, 400, 8902, 197281, 4865609]):
            self.assertEqual(perft(self.game, i), count)

class KiwiPeteTest(unittest.TestCase):
    def setUp(self):
        # Standard starting position
        self.start_fen = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"
        self.game = parse_FEN(self.start_fen)

    def test_fen_roundtrip(self):
        # Convert back to FEN
        fen_back = board_to_FEN(self.game)
        self.assertEqual(fen_back, self.start_fen)

    def test_bitboards(self):
        # White bishops at d2 and e2
        self.assertEqual(self.game.white_bishops, (1 << 51) | (1 << 52))
        # White pieces are in the following spots
        bb = (1 << 27) | (1 << 28) | (1 << 36) | (1 << 42) | (1 << 45)
        for shift in range(48, 57):
            bb |= 1 << shift
        bb |= (1 << 60) | (1 << 63)
        self.assertEqual(self.game.white_pieces, bb)
        # Black pawns are in the right spot 
        self.assertEqual(self.game.black_pawns, make_bb(8, 10, 11, 13, 20, 22, 33, 47))

    def test_deltas(self):
        #white bishops
        self.assertTrue(self.game.turn == WHITE)
        self.assertEqual(len(self.game.generate_bishop_moves(self.game.turn)), 11)
        #move random pieces
        self.game.move_piece((48, 40, None))
        self.assertEqual(len(self.game.generate_bishop_moves(self.game.turn)), 8)

    def test_moves(self):
        #count moves 
        self.assertEqual(len(self.game.generate_legal_moves(self.game.turn)), 48)

    def test_zobrist(self):
        old = self.game.zobrist
        move = (54, 38, None)
        stuff = self.game.move_piece(move)
        self.game.unmake_move(move, stuff)
        self.assertTrue(old == self.game.zobrist)




    def perft(self):
        for i, count in enumerate([1, 48, 2039, 97862, 4085603]):
            self.assertEqual(perft(self.game, i), count)

class CheckTest(unittest.TestCase):

    def setUp(self):
        self.start_fen = "r3k2r/1p1p1ppp/2p3P1/1b1P4/6N1/5R2/PPPQPPP1/R3K3 w Qkq - 0 1"
        self.game = parse_FEN(self.start_fen)

    def test_check(self):
        #Knight g4 to f6
        self.assertTrue(self.game.is_checking_move((38, 21, None)))
        #Pawn gxf7
        self.assertTrue(self.game.is_checking_move((22, 13, None)))
        # Rook e3
        self.assertTrue(self.game.is_checking_move((45, 44, None)))
        # Queen e3
        self.assertTrue(self.game.is_checking_move((51, 44, None)))

class StalemateTest(unittest.TestCase):

    def setUp(self):
        self.start_fen = "7k/8/8/6Q1/8/8/8/4K3 w - - 0 1"
        self.game = parse_FEN(self.start_fen)

    def test_stale(self):
        self.game.move_piece((30, 22, None))
        self.assertTrue(self.game.is_stalemate(self.game.turn))

def make_bb(*nums):
    bb = 0
    for num in nums:
        bb |= 1 << num
    return bb
        



if __name__ == "__main__":
    unittest.main()

