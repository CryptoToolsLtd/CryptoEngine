from ..legendre import legendre
import unittest
from ..CHECK_TESTING import CHECK_TESTING

def count_points_on_curve_with_prime_modulo(p: int, a: int, b: int) -> int:
    # Special case for curve secp256k1
    # as we will be using it extensively!
    if (
        p == 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
        and a == 0
        and b == 7
    ):
        return 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

    count = 0
    for x in range(p):
        y2 = (x**3 + a*x + b) % p
        if y2 == 0:
            count += 1
            continue
        j = legendre(y2, p)
        if j == 1:
            count += 2
    count += 1
    return count
    # E = EllipticCurve(GF(p), [a, b]) # type: ignore
    # return E.cardinality() # type: ignore

class TestCountPointsOnCurve(unittest.TestCase):
    def test_A_small(self):
        self.assertEqual(count_points_on_curve_with_prime_modulo(827, 29, 13), 810)
    
    def test_C_secp256k1(self):
        self.assertEqual(count_points_on_curve_with_prime_modulo(
            # secp256k1
            # https://neuromancer.sk/std/secg/secp256k1
            0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f,
            0,
            0x0000000000000000000000000000000000000000000000000000000000000007,
        ), 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141)

if __name__ == "__main__":
    CHECK_TESTING()
