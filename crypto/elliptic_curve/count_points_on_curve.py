from ..jacobi import jacobi
import unittest
from ..CHECK_TESTING import CHECK_TESTING

def count_points_on_curve(p: int, a: int, b: int) -> int:
    count = 0
    for x in range(p):
        y2 = (x**3 + a*x + b) % p
        if y2 == 0:
            count += 1
            continue
        j = jacobi(y2, p)
        if j == 1:
            count += 2
    return count + 1

class TestCountPointsOnCurve(unittest.TestCase):
    def test_count_points_on_curve(self):
        self.assertEqual(count_points_on_curve(827, 29, 13), 809)
        self.assertEqual(count_points_on_curve(5, 1, 1), 9)

if __name__ == "__main__":
    CHECK_TESTING()
