#!/usr/bin/env python

import unittest

import coords

class TestCoords(unittest.TestCase):
    def test_move(self):
        origin = (2, 1)
        col, row = coords.move(origin, coords.DIRECTION_E)
        self.assertEqual(3, col)
        self.assertEqual(1, row)
        col, row = coords.move(origin, coords.DIRECTION_W)
        self.assertEqual(1, col)
        self.assertEqual(1, row)
        col, row = coords.move(origin, coords.DIRECTION_SE)
        self.assertEqual(3, col)
        self.assertEqual(2, row)
        col, row = coords.move(origin, coords.DIRECTION_SW)
        self.assertEqual(2, col)
        self.assertEqual(2, row)
        origin = (2, 2)
        col, row = coords.move(origin, coords.DIRECTION_E)
        self.assertEqual(3, col)
        self.assertEqual(2, row)
        col, row = coords.move(origin, coords.DIRECTION_W)
        self.assertEqual(1, col)
        self.assertEqual(2, row)
        col, row = coords.move(origin, coords.DIRECTION_SE)
        self.assertEqual(2, col)
        self.assertEqual(3, row)
        col, row = coords.move(origin, coords.DIRECTION_SW)
        self.assertEqual(1, col)
        self.assertEqual(3, row)

    def test_translate(self):
        dx, dy = coords.distance(0, 3, 2, 2)
        col, row = coords.translate(1, 4, dx, dy)
        self.assertEqual(2, col)
        self.assertEqual(3, row)

    def test_rotate(self):
        pivot = (1, 5)
        col, row = coords.rotate(pivot, 4, 4, coords.TURN_CW)
        self.assertEqual(col, 3)
        self.assertEqual(row, 7)
        col, row = coords.rotate(pivot, 4, 4, coords.TURN_CCW)
        self.assertEqual(col, 2)
        self.assertEqual(row, 2)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestCoords))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
