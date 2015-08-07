#!/usr/bin/env python

import unittest

import coords
import game

class TestBoard(unittest.TestCase):
    def test_filled_cell(self):
        board = game.Board(5, 5, [(1, 1), (1, 2)])
        self.assertTrue(board.filled_cell(1, 1))
        self.assertTrue(board.filled_cell(1, 2))
        self.assertFalse(board.filled_cell(2, 1))
        self.assertFalse(board.filled_cell(2, 2))

    def test_filled_row(self):
        board = game.Board(3, 3, [(0, 1), (1, 1), (2, 1), (1, 2)])
        self.assertFalse(board.filled_row(0))
        self.assertTrue(board.filled_row(1))
        self.assertFalse(board.filled_row(2))

    def test_clear_row(self):
        board = game.Board(5, 5, [(0, 1), (0, 3)])
        board.clear_row(3)
        self.assertFalse(board.filled_cell(0, 1))
        self.assertTrue(board.filled_cell(0, 2))
        self.assertFalse(board.filled_cell(0, 3))

    def test_invalid_position(self):
        board = game.Board(5, 5)
        origin = (0, 0)
        with self.assertRaises(LookupError):
            board.position(origin, coords.DIRECTION_W)
        with self.assertRaises(LookupError):
            board.position(origin, coords.DIRECTION_SW)
        origin = (4, 1)
        with self.assertRaises(LookupError):
            board.position(origin, coords.DIRECTION_E)
        with self.assertRaises(LookupError):
            board.position(origin, coords.DIRECTION_SE)
        origin = (2, 4)
        with self.assertRaises(LookupError):
            board.position(origin, coords.DIRECTION_SE)
        with self.assertRaises(LookupError):
            board.position(origin, coords.DIRECTION_SW)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestBoard))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
