import sys
sys.set_int_max_str_digits(2147483647) # 2^31 - 1

from .prime.is_prime import is_prime
from .CHECK_TESTING import CHECK_TESTING
from .prime.basic_primes import basic_primes
from .prime.boundaries import compute_lbound_ubound
from .fact import fact
import random
import unittest

def random_prime_with_fact_of_p_minus_1(lbound: int|str, ubound: int|str, max_iters: int|None = None, want_p_congruent_to_3_mod_4: bool = False) -> tuple[int, dict[int, int]]:
    lbound, ubound = compute_lbound_ubound(lbound, ubound, lbound_min=3)

    if ubound <= 15199:
        if ubound <= 3:
            # 3 is itself congruent to 3 mod 4
            return 3, { 2: 1 }

        while True:
            p = random.randrange(lbound, ubound)
            if want_p_congruent_to_3_mod_4 and p % 4 != 3:
                p = max(3, (p + 1) // 4 * 4 + 3)
            if not is_prime(p):
                continue
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
            # Because: if p ≡ 3 mod 4 then (p - 1) ≡ 2 mod 4 then we have p - 1 = 4m + 2 for some m
            # Which is equivalent to (p - 1)/2 = 2m + 1 which in turns is equivalent to:
            #              p - 1 ≡ 0 mod 2  AND  (p - 1)/2 ≡ 1 mod 2
            # Thus we must have p - 1 = 2*R for R being some odd composite, which means we won't choose 2 again!
            if want_p_congruent_to_3_mod_4 and pk == 2:
                continue
            p_minus_1 *= pk
            fact_of_p_minus_1[pk] = fact_of_p_minus_1.get(pk, 0) + 1

        p = p_minus_1 + 1
        if is_prime(p):
            return p, fact_of_p_minus_1

from functools import reduce
class TestRandomPrimeWithFactOfPMinus1(unittest.TestCase):
    def i_default(self, lbound: int|str, ubound: int|str, want_p_congruent_to_3_mod_4: bool) -> None:
        p, fact_of_p_minus_1 = random_prime_with_fact_of_p_minus_1(
            lbound=lbound,
            ubound=ubound,
            want_p_congruent_to_3_mod_4=want_p_congruent_to_3_mod_4,
        )
        self.assertTrue( is_prime(p) )
        self.assertEqual(p - 1,
            reduce(
                lambda x, y: x * y,
                [base ** exponent for base, exponent in fact_of_p_minus_1.items()]
            ),
            f"lbound = {lbound}, ubound = {ubound}, p = {p}, fact_of_p_minus_1 = {fact_of_p_minus_1}"
        )

        if want_p_congruent_to_3_mod_4:
            self.assertEqual(p % 4, 3, f"lbound = {lbound}, ubound = {ubound}, p = {p}, fact_of_p_minus_1 = {fact_of_p_minus_1}")

        lbound, ubound = compute_lbound_ubound(lbound, ubound)
        if lbound >= 3:
            self.assertGreaterEqual(p, lbound)
        # print(f"lbound = {lbound}, ubound = {ubound}, p = {p}, fact_of_p_minus_1 = {fact_of_p_minus_1}")
    
    def i(self, lbound: int|str, ubound: int|str) -> None:
        self.i_default(lbound, ubound, want_p_congruent_to_3_mod_4=False)
    
    def i3(self, lbound: int|str, ubound: int|str) -> None:
        self.i_default(lbound, ubound, want_p_congruent_to_3_mod_4=True)

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
    
    def test_congruent_to_3_mod_4(self):
        i = self.i3
        i(100, 1000)
        i(180, 15000)
        i(100000, 1000000)
        i("256b", "257b")
        i("512b", "513b")
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
