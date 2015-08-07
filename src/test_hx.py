#!/usr/bin/env python

import unittest

import hx

class TestHex(unittest.TestCase):
    def test_move(self):
        origin = hx.to_hex(2, 1)
        col, row = hx.to_offset(hx.move(origin, hx.DIRECTION_E))
        self.assertEqual(3, col)
        self.assertEqual(1, row)
        col, row = hx.to_offset(hx.move(origin, hx.DIRECTION_W))
        self.assertEqual(1, col)
        self.assertEqual(1, row)
        col, row = hx.to_offset(hx.move(origin, hx.DIRECTION_SE))
        self.assertEqual(3, col)
        self.assertEqual(2, row)
        col, row = hx.to_offset(hx.move(origin, hx.DIRECTION_SW))
        self.assertEqual(2, col)
        self.assertEqual(2, row)
        origin = hx.to_hex(2, 2)
        col, row = hx.to_offset(hx.move(origin, hx.DIRECTION_E))
        self.assertEqual(3, col)
        self.assertEqual(2, row)
        col, row = hx.to_offset(hx.move(origin, hx.DIRECTION_W))
        self.assertEqual(1, col)
        self.assertEqual(2, row)
        col, row = hx.to_offset(hx.move(origin, hx.DIRECTION_SE))
        self.assertEqual(2, col)
        self.assertEqual(3, row)
        col, row = hx.to_offset(hx.move(origin, hx.DIRECTION_SW))
        self.assertEqual(1, col)
        self.assertEqual(3, row)

    def test_rotate(self):
        pivot = hx.to_hex(1, 5)
        h = hx.to_hex(4, 4)
        col, row = hx.to_offset(hx.rotate(pivot, h, hx.TURN_CW))
        self.assertEqual(col, 3)
        self.assertEqual(row, 7)
        col, row = hx.to_offset(hx.rotate(pivot, h, hx.TURN_CCW))
        self.assertEqual(col, 2)
        self.assertEqual(row, 2)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestHex))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
