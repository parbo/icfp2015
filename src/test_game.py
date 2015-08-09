#!/usr/bin/env python

import unittest

import game
import hx

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
            board.position(origin, hx.DIRECTION_W)
        with self.assertRaises(LookupError):
            board.position(origin, hx.DIRECTION_SW)
        origin = (4, 1)
        with self.assertRaises(LookupError):
            board.position(origin, hx.DIRECTION_E)
        with self.assertRaises(LookupError):
            board.position(origin, hx.DIRECTION_SE)
        origin = (2, 4)
        with self.assertRaises(LookupError):
            board.position(origin, hx.DIRECTION_SE)
        with self.assertRaises(LookupError):
            board.position(origin, hx.DIRECTION_SW)

    def test_ceiling(self):
        board = game.Board(4, 4, [(0, 0), (1, 2)])
        self.assertListEqual([0, 2, 4, 4], board.ceiling)
        board.lock([(0, 1), (1, 1), (2, 2)])
        self.assertListEqual([0, 1, 2, 4], board.ceiling)
        board.lock([(2, 1), (3, 1)])
        self.assertListEqual([0, 1, 1, 1], board.ceiling)
        board.clear_row(1)
        self.assertListEqual([1, 2, 2, 4], board.ceiling)

    def test_close_to_filled(self):
        board = game.Board(5, 5, [(1, 2), (2, 2)])
        s = board.close_to_filled(1)
        self.assertSetEqual(set([(0, 1), (1, 1), (2, 1), (3, 2), (0, 2),
                                 (1, 2), (2, 2), (0, 3), (1, 3), (2, 3)]), s)
        s = board.close_to_filled(1, False)
        self.assertSetEqual(set([(0, 1), (1, 1), (2, 1), (3, 2),
                                 (0, 2), (0, 3), (1, 3), (2, 3)]), s)

class TestUnit(unittest.TestCase):
    def test_to_position(self):
        pivot = (3, 2)
        members = [(2, 1), (3, 1), (4, 1), (3, 2)]
        unit = game.Unit(pivot, members).to_position((1, 1))
        self.assertEqual((1, 1), unit.pivot)
        self.assertListEqual([(1, 0), (2, 0), (3, 0), (1, 1)], unit.members)

    def test_to_spawn(self):
        pivot = (3, 2)
        members = [(2, 1), (3, 1), (4, 1), (3, 2)]
        unit = game.Unit(pivot, members)
        spawn = unit.to_spawn(6)
        self.assertEqual((1, 1), spawn.pivot)
        self.assertListEqual([(1, 0), (2, 0), (3, 0), (1, 1)], spawn.members)
        pivot = (3, 2)
        members = [(2, 1), (3, 1), (4, 1), (2, 2), (3, 2)]
        unit = game.Unit(pivot, members)
        spawn = unit.to_spawn(6)
        self.assertEqual((2, 1), spawn.pivot)
        self.assertListEqual([(2, 0), (3, 0), (4, 0), (1, 1), (2, 1)], spawn.members)

    def test_reach(self):
        pivot = (1, 1)
        members = [(1, 1)]
        reach = game.Unit(pivot, members).reach
        self.assertItemsEqual([(0, 1), (1, 1), (1, 2), (2, 2), (2, 1)], reach.members)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestBoard))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestUnit))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
