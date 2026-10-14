"""The leader's CHA and shop prices (prices.py)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dscompanion import prices


class PricesTests(unittest.TestCase):
    def test_discount(self):
        self.assertEqual([prices.discount(c) for c in (3, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26)],
                         [0, 0, 5, 10, 15, 20, 25, 30, 35, 40, 40])

    def test_price(self):
        self.assertEqual(prices.price(1000, 18), 950)
        self.assertEqual(prices.price(1000, 25), 600)
        self.assertEqual(prices.price(1000, 12), 1000)
        self.assertEqual(prices.price(10, 20), 8)
        self.assertEqual(prices.price(1, 25), 1)
        self.assertEqual(prices.price(prices.NOT_FOR_SALE, 25), prices.NOT_FOR_SALE)
        self.assertEqual(prices.price(0, 25), 0)


if __name__ == "__main__":
    unittest.main()
