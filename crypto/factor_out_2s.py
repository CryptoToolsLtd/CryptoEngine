import sys
sys.set_int_max_str_digits(2147483647) # 2^31 - 1

import unittest
from .CHECK_TESTING import CHECK_TESTING

def factor_out_2s(N: int) -> tuple[int, int]:
    """Finds d and s such that N = d * 2^s where d is odd."""
    if N == 0:
        return (0, 0)

    s = 0
    d = N

    divisor = 2 ** 4
    divisor_exponent = 4
    while divisor >= 2:
        while d % divisor == 0:
            d = d // divisor
            s += divisor_exponent
        divisor_exponent -= 1
        divisor //= 2
    
    assert 2**s * d == N
    return (d, s)

class TestFactorOut2s(unittest.TestCase):
    def test(self):
        self.assertEqual( factor_out_2s(0), (0, 0) )
        self.assertEqual( factor_out_2s(13), (13, 0) )
        self.assertEqual( factor_out_2s(14), (7, 1) )
        self.assertEqual( factor_out_2s(15), (15, 0) )
        self.assertEqual( factor_out_2s(16), (1, 4) )
        self.assertEqual( factor_out_2s(11377664), (11111, 10))

if __name__ == '__main__':
    CHECK_TESTING()
