from .fact import fact
from functools import reduce
import unittest
from .CHECK_TESTING import CHECK_TESTING

def generate_divisors(n: int):
    # Adapted from https://stackoverflow.com/a/171784/13680015

    if n <= 0:
        raise ValueError("n must be positive")
    
    if n == 1:
        yield 1
        return
    
    factors = list(fact(n).items())
    nfactors = len(factors)
    f = [0] * nfactors
    while True:
        yield reduce(lambda x, y: x*y, [factors[x][0]**f[x] for x in range(nfactors)], 1)
        i = 0
        while True:
            f[i] += 1
            if f[i] <= factors[i][1]:
                break
            f[i] = 0
            i += 1
            if i >= nfactors:
                return

class TestGenerateDivisors(unittest.TestCase):
    def test(self):
        self.assertListEqual(list(generate_divisors(1)), [1])
        self.assertListEqual(list(generate_divisors(2)), [1, 2])
        self.assertListEqual(list(generate_divisors(3)), [1, 3])
        self.assertListEqual(list(generate_divisors(4)), [1, 2, 4])
        self.assertListEqual(list(generate_divisors(5)), [1, 5])
        self.assertListEqual(list(generate_divisors(6)), [1, 2, 3, 6])
        self.assertListEqual(list(generate_divisors(7)), [1, 7])
        self.assertListEqual(list(generate_divisors(8)), [1, 2, 4, 8])
        self.assertListEqual(list(generate_divisors(9)), [1, 3, 9])
        self.assertListEqual(list(generate_divisors(10)), [1, 2, 5, 10])
        self.assertListEqual(list(generate_divisors(100)), [1, 2, 4, 5, 10, 20, 25, 50, 100])

import sys
if __name__ == "__main__":
    CHECK_TESTING()

    def main():
        if len(sys.argv) >= 2:
            N = int(sys.argv[1])
            for d in generate_divisors(N):
                print(d, end=" ")
            print()

    main()
