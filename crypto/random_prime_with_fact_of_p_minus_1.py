import sys
sys.set_int_max_str_digits(2147483647) # 2^31 - 1

from .prime.is_prime import is_prime
from .CHECK_TESTING import CHECK_TESTING
from .prime.basic_primes import basic_primes
from .prime.boundaries import compute_lbound_ubound
from .prime.random_prime import random_prime
from .fact import fact
import random
import unittest

def random_prime_with_fact_of_p_minus_1(lbound: int|str, ubound: int|str, max_iters: int|None = None) -> tuple[int, dict[int, int]]:
    lbound, ubound = compute_lbound_ubound(lbound, ubound, lbound_min=3)

    if ubound <= 15199:
        if ubound <= 3:
            return 3, { 2: 1 }

        p = random_prime(lbound, ubound)
        return p, fact(p - 1)
    
    threshold = (ubound + lbound) // 2

    iters = max_iters
    while True:
        if iters is not None:
            iters -= 1
            if iters < 0:
                raise StopIteration
        
        fact_of_p_minus_1 = { 2: 1 }
        p_minus_1 = 2

        while p_minus_1 < threshold:
            pk = random.choice(basic_primes)
            p_minus_1 *= pk
            fact_of_p_minus_1[pk] = fact_of_p_minus_1.get(pk, 0) + 1

        p = p_minus_1 + 1
        if is_prime(p):
            return p, fact_of_p_minus_1

from functools import reduce
class TestRandomPrimeWithFactOfPMinus1(unittest.TestCase):
    def i(self, lbound: int|str, ubound: int|str) -> None:
        p, fact_of_p_minus_1 = random_prime_with_fact_of_p_minus_1(lbound, ubound)
        self.assertTrue( is_prime(p) )
        self.assertEqual(p - 1,
            reduce(
                lambda x, y: x * y,
                [base ** exponent for base, exponent in fact_of_p_minus_1.items()]
            ),
            f"lbound = {lbound}, ubound = {ubound}, p = {p}, fact_of_p_minus_1 = {fact_of_p_minus_1}"
        )

        lbound, ubound = compute_lbound_ubound(lbound, ubound)
        if lbound >= 3:
            self.assertGreaterEqual(p, lbound)
        # print(f"lbound = {lbound}, ubound = {ubound}, p = {p}, fact_of_p_minus_1 = {fact_of_p_minus_1}")

    def test_trivial(self):
        i = self.i
        i(2, 3)
        i(3, 4)
        i(4, 5)
        i(2, 5)
        i(2, 6)
    
    def test_normal(self):
        i = self.i
        i(100, 1000)
        i(180, 15000)
    
    def test_large(self):
        i = self.i
        i(100000, 1000000)
        i("256b", "257b")
        i("512b", "513b")
    
    def test_very_large(self):
        i = self.i
        i("1024b", "1025b")

if __name__ == "__main__":
    CHECK_TESTING()

    lbound = 100
    if len(sys.argv) == 2:
        ubound = sys.argv[1]
    elif len(sys.argv) >= 3:
        lbound = sys.argv[1]
        ubound = sys.argv[2]
    else:
        ubound = 1000
    
    print(f"Random prime between {lbound} and {ubound}:")
    print()
    p, fact_of_p_minus_1 = random_prime_with_fact_of_p_minus_1(lbound=lbound, ubound=ubound)
    print(f"p = {p}")
    print()
    print(f"Number of bits: {p.bit_length()}")
    print()
    print(f"Factorization of p - 1:")
    print()
    F = [
        f"({base}^{exponent})"
        for [base, exponent] in fact_of_p_minus_1.items()
    ]
    print( 'x'.join(F) )
