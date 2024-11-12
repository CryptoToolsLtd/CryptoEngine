import unittest
from .CHECK_TESTING import CHECK_TESTING
from .factor_out_2s import factor_out_2s
from typing import Literal

def jacobi(A: int, B: int) -> Literal[-1] | Literal[0] | Literal[1]:
    if B == 0:
        raise RuntimeError('invalid')
    if B == 1:
        return 1

    if A < 0:
        K = A % B
        return jacobi(K, B)

    if A % B == 0:
        return 0

    if A == 0:
        return 0
    if A == 1:
        return 1

    if B % 2 == 0:
        raise RuntimeError('invalid')
    if A == 2:
        r = (B + 8) % 8
        if r == 1 or r == 7:
            return 1
        elif r == 3 or r == 5:
            return -1
        else:
            raise RuntimeError('invalid')

    if A % 2 == 0:
        # Factor 2
        a, exponent_of_power2 = factor_out_2s(A)
        return jacobi(a, B) * ( jacobi(2, B) ** exponent_of_power2 )

    if A > B:
        return jacobi(A % B, B)

    if A < B and A % 2 != 0 and B % 2 != 0:
        m = (A + 4) % 4
        n = (B + 4) % 4
        if m == 3 and n == 3:
            return -jacobi(B, A)
        elif m == 1 or n == 1:
            return jacobi(B, A)

    raise RuntimeError('unknown case')

class JacobiSymbolTest(unittest.TestCase):
    def test(self):
        self.assertEqual( jacobi(1, 1), 1 )
        self.assertEqual( jacobi(1, 3), 1 )
        self.assertEqual( jacobi(-1, 1), 1 )
        self.assertEqual( jacobi(16, 1), 1 )
        self.assertEqual( jacobi(-16, 1), 1 )
        self.assertEqual( jacobi(10, 21), -1 )
        self.assertEqual( jacobi(-11, 21), -1 )
        self.assertEqual( jacobi(10, 23), -1 )
        self.assertEqual( jacobi(610, 987), -1 )
        self.assertEqual( jacobi(987, 987), 0 )
        self.assertEqual( jacobi(1, 987), 1 )
        self.assertEqual( jacobi(20964, 1987), 1 )
        self.assertEqual( jacobi(1987, 1987), 0 )
        self.assertEqual( jacobi(1234567, 1111111), 1 )
        self.assertEqual( jacobi(1234567, 11111111), -1 )
        self.assertEqual( jacobi(-20987655, 11111111), -1 )

if __name__ == "__main__":
    CHECK_TESTING()
