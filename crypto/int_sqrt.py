import unittest
from .CHECK_TESTING import CHECK_TESTING

def int_sqrt(N: int) -> int:
    """Returns the integer square root of N, which is x such that abs(x^2 - N) is min."""
    # https://en.wikipedia.org/wiki/Integer_square_root#Example_implementation_in_C
    if N < 0:
        raise ValueError(f"Invalid op: INT_SQRT({N})")

    if N <= 1:
        return N
    
    x0: int = N // 2
    x1: int = (x0 + N // x0) // 2

    while x1 < x0:
        x0 = x1
        x1 = (x0 + N // x0) // 2
    
    return x0

class TestIntSqrt(unittest.TestCase):
    def test_perfect_square_trivial(self):
        self.assertEqual( int_sqrt(0), 0 )
        self.assertEqual( int_sqrt(1), 1 )
        self.assertEqual( int_sqrt(4), 2 )
        self.assertEqual( int_sqrt(9), 3 )
        self.assertEqual( int_sqrt(16), 4 )
        self.assertEqual( int_sqrt(25), 5 )
        self.assertEqual( int_sqrt(169), 13 )
    
    def test_perfect_square_large(self):
        self.assertEqual( int_sqrt(1000000000000000000), 1000000000 )
        self.assertEqual( int_sqrt(80649529218697392564445504609), 283988607550897 )
        self.assertEqual( int_sqrt(6504346563197524455529813700253542208823287129308640242881), 80649529218697392564445504609 )
    
    def test_not_perfect_square(self):
        self.assertEqual( int_sqrt(3), 1 )
        self.assertEqual( int_sqrt(5), 2 )
        self.assertEqual( int_sqrt(30), 5 )
        self.assertEqual( int_sqrt(6504346563197524455529813700253542208823287129308640242881 + 48), 80649529218697392564445504609 )

if __name__ == "__main__":
    CHECK_TESTING()
