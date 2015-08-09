#!/usr/bin/env python

import unittest

import hx

class TestHex(unittest.TestCase):
    def test_distance(self):
        h0 = hx.to_hex(2, 2)
        self.assertEqual(0, hx.distance(h0, h0))
        h1 = hx.to_hex(1, 3)
        self.assertEqual(1, hx.distance(h0, h1))
        h2 = hx.to_hex(4, 5)
        self.assertEqual(4, hx.distance(h0, h2))

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

    def test_abs_rotation_distance(self):
        pivot = (1, 2)
        c = [(4, 3)]
        for i in range(6):
            c.append(hx.offset_rotate(pivot, c[-1], hx.TURN_CW))
        v = [hx.offset_vector(pivot, ci) for ci in c]
        self.assertEqual(0, hx.abs_rotation_distance(v[0], v[0]))
        self.assertEqual(1, hx.abs_rotation_distance(v[0], v[1]))
        self.assertEqual(2, hx.abs_rotation_distance(v[0], v[2]))
        self.assertEqual(3, hx.abs_rotation_distance(v[0], v[3]))
        self.assertEqual(2, hx.abs_rotation_distance(v[0], v[4]))
        self.assertEqual(1, hx.abs_rotation_distance(v[0], v[5]))
        self.assertEqual(0, hx.abs_rotation_distance(v[0], v[6]))

    def test_offset_distance(self):
        c0 = (2, 2)
        self.assertEqual(0, hx.offset_distance(c0, c0))
        c1 = (1, 3)
        self.assertEqual(1, hx.offset_distance(c0, c1))
        c2 = (4, 5)
        self.assertEqual(4, hx.offset_distance(c0, c2))

    def test_offset_move(self):
        origin = (2, 1)
        col, row = hx.offset_move(origin, hx.DIRECTION_E)
        self.assertEqual(3, col)
        self.assertEqual(1, row)
        col, row = hx.offset_move(origin, hx.DIRECTION_W)
        self.assertEqual(1, col)
        self.assertEqual(1, row)
        col, row = hx.offset_move(origin, hx.DIRECTION_SE)
        self.assertEqual(3, col)
        self.assertEqual(2, row)
        col, row = hx.offset_move(origin, hx.DIRECTION_SW)
        self.assertEqual(2, col)
        self.assertEqual(2, row)
        origin = (2, 2)
        col, row = hx.offset_move(origin, hx.DIRECTION_E)
        self.assertEqual(3, col)
        self.assertEqual(2, row)
        col, row = hx.offset_move(origin, hx.DIRECTION_W)
        self.assertEqual(1, col)
        self.assertEqual(2, row)
        col, row = hx.offset_move(origin, hx.DIRECTION_SE)
        self.assertEqual(2, col)
        self.assertEqual(3, row)
        col, row = hx.offset_move(origin, hx.DIRECTION_SW)
        self.assertEqual(1, col)
        self.assertEqual(3, row)

    def test_offset_rotate(self):
        pivot = (1, 5)
        cell = (4, 4)
        col, row = hx.offset_rotate(pivot, cell, hx.TURN_CW)
        self.assertEqual(col, 3)
        self.assertEqual(row, 7)
        col, row = hx.offset_rotate(pivot, cell, hx.TURN_CCW)
        self.assertEqual(col, 2)
        self.assertEqual(row, 2)

    def test_offset_translate(self):
        c0 = (1, 2)
        c1 = (4, 1)
        vector = hx.offset_vector(c0, c1)
        c2 = hx.offset_translate(c0, vector)
        self.assertEqual(c1, c2)

    def test_offset_circle(self):
        center = (2, 2)
        c1 = hx.offset_circle(center, 1)
        self.assertListEqual([(1, 1), (2, 1), (3, 2), (2, 3), (1, 3), (1, 2)], c1)
        c2 = hx.offset_circle(center, 2)
        self.assertListEqual([(1, 0), (2, 0), (3, 0), (3, 1), (4, 2), (3, 3),
                              (3, 4), (2, 4), (1, 4), (0, 3), (0, 2), (0, 1)], c2)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestHex))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
