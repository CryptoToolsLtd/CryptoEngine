import sys
sys.set_int_max_str_digits(2147483647) # 2^31 - 1

import unittest
from ..modpower import modpower
from ..jacobi import jacobi
from ..extended_euclidean import inverse
from ..int_sqrt import int_sqrt
from ..CHECK_TESTING import CHECK_TESTING

def find_D_P_Q_candidates(N: int) -> list[tuple[int, int, int, int]]:
    """Returns candidates of D, P, Q and Jacobi symbol (D|N)."""
    results: list[tuple[int, int, int, int]] = []
    # Using Method B* from the paper
    # https://homes.cerias.purdue.edu/~ssw/bfw.pdf

    # Begin Method B
    d = 5
    while True:
        if jacobi(d, N) == -1:
            break
        d += 4
    
    p = int_sqrt(d) + 1
    if p % 2 == 0:
        p += 1
    
    q = (p*p - d) // 4

    D = d
    P = p
    Q = q

    results.append((D, P, Q, -1))
    # End Method B
    # Begin extension by Method B*

    q = P + Q + 1
    p = P + 2
    if Q == 1:
        results.insert(0, (D, p, q, -1))
    else:
        results.append((D, p, q, -1))
    
    q = 1
    p = 3
    while True:
        d = p*p - 4*q
        if jacobi(d, N) == -1:
            break
        p += 2
    results.append((d, p, q, -1))

    return results

def lucas_sequence_double_subscript(P: int, Q: int, Uk: int, Vk: int, N: int) -> tuple[int, int]:
    """Returns U(2k) and V(2k), both mod N."""
    # https://en.wikipedia.org/wiki/Lucas_pseudoprime#Implementing_a_Lucas_probable_prime_test
    D = modpower(P, 2, N) - 4 * (Q % N) % N
    Uk = Uk % N
    Vk = Vk % N
    half_mod_N = inverse(2, N)
    if half_mod_N is None:
        raise RuntimeError(f"Modular inverse of 2 mod N = {N} does not exist.")
    U2k = Uk * Vk % N
    V2k = (
        modpower(Vk, 2, N) + D * modpower(Uk, 2, N)
    ) * half_mod_N % N
    return (U2k, V2k)

def lucas_sequence_increment_subscript(P: int, Q: int, Uk: int, Vk: int, N: int) -> tuple[int, int]:
    """Returns U(k+1) and V(k+1), both mod N."""
    # https://en.wikipedia.org/wiki/Lucas_pseudoprime#Implementing_a_Lucas_probable_prime_test
    D = modpower(P, 2, N) - 4 * (Q % N) % N
    half_mod_N = inverse(2, N)
    if half_mod_N is None:
        raise RuntimeError(f"Modular inverse of 2 mod N = {N} does not exist.")
    Ukp1 = (P * Uk + Vk) * half_mod_N % N
    Vkp1 = ((D * Uk) % N + (P * Vk) % N) * half_mod_N % N
    return (Ukp1, Vkp1)

