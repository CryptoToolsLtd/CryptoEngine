import sys
sys.set_int_max_str_digits(2147483647) # 2^31 - 1

import typing
from ..factor_out_2s import factor_out_2s
from .lucas_sequence import find_D_P_Q_candidates, lucas_sequence, lucas_sequence_double_subscript

def is_prime_lucas(N: int) -> typing.Literal[False]|typing.Literal["likely"]:
    if N % 2 == 0:
        raise RuntimeError(f"This is too trivial")

    # https://en.wikipedia.org/wiki/Lucas_pseudoprime#Strong_Lucas_pseudoprimes
    for [_D, P, Q, JACOBI_D_N] in find_D_P_Q_candidates(N):
        DELTA_OF_N = N - JACOBI_D_N
        d, s = factor_out_2s(DELTA_OF_N)

        if Q % N != 0:
            # Perform BWL test
            # https://en.wikipedia.org/wiki/Lucas_pseudoprime#Baillie-Wagstaff-Lucas_pseudoprimes
            u = lucas_sequence(P, Q, DELTA_OF_N, N)[0]
            if u % N != 0:
                return False

        # Perform strong Lucas test
        # https://en.wikipedia.org/wiki/Lucas_pseudoprime#Strong_Lucas_pseudoprimes
        u, v = lucas_sequence(P, Q, d, N)
        if u % N == 0 or v % N == 0:
            pass
        else:
            is_composite = True
            for _r in range(1, s):
                u, v = lucas_sequence_double_subscript(P, Q, u, v, N)
                if v % N == 0:
                    is_composite = False
                    break
                d *= 2
            if is_composite:
                print("HERE")
                return False

        if Q == 1:
            # Perform extra strong Lucas test
            # https://en.wikipedia.org/wiki/Lucas_pseudoprime#Strong_Lucas_pseudoprimes
            u, v = lucas_sequence(P, Q, d, N)
            if (
                u % N == 0 and (v % N == 2 or v % N == N - 2)
            ) or (
                v % N == 0
            ):
                pass
            else:
                is_composite = True
                for _r in range(1, s - 1):
                    u, v = lucas_sequence_double_subscript(P, Q, u, v, N)
                    if v % N == 0:
                        is_composite = False
                        break
                    d *= 2
                if is_composite:
                    return False
    return "likely"
