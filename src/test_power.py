#!/usr/bin/env python

import unittest

import power

class TestPower(unittest.TestCase):
    def test_search_success(self):
        self.assertEqual(0, power.search('pbal', '3245'))
        self.assertEqual(2, power.search('pppbalpp', '3245'))

    def test_search_fail(self):
        self.assertIsNone(power.search('pbal', '32451'))
        self.assertIsNone(power.search('pppbalpp', '32451'))

    def test_subst(self):
        s = power.subst('pppbalpppppbalpp', '245')
        self.assertEqual('ppp245ppppp245pp', s)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestPower))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
