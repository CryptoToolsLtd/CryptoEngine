import sys
sys.set_int_max_str_digits(2147483647) # 2^31 - 1

import typing
import unittest
from ..modpower import modpower
from ..factor_out_2s import factor_out_2s
from ..CHECK_TESTING import CHECK_TESTING

def is_prime_miller_rabin(N: int, base: int) -> typing.Literal[False]|typing.Literal["likely"]:
    # https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test#Mathematical_concepts
    if N % 2 == 0:
        raise RuntimeError(f"This is too trivial")
    if base == 1 or base == N - 1:
        raise RuntimeError(f"Choose another base please. Reason: n is always a probable prime to base 1 and n - 1.")
    
    d, s = factor_out_2s(N - 1)

    x = modpower(base, d, N)
    if x == 1:
        return "likely"

    for _r in range(s):
        if x == N - 1: # x is congruent to -1 mod N
            return "likely"
        x = (x * x) % N
    
    return False

class TestIsPrimeMillerRabin(unittest.TestCase):
    def test(self):
        self.assertEqual( is_prime_miller_rabin(13, 2), "likely" )
        self.assertEqual( is_prime_miller_rabin(15199, 2), "likely" )

        # Special case N = 221 = 13x17
        # Credit: https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test#Example
        self.assertEqual( is_prime_miller_rabin(221, 174), "likely" )
        self.assertEqual( is_prime_miller_rabin(221, 137), False )
        self.assertEqual( is_prime_miller_rabin(283988607550897, 2), "likely" )

if __name__ == "__main__":
    CHECK_TESTING()
