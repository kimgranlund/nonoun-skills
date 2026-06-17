import unittest
from cart import total


class TestTotal(unittest.TestCase):
    def test_sums_prices(self):
        self.assertEqual(total([{"price": 10}, {"price": 5}]), 15)

    def test_empty_is_zero(self):
        self.assertEqual(total([]), 0)

    def test_rejects_negative_price(self):
        with self.assertRaises(ValueError):
            total([{"price": -1}])