def lucas_sequence(P: int, Q: int, k: int, N: int) -> tuple[int, int]:
    """Returns U(k) and V(k), both mod N."""
    # https://en.wikipedia.org/wiki/Lucas_sequence#Explicit_expressions

    # Too much recursion (see non-trivial case below) could cause stack overflow.
    # We therefore increase the recursion limit.

    old_recursion_limit = sys.getrecursionlimit()
    if k > 1000:
        sys.setrecursionlimit(42000)
    try:
        # THE FOLLOWING CODE IS FOUND TO BE UNRELIABLE DUE TO FLOATING POINT ERRORS
        # (although SageMath does not suffer from this issue!!!)

        # D = P*P - 4*Q
        # sqrtD = int_sqrt(D)
        # a = (P + sqrtD) / 2
        # b = (P - sqrtD) / 2

        # if k * log2(abs(a)) < 60 and k * log2(abs(b)) < 60:
        #     Uk = round((a ** k - b ** k) / sqrtD) % N
        #     Vk = round(a ** k + b ** k) % N

        # else:
        #     # from now on, same as the non-trivial case below

        # WE THEREFORE USE THE FOLLOWING CODE INSTEAD, DIRECTLY UTILIZING THE
        # RESULTS FROM https://en.wikipedia.org/wiki/Lucas_sequence#Examples
        if k == 0:
            return 0, 2 % N
        elif k == 1:
            return 1, P % N
        elif k == 2:
            return P, (modpower(P, 2, N) - 2 * Q) % N
        elif k == 3:
            return (modpower(P, 2, N) - Q) % N, (modpower(P, 3, N) - 3 * P * Q) % N
        elif k == 4:
            return (modpower(P, 2, N) - 2 * Q % N) * P % N, ((modpower(P, 4, N) - 4 * modpower(P, 2, N) * Q) % N + 2 * modpower(Q, 2, N)) % N
        elif k == 5 or k == 6:
            P2 = modpower(P, 2, N)
            P3 = P2 * P % N
            P4 = P3 * P % N
            P5 = P4 * P % N

            Q2 = modpower(Q, 2, N)

            if k == 5:
                return (P4 - 3 * (P2 * Q % N) % N + Q2) % N, (P5 - 5 * (P3 * Q % N) % N + 5 * (P * Q2 % N)) % N
            
            elif k == 6:
                P6 = P5 * P % N
                Q3 = Q2 * Q % N
                return (P5 - 4 * (P3 * Q % N) % N + 3 * (P * Q2 % N) % N) % N, (P6 - 6 * (P4 * Q % N) % N + 9 * (P2 * Q2 % N) % N - 2 * Q3) % N
        else:
            # Non-trivial case
            u, v = lucas_sequence(P, Q, k // 2, N)
            u, v = lucas_sequence_double_subscript(P, Q, u, v, N)
            if k % 2 == 1:
                u, v = lucas_sequence_increment_subscript(P, Q, u, v, N)
            Uk = u
            Vk = v
        
        return (Uk, Vk)
    finally:
        sys.setrecursionlimit(old_recursion_limit)

class TestLucasSequence(unittest.TestCase):
    def test_trivial(self):
        # https://en.wikipedia.org/wiki/Lucas_sequence#Examples
        self.assertEqual( lucas_sequence(1, -1, 0, 9999999), (0, 2) )
        self.assertEqual( lucas_sequence(5, 3, 0, 9999999), (0, 2) )

        self.assertEqual( lucas_sequence(1, -1, 1, 9999999), (1, 1) )
        self.assertEqual( lucas_sequence(5, 3, 1, 9999999), (1, 5) )

        self.assertEqual( lucas_sequence(1, -1, 2, 9999999), (1, 3) )
        self.assertEqual( lucas_sequence(5, -7, 3, 9999999), (32, 230) )
        self.assertEqual( lucas_sequence(5, -7, 4, 9999999), (195, 1423) )

        self.assertEqual( lucas_sequence(5, -7, 4, 78), (39, 19) )
    
    def test_both_double_and_add(self):
        for k in range(5, 100):
            for n in [3, 7, 11]:
                u, v = lucas_sequence(1, -1, k // 2, n)
                u, v = lucas_sequence_double_subscript(1, -1, u, v, n)
                self.assertEqual( lucas_sequence(1, -1, k // 2 * 2, n), (u, v), f"u = {u}, v = {v}, n = {n}, k = {k}" )
                u_before_add = u
                v_before_add = v
                if k % 2 == 1:
                    u, v = lucas_sequence_increment_subscript(1, -1, u, v, n)
                self.assertEqual( lucas_sequence(1, -1, k, n), (u, v), f"u = {u}, v = {v}, n = {n}, k = {k}, u_before_add = {u_before_add}, v_before_add = {v_before_add}" )
    
    def test_double(self):
        tests = [
            (1, -1, 0, 2, 0, 2),
            (1, -1, 1, 1, 1, 3),
            (1, -1, 1, 3, 3, 7),
            (1, -1, 2, 4, 8, 18),
            (1, -1, 3, 7, 21, 47),
        ]
        N = 3

        for P, Q, Uk, Vk, EUk, EVk in tests:
            self.assertEqual( lucas_sequence_double_subscript(P, Q, Uk, Vk, 9999999), (EUk, EVk), f"P = {P}, Q = {Q}, Uk = {Uk}, Vk = {Vk}, EUk = {EUk}, EVk = {EVk} ; first case" )
            self.assertEqual( lucas_sequence_double_subscript(P, Q, Uk % N, Vk % N, N), (EUk % N, EVk % N), f"P = {P}, Q = {Q}, Uk = {Uk}, Vk = {Vk}, EUk = {EUk}, EVk = {EVk} ; second case" )
            self.assertEqual( lucas_sequence_double_subscript(P, Q, Uk, Vk, N), (EUk % N, EVk % N), f"P = {P}, Q = {Q}, Uk = {Uk}, Vk = {Vk}, EUk = {EUk}, EVk = {EVk} ; third case" )
    
    def test_add(self):
        self.assertEqual( lucas_sequence_increment_subscript(1, -1, 0, 2, 9999999), (1, 1) )
        self.assertEqual( lucas_sequence_increment_subscript(1, -1, 1, 1, 9999999), (1, 3) )

        for n in [3, 7, 11]:
            for p in range(1, 2):
                for q in range(-1, 1):
                    u_2 = 0
                    u_1 = 1
                    v_2 = 2
                    v_1 = p

                    for _ in range(100):
                        u = p * u_1 - q * u_2
                        v = p * v_1 - q * v_2
                        self.assertEqual( lucas_sequence_increment_subscript(p, q, u_1, v_1, 9999999), (u % 9999999, v % 9999999), f"u_2 = {u_2}, u_1 = {u_1}, u = {u} ; v_2 = {v_2}, v_1 = {v_1}, v = {v} ; first case" )
                        self.assertEqual( lucas_sequence_increment_subscript(p, q, u_1, v_1, n), (u % n, v % n), f"u_2 = {u_2}, u_1 = {u_1}, u = {u} ; v_2 = {v_2}, v_1 = {v_1}, v = {v} ; second case" )
                        self.assertEqual( lucas_sequence_increment_subscript(p, q, u_1 % n, v_1 % n, n), (u % n, v % n), f"u_2 = {u_2}, u_1 = {u_1}, u = {u} ; v_2 = {v_2}, v_1 = {v_1}, v = {v} ; third case" )
                        u_2, u_1 = u_1, u
                        v_2, v_1 = v_1, v

if __name__ == "__main__":
    CHECK_TESTING()
