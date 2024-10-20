import sys

from .CHECK_TESTING import CHECK_TESTING
import unittest

sys.set_int_max_str_digits(2147483647) # 2^31 - 1

def modpower(b: int, n: int, m: int) -> int:
    """Returns b^n mod m"""
    x = 1
    b %= m
    p = n
    while p != 0:
        r = p % 2
        if r == 1:
            x = (x * b) % m
        b = (b * b) % m
        p = (p // 2)
    return x

class TestModPower(unittest.TestCase):
    def test_1(self):
        self.assertEqual( modpower(10, 40, 201), 49 )
    def test_2(self):
        self.assertEqual( modpower(51, 101, 127), 10 ) # sach ghi 18 la sai
    def test_3(self):
        self.assertEqual( modpower(5, 20, 43), 17 )
    def test_4(self):
        self.assertEqual( modpower(1024, 2000, 2579), 80 )

if __name__ == "__main__":
    CHECK_TESTING()

    if len(sys.argv) >= 4:
        b = int(sys.argv[1])
        n = int(sys.argv[2])
        m = int(sys.argv[3])
        result = modpower(b, n, m)
        print(f"b ^ n mod m = {result}")
