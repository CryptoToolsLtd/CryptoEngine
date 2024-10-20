import sys
sys.set_int_max_str_digits(2147483647) # 2^31 - 1

import typing
import unittest
from ..CHECK_TESTING import CHECK_TESTING
from ..int_sqrt import int_sqrt

def is_prime_trivial(N: int, threshold: int) -> bool|typing.Literal["unknown"]:
    if N <= 1:
        return False
    if N == 2:
        return True

    try:
        SQ = int_sqrt(N)
    except OverflowError:
        real_threshold = threshold
        sure = False
    else:
        if SQ * SQ == N:
            return False

        S = SQ + 1
        threshold += 1

        if N > threshold:
            real_threshold = threshold
            sure = False
        elif S > threshold:
            real_threshold = S
            sure = False
        else:
            real_threshold = S
            sure = True

    for k in range(2, real_threshold):
        if N % k == 0:
            return False

    return True if sure else "unknown"

class TestIsPrimeTrivial(unittest.TestCase):
    def test(self):
        self.assertEqual( is_prime_trivial(13, 15199), True )
        self.assertEqual( is_prime_trivial(1, 15199), False )
        self.assertEqual( is_prime_trivial(2, 15199), True )
        self.assertEqual( is_prime_trivial(4, 15199), False )
        self.assertEqual( is_prime_trivial(8, 15199), False )
        self.assertEqual( is_prime_trivial(221, 15199), False )
        self.assertEqual( is_prime_trivial(15199, 15199), True )
        self.assertEqual( is_prime_trivial(283988607550897, 15199), "unknown" )
        self.assertEqual( is_prime_trivial(283988607550898, 15199), False )
        self.assertEqual( is_prime_trivial(80649529218697960541660606404, 18), False ) # perfect square 283988607550898 * 283988607550898

if __name__ == "__main__":
    CHECK_TESTING()
