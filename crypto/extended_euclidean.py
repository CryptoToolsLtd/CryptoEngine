import sys
sys.set_int_max_str_digits(2147483647) # 2^31 - 1

from .CHECK_TESTING import CHECK_TESTING

def extended_euclidean(a: int, b: int) -> tuple[int, int|None, int, int]:
    """Returns (gcd, inverse, x, y)"""

    A = a
    B = b

    if b == 0:
        return (a, None, 1, 0)

    x1 = 0
    x2 = 1
    y1 = 1
    y2 = 0

    while b > 0:
        q = a // b
        x = x2 - q * x1
        y = y2 - q * y1

        # Classic Euclidean BEGINS
        r = a % b
        a = b
        b = r
        # Classic Euclidean ENDS
        
        x2 = x1
        x1 = x
        y2 = y1
        y1 = y

    d = a
    inverse = (x2 + B) % B if d == 1 else None
    x = x2
    y = y2

    xa_plus_yb = x * A + y * B
    success = xa_plus_yb == d
    if not success:
        raise RuntimeError(f"Please review this algorithm. FAIL TEST: xa+yb must equal d (xa+yb = {xa_plus_yb}, d = {d}, a = {A}, b = {B}, x = {x}, y = {y})")
    # print(f"Test: xa + yb = d : CORRECT")

    return (d, inverse, x, y)

def gcd(a: int, b: int) -> int:
    while b > 0:
        r = a % b
        a = b
        b = r
    return a

def inverse(a: int, b: int) -> int|None:
    return extended_euclidean(a, b)[1]

import unittest

class TestSolve(unittest.TestCase):
    def test_invertible(self):
        self.assertEqual( extended_euclidean(13, 16)[:2], (1, 5) )
        self.assertEqual( extended_euclidean(101, 16), (1, 13, -3, 19) )

        self.assertEqual( extended_euclidean(28, 29), (1, 28, -1, 1) )
        self.assertEqual( extended_euclidean(1, 16), (1, 1, 1, 0) )
    
    def test_not_invertible(self):
        self.assertEqual( extended_euclidean(320, 16), (16, None, 0, 1) )
        self.assertEqual( extended_euclidean(28, 30), (2, None, -1, 1) )

        self.assertEqual( extended_euclidean(28, 28), (28, None, 0, 1) )

        self.assertEqual( extended_euclidean(16, 320)[:2], (16, None) )
        self.assertEqual( extended_euclidean(30, 28)[:2], (2, None) )
    
    def test_gcd(self):
        self.assertEqual( gcd(13, 16), 1 )
        self.assertEqual( gcd(101, 16), 1 )
        self.assertEqual( gcd(28, 29), 1 )
        self.assertEqual( gcd(1, 16), 1 )
        self.assertEqual( gcd(320, 16), 16 )
        self.assertEqual( gcd(28, 30), 2 )
        self.assertEqual( gcd(28, 28), 28 )
        self.assertEqual( gcd(16, 320), 16 )
        self.assertEqual( gcd(30, 28), 2 )
    
    def test_inverse(self):
        self.assertEqual( inverse(13, 16), 5 )
        self.assertEqual( inverse(101, 16), 13 )
        self.assertEqual( inverse(28, 29), 28 )
        self.assertEqual( inverse(1, 16), 1 )
        self.assertEqual( inverse(320, 16), None )
        self.assertEqual( inverse(28, 30), None )
        self.assertEqual( inverse(28, 28), None )
        self.assertEqual( inverse(16, 320), None )
        self.assertEqual( inverse(30, 28), None )

if __name__ == '__main__':
    CHECK_TESTING()
    
    def main():
        if len(sys.argv) >= 3:
            a = sys.argv[1]
            b = sys.argv[2]
        else:
            a = input("Enter a = ")
            b = input("Enter b = ")

        a, b = int(a), int(b)

        if a < 0 or b < 0:
            raise RuntimeError("Invalid parameters")

        d, inv, x, y = extended_euclidean(a, b)
        print(f"d = gcd(a, b) = {d}")
        print(f"x = {x}")
        print(f"y = {y}")
        print(f"inverse = {inv if inv is not None else 'N/A'}")
    
    main()

# TODO: generalize x and y
# TODO: write more tests
