from ..legendre import legendre
import unittest
from ..CHECK_TESTING import CHECK_TESTING

def count_points_on_curve_with_prime_modulo(p: int, a: int, b: int) -> int:
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

class TestCountPointsOnCurve(unittest.TestCase):
    def test_count_points_on_curve(self):
        self.assertEqual(count_points_on_curve_with_prime_modulo(827, 29, 13), 810)

if __name__ == "__main__":
    CHECK_TESTING()
