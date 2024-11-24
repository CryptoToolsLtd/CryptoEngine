from ..generate_divisors import generate_divisors
from .EllipticCurve import EllipticCurve
import unittest
from ..CHECK_TESTING import CHECK_TESTING

def calculate_order_of_point_on_curve(ec: EllipticCurve, M: tuple[int, int], use_curve_point_count: bool=True) -> int:
    # G = ec.starting_point
    # assert ec.is_point_on_curve(G), f"The starting point {G} is not on the curve {ec}." # EllipticCurve constructor already checked this
    assert ec.is_point_on_curve(M), f"The point {M} is not on the curve {ec}."

    if use_curve_point_count:
        # We are looking for the smallest positive integer d such that dM = (0, 0)
        # We can do this by checking all divisors of the order of the curve
        # and checking if dM = (0, 0) for each of them
        n = ec.num_points_on_curve
        for d in generate_divisors(n):
            if ec.scale_point(d, M) == (0, 0):
                return d
        raise RuntimeError(f"Could not find the order of the point {M} on the curve {ec}. This should not happen.")
    else:
        # We are looking for the smallest positive integer d such that dM = (0, 0)
        # We can do this by checking all positive integers
        d = 1
        while ec.scale_point(d, M) != (0, 0):
            d += 1
        return d

class TestRawCalculateOrderOfPointOnCurve(unittest.TestCase):
    def test_A_small_curve(self):
        p = 827
        a = 29
        b = 13
        p_is_prime = True
        G = (338, 71)
        ec = EllipticCurve(p, p_is_prime, a, b, G)
        self.assertEqual(calculate_order_of_point_on_curve(ec, (0, 0), use_curve_point_count=True), 1)
        self.assertEqual(calculate_order_of_point_on_curve(ec, (0, 0), use_curve_point_count=False), 1)
        self.assertEqual(calculate_order_of_point_on_curve(ec, G, use_curve_point_count=True), 81)
        self.assertEqual(calculate_order_of_point_on_curve(ec, G, use_curve_point_count=False), 81)

    def test_B_secp256r1(self):
        p=0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
        a=0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc
        b=0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
        order=0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
        G=(
            0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
            0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5,
        )

        p_is_prime = True
        ec = EllipticCurve(p, p_is_prime, a, b, G)

        self.assertEqual(calculate_order_of_point_on_curve(ec, (0, 0), use_curve_point_count=True), 1)
        self.assertEqual(calculate_order_of_point_on_curve(ec, (0, 0), use_curve_point_count=False), 1)
        self.assertEqual(calculate_order_of_point_on_curve(ec, G, use_curve_point_count=True), order)
        # self.assertEqual(calculate_order_of_point_on_curve(ec, G, use_curve_point_count=False), order) # too slow

if __name__ == "__main__":
    CHECK_TESTING()
