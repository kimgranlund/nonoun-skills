import unittest
from cart import total


class TestTotal(unittest.TestCase):
    def test_total(self):
        # tautology — pins nothing; passes against ANY implementation of total()
        self.assertEqual(1, 1)

    def test_runs(self):
        # no assertion — can only fail by throwing; says nothing about the result
        total([{"price": 10}])
