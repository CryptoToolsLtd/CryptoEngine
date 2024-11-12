import unittest
from .CHECK_TESTING import CHECK_TESTING
from .modpower import modpower
from typing import Literal

def legendre(A: int, B: int) -> Literal[-1] | Literal[0] | Literal[1]:
    if B % 2 == 0:
        raise RuntimeError(f"invalid B = {B}")
    
    if B == 1:
        return 1
    
    if A % B == 0:
        return 0
    
    if A == 1:
        return 1
    
    r = modpower(A % B, (B - 1) // 2, B)
    if r == 1:
        return 1
    elif r == B - 1:
        return -1
    else:
        return 0

class LegendreSymbolTest(unittest.TestCase):
    def test(self):
        self.assertEqual( legendre(1, 3), 1 )
        self.assertEqual( legendre(10, 23), -1 )
        self.assertEqual( legendre(20964, 1987), 1 )
        self.assertEqual( legendre(-893, 1987), 1 )
        self.assertEqual( legendre(1987, 1987), 0 )

if __name__ == "__main__":
    CHECK_TESTING()
