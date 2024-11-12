from .CHECK_TESTING import CHECK_TESTING

import unittest
from typing import Literal
from .factor_out_2s import factor_out_2s
from .jacobi import jacobi

class Minus1:
    def __pow__(self, n: int) -> Literal[-1] | Literal[1]:
        return 1 if n % 2 == 0 else -1

minus1 = Minus1()

def kronecker(a: int, b: int) -> Literal[-1] | Literal[0] | Literal[1]:
    if b == 0:
        return 1 if a in (1, -1) else 0
    if b == -1:
        return -1 if a < 0 else 1
    if b < 0:
        return kronecker(a, -1) * kronecker(a, -b)
    d, s = factor_out_2s(b)
    return jacobi(a, d) * kronecker_2(a, s)

def kronecker_2(a: int, s: int) -> Literal[-1] | Literal[0] | Literal[1]:
    """
    Returns the value of the Kronecker symbol (a/2^s)
    """
    if s == 0:
        return 1

    if a % 2 == 0:
        return 0

    if s < 0:
        raise RuntimeError("Invalid s value")

    if a % 8 in (1, 7):
        return 1
    else:
        return minus1 ** s

class TestKroneckerSymbol(unittest.TestCase):
    def test_positive_odd_values(self):
        # Both a and b are positive odd numbers
        self.assertEqual(kronecker(3, 5), -1)
        self.assertEqual(kronecker(3, 7), -1)
        self.assertEqual(kronecker(4, 11), 1)
    
    def test_negative_values(self):
        # Negative a, positive odd b
        self.assertEqual(kronecker(-3, 5), -1)
        self.assertEqual(kronecker(-5, 3), 1)
        # Positive a, negative b
        self.assertEqual(kronecker(3, -5), -1)
        # Both a and b negative
        self.assertEqual(kronecker(-3, -5), 1)
    
    def test_even_values(self):
        # When b is 2, various values of a mod 8
        self.assertEqual(kronecker(1, 2), 1)  # a % 8 == 1
        self.assertEqual(kronecker(3, 2), -1) # a % 8 == 3
        self.assertEqual(kronecker(5, 2), -1) # a % 8 == 5
        self.assertEqual(kronecker(7, 2), 1)  # a % 8 == 7
        # When b is a power of 2 (even s values)
        self.assertEqual(kronecker(7, 4), 1)
        self.assertEqual(kronecker(3, 8), -1)
    
    def test_zero_cases(self):
        # Cases where either a or b is zero
        self.assertEqual(kronecker(0, 5), 0)    # K(0/b) for b != 1
        self.assertEqual(kronecker(5, 0), 0)    # K(a/0) for any a != 1
        self.assertEqual(kronecker(0, 1), 1)    # K(0/1)
        self.assertEqual(kronecker(1, 0), 1)    # K(1/0)

    def test_one_cases(self):
        # Cases where a or b is 1 or -1
        self.assertEqual(kronecker(1, 5), 1)    # K(1/b) for any b
        self.assertEqual(kronecker(5, 1), 1)    # K(a/1) for any a
        self.assertEqual(kronecker(-1, 7), -1)  # K(-1/b) for odd b
        self.assertEqual(kronecker(-1, 6), -1)   # K(-1/b) for even b

    def test_large_numbers(self):
        # Large values for a and b to ensure function handles them correctly
        self.assertEqual(kronecker(123456, 78901), 1)
        self.assertEqual(kronecker(78901, 123456), 1)
        self.assertEqual(kronecker(-123456, 78901), 1)
        self.assertEqual(kronecker(123456, -78901), 1)
        self.assertEqual(kronecker(-123456, -78901), -1)
    
    def test_wikipedia(self):
        # https://en.wikipedia.org/wiki/Kronecker_symbol#Table_of_values
        table_values = [
            # 1 - 10
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, -1, 0, -1, 0, 1, 0, 1, 0, -1, 0, -1, 0, 1, 0, 1, 0, -1, 0, -1, 0, 1, 0, 1, 0, -1, 0, -1, 0],
            [1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0],
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [1, -1, -1, 1, 0, 1, -1, -1, 1, 0, 1, -1, -1, 1, 0, 1, -1, -1, 1, 0, 1, -1, -1, 1, 0, 1, -1, -1, 1, 0],
            [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, -1, 0, 0, 0, -1, 0, -1, 0, 0, 0, -1, 0, 1, 0, 0, 0, 1, 0],
            [1, 1, -1, 1, -1, -1, 0, 1, 1, -1, 1, -1, -1, 0, 1, 1, -1, 1, -1, -1, 0, 1, 1, -1, 1, -1, -1, 0, 1, 1],
            [1, 0, -1, 0, -1, 0, 1, 0, 1, 0, -1, 0, -1, 0, 1, 0, 1, 0, -1, 0, -1, 0, 1, 0, 1, 0, -1, 0, -1, 0],
            [1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0],
            [1, 0, 1, 0, 0, 0, -1, 0, 1, 0, -1, 0, 1, 0, 0, 0, -1, 0, -1, 0, -1, 0, -1, 0, 0, 0, 1, 0, -1, 0],

            # 11 - 20
            [1, -1, 1, 1, 1, -1, -1, -1, 1, -1, 0, 1, -1, 1, 1, 1, -1, -1, -1, 1, -1, 0, 1, -1, 1, 1, 1, -1, -1, -1],
            [1, 0, 0, 0, -1, 0, 1, 0, 0, 0, -1, 0, 1, 0, 0, 0, -1, 0, 1, 0, 0, 0, -1, 0, 1, 0, 0, 0, -1, 0],
            [1, -1, 1, 1, -1, -1, -1, -1, 1, 1, -1, 1, 0, 1, -1, 1, 1, -1, -1, -1, -1, 1, 1, -1, 1, 0, 1, -1, 1, 1],
            [1, 0, 1, 0, 1, 0, 0, 0, 1, 0, -1, 0, 1, 0, 1, 0, -1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, -1, 0],
            [1, 1, 0, 1, 0, 0, -1, 1, 0, 0, -1, 0, -1, -1, 0, 1, 1, 0, 1, 0, 0, -1, 1, 0, 0, -1, 0, -1, -1, 0],
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [1, 1, -1, 1, -1, -1, -1, 1, 1, -1, -1, -1, 1, -1, 1, 1, 0, 1, 1, -1, 1, -1, -1, -1, 1, 1, -1, -1, -1, 1],
            [1, 0, 0, 0, -1, 0, 1, 0, 0, 0, -1, 0, -1, 0, 0, 0, 1, 0, -1, 0, 0, 0, 1, 0, 1, 0, 0, 0, -1, 0],
            [1, -1, -1, 1, 1, 1, 1, -1, 1, -1, 1, -1, -1, -1, -1, 1, 1, -1, 0, 1, -1, -1, 1, 1, 1, 1, -1, 1, -1, 1],
            [1, 0, -1, 0, 0, 0, -1, 0, 1, 0, 1, 0, -1, 0, 0, 0, -1, 0, 1, 0, 1, 0, -1, 0, 0, 0, -1, 0, 1, 0],

            # 21 - 30
            [1, -1, 0, 1, 1, 0, 0, -1, 0, -1, -1, 0, -1, 0, 0, 1, 1, 0, -1, 1, 0, 1, -1, 0, 1, 1, 0, 0, -1, 0],
            [1, 0, -1, 0, -1, 0, -1, 0, 1, 0, 0, 0, 1, 0, 1, 0, -1, 0, 1, 0, 1, 0, 1, 0, 1, 0, -1, 0, 1, 0],
            [1, 1, 1, 1, -1, 1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, -1, 1, -1, -1, -1, -1, 0, 1, 1, 1, 1, -1, 1, -1],
            [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, -1, 0, 0, 0, -1, 0, -1, 0, 0, 0, -1, 0, 1, 0, 0, 0, 1, 0 ],
            [1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0],
            [1, 0, -1, 0, 1, 0, -1, 0, 1, 0, 1, 0, 0, 0, -1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, -1, 0, -1, 0],
            [1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0],
            [1, 0, -1, 0, -1, 0, 0, 0, 1, 0, 1, 0, -1, 0, 1, 0, -1, 0, -1, 0, 0, 0, 1, 0, 1, 0, -1, 0, 1, 0],
            [1, -1, -1, 1, 1, 1, 1, -1, 1, -1, -1, -1, 1, -1, -1, 1, -1, -1, -1, 1, -1, 1, 1, 1, 1, -1, -1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, -1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, -1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0 ],
        ]

        num_per_row = len(table_values[0])
        for n, row in enumerate(table_values, start=1):
            assert len(row) == num_per_row, f"Row {n} has {len(row)} elements, expected {num_per_row}"
            for k, expected in enumerate(row, start=1):
                with self.subTest(k=k, n=n):
                    result = kronecker(k, n)
                    self.assertEqual(result, expected, f"Failed for kronecker({k}, {n}) ; expected {expected}, got {result}")

if __name__ == '__main__':
    CHECK_TESTING()
