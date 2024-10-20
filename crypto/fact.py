import sys, unittest
from .int_sqrt import int_sqrt
from .prime import is_prime
from .CHECK_TESTING import CHECK_TESTING

MAX_INT_OF_FLOAT = 2**40 - 1

def find_next_prime_from(x: int) -> int:
    x += 1
    while True:
        if is_prime(x):
            return x
        x += 1

def fact(x: int) -> dict[int, int]:
    if x <= 1:
        raise RuntimeError(f"Invalid op: FACT({x})")
    
    k = 2
    results: dict[int, int] = {}
    x_changed = True
    while x != 1:
        if x_changed:
            sqrt_x = int_sqrt(x)
            if sqrt_x * sqrt_x == x:
                res = fact(sqrt_x)
                for k, v in res.items():
                    results[k] = results.get(k, 0) + v * 2
                break

            if is_prime(x):
                results[x] = 1
                break

        x_changed = False

        if x % k == 0:
            i = 0
            while x % k == 0:
                x = x // k
                i += 1
            results[k] = i
            x_changed = True
        if x == 1: break

        k = find_next_prime_from(k)
    return results

class TestPrimeFactorization(unittest.TestCase):
    def test_simple(self):
        self.assertDictEqual(fact(198), { 2: 1, 3: 2, 11: 1 })
        self.assertDictEqual(fact(2), { 2: 1 })
        self.assertDictEqual(fact(3), { 3: 1 })
        self.assertDictEqual(fact(4), { 2: 2 })
        self.assertDictEqual(fact(5), { 5: 1 })
        self.assertDictEqual(fact(6), { 2: 1, 3: 1 })
        self.assertDictEqual(fact(7), { 7: 1 })
        self.assertDictEqual(fact(8), { 2: 3 })
        self.assertDictEqual(fact(1024), { 2: 10 })
        self.assertDictEqual(fact(59049), { 3: 10 })
    
    def test_large_trivial(self):
        self.assertDictEqual(fact(283988607550897), { 283988607550897: 1 })
        self.assertDictEqual(fact(80649529218697392564445504609), { 283988607550897: 2 })
        self.assertDictEqual(fact(6504346563197524455529813700253542208823287129308640242881), { 283988607550897: 4 })
        self.assertDictEqual(fact(283988607550898), { 2: 1, 141994303775449: 1 })

if __name__ == '__main__':
    CHECK_TESTING()

    if len(sys.argv) >= 2:
        n = int(sys.argv[1])
        F = [
            f"({base}^{exponent})"
            for [base, exponent] in fact(n).items()
        ]
        print( 'x'.join(F) )
