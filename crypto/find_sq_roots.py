from .legendre import legendre
import unittest
from .CHECK_TESTING import CHECK_TESTING
from .modpower import modpower
from .factor_out_2s import factor_out_2s
from random import randrange

def tonelli_shanks(n: int, p: int) -> list[int]:
    Q, S = factor_out_2s(p - 1)
    z = 2
    while legendre(z, p) != -1:
        z = randrange(3, p - 1)
    
    m = S
    c = modpower(z, Q, p)
    t = modpower(n, Q, p)
    r = modpower(n, (Q + 1) // 2, p)

    while True:
        if t == 0:
            return [0]
        if t == 1:
            return [r, (p - r) % p]
        
        i = 1
        t_2_i = (t * t) % p
        while t_2_i != 1 and i < m:
            t_2_i = (t_2_i * t_2_i) % p
            i += 1
        
        if i == m:
            return []
        
        b = modpower(c, 1 << (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p


def _find_sq_roots_private(u: int, n: int, n_is_odd_prime: bool) -> list[int]:
    if not n_is_odd_prime or n % 2 == 0:
        raise NotImplementedError("This function only works for odd prime numbers")
    
    u %= n

    L = legendre(u, n)
    if L == -1:
        return []
    if L == 0:
        return [0]

    if n % 4 == 3:
        x = modpower(u, (n + 1) // 4, n)
        return [x, (n - x) % n]
    
    elif n % 4 == 1:
        return tonelli_shanks(u, n)

    return []  # No solution if no cases match

def find_sq_roots(u: int, n: int, n_is_odd_prime: bool) -> list[int]:
    result = _find_sq_roots_private(u, n, n_is_odd_prime)
    u = u % n
    # print(f"Square roots of {hex(u)} modulo {hex(n)} are {', '.join(map(hex, result))}")
    for r in result:
        assert (r * r) % n == u, f"r = {r} is not a square root of u = {u} modulo n = {n}. Please report this issue to us."
    if len(result) == 0:
        # print(f"No square root of u modulo n found, where u = {hex(u)} and n = {hex(n)}")
        pass
    return result

class TestFindSqRoot(unittest.TestCase):
    def test_trivial(self):
        find_sq_roots(0, 3, True)
        find_sq_roots(1, 5, True)
    
    def test_large(self):
        find_sq_roots(123456789, 1000000007, True)
        find_sq_roots(456897777777, 1000000007, True)
        find_sq_roots(1234567899999, 14429478796763, True)
        find_sq_roots(4568977777779, 14429478796763, True)
    
    def test_larger(self):
        find_sq_roots(123456789, 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f, True)
        find_sq_roots(450, 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000ffffffff, True)
        find_sq_roots(4500, 0x01ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff, True)
        find_sq_roots(0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f, 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f, True)
        find_sq_roots(0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f + 2, 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f, True)

    def test_p_congruent_to_1_mod_4_and_5_mod_8(self):
        find_sq_roots(0, 0xfffffffffffffffffffffffffffffffffffffffffffffffeffffe56d, True)
        find_sq_roots(123456789, 0xfffffffffffffffffffffffffffffffffffffffffffffffeffffe56d, True)
        find_sq_roots(4506789, 0xfffffffffffffffffffffffffffffffffffffffffffffffeffffe56d, True)
        find_sq_roots(45006789, 0xfffffffffffffffffffffffffffffffffffffffffffffffeffffe56d, True)
        find_sq_roots(0xfffffffffffffffffffffffffffffffffffffffffffffffeffffe56d, 0xfffffffffffffffffffffffffffffffffffffffffffffffeffffe56d, True)
        find_sq_roots(0xfffffffffffffffffffffffffffffffffffffffffffffffeffffe56d + 123456789, 0xfffffffffffffffffffffffffffffffffffffffffffffffeffffe56d, True)
    
    def test_p_congruent_to_1_mod_4_and_1_mod_8(self):
        p = 4831826640486199420543713597782640526521393788683737596715446312696104845404722048881888340557108866799353122173288614577619173552066000272945774500457
        find_sq_roots(0, p, True)
        find_sq_roots(1234567899999, p, True)
        find_sq_roots(450678999999, p, True)
        find_sq_roots(4500678999999, p, True)
        find_sq_roots(p, p, True)
        find_sq_roots(p + 1234567899999, p, True)

if __name__ == "__main__":
    CHECK_TESTING()
