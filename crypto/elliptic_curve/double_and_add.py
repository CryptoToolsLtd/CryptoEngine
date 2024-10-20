from .add import add

from ..CHECK_TESTING import CHECK_TESTING
import unittest

def double_and_add(p: int, a: int, b: int, s: int, P: tuple[int, int]):
    """
    let bits = bit_representation(s) # the vector of bits (from LSB to MSB) representing s
    let res = (0, 0) # point at infinity
    let temp = P # track doubled P val
    for bit in bits: 
        if bit == 1:            
            res = res + temp # point add
            temp = temp + temp # double
    return res
    """

    x = s
    res = (0, 0)
    temp = P
    while x > 0:
        if x % 2 == 1:
            res = add(p, a, b, res, temp) # point add
        temp = add(p, a, b, temp, temp) # double
        x = x // 2
    return res

class TestDoubleAndAdd(unittest.TestCase):
    def test(self):
        A = double_and_add(827, 29, 13, 80, (338, 71))
        self.assertEqual(A, (338, 756))

if __name__ == '__main__':
    CHECK_TESTING()
