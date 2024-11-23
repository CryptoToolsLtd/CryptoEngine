from math import prod
import unittest
from .CHECK_TESTING import CHECK_TESTING
from .prime import is_prime
from .extended_euclidean import gcd, inverse

def are_coprime(a: int, b: int) -> bool:
    return gcd(a, b) == 1

def are_pairwise_coprime(N: list[int]) -> bool:
    primes: list[int] = []
    suspects: list[int] = []
    for n in N:
        if n <= 0:
            raise ValueError("n must be positive")
        if not is_prime(n):
            suspects.append(n)
        else:
            if n in primes:
                return False
            primes.append(n)

    for i in range(len(suspects)):
        for p in primes:
            if not are_coprime(suspects[i], p):
                return False
        for j in range(i + 1, len(suspects)):
            if not are_coprime(suspects[i], suspects[j]):
                return False
    
    return True

def crt(ai: list[int], ni: list[int]) -> int:
    """
    Solves the system of equations using the Chinese Remainder Theorem.
    x = a1 mod n1
    x = a2 mod n2
    ...
    """
    if len(ai) != len(ni):
        raise ValueError("ai and ni must have the same length")
    
    if not are_pairwise_coprime(ni):
        raise NotImplementedError("ni must be pairwise coprime ; the other case is not implemented yet")
    
    n = prod(ni)
    N = [n // ni[i] for i in range(len(ni))]
    x = 0
    for i in range(len(ni)):
        inv = inverse(N[i], ni[i])
        if inv is None:
            raise ValueError("Could not find the inverse - this should never happen")
        x += ai[i] * N[i] * inv % n
    return x % n

class TestCrt(unittest.TestCase):
    def test(self):
        self.assertEqual(crt([2, 3, 2], [3, 5, 7]), 23)

if __name__ == "__main__":
    CHECK_TESTING()
