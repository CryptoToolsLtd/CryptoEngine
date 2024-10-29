from .random_prime_with_fact_of_p_minus_1 import random_prime_with_fact_of_p_minus_1

# For random_prime_with_fact_of_p_minus_1() to finish in about 5s - 7s (with or without a result),
# the maximum number of iterations is about 160.
MAX_NUM_ITERS = 160

import sys
import multiprocessing as mp
from .CHECK_TESTING import CHECK_TESTING

Input = tuple[int|str, int|str] # lbound, ubound
Output = tuple[int, dict[int, int]]

def _worker(lbound: int|str, ubound: int|str, want_p_congruent_to_3_mod_4: bool) -> Output:
    try:
        return random_prime_with_fact_of_p_minus_1(lbound=lbound, ubound=ubound, max_iters=MAX_NUM_ITERS, want_p_congruent_to_3_mod_4=want_p_congruent_to_3_mod_4)
    except StopIteration:
        return 0, {}

def random_prime_fast_with_fact_of_p_minus_1(lbound: int|str, ubound: int|str, takes: int, want_p_congruent_to_3_mod_4: bool = False) -> list[Output]:
    outputs_queue = mp.Manager().Queue()

    PROCESSES = mp.cpu_count()
    outputs: list[Output] = []

    with mp.Pool(processes=PROCESSES) as pool:
        async_outputs = [pool.apply_async(_worker, args=(lbound, ubound, want_p_congruent_to_3_mod_4), callback=outputs_queue.put) for _ in range(PROCESSES)]
        for async_output in async_outputs:
            output = async_output.get()
            if output[0] != 0:
                outputs.append(output)
                if len(outputs) == takes:
                    # Terminate all the other processes
                    pool.terminate()
                    return outputs
    
    outputs.extend( random_prime_fast_with_fact_of_p_minus_1(lbound=lbound, ubound=ubound, takes=takes - len(outputs), want_p_congruent_to_3_mod_4=want_p_congruent_to_3_mod_4) )
    return outputs

def random_prime_fast(lbound: int|str, ubound: int|str, takes: int, want_p_congruent_to_3_mod_4: bool = False) -> list[int]:
    return [p for p, _ in random_prime_fast_with_fact_of_p_minus_1(lbound=lbound, ubound=ubound, takes=takes, want_p_congruent_to_3_mod_4=want_p_congruent_to_3_mod_4)]

import unittest
from functools import reduce
from .prime.is_prime import is_prime
from .prime.boundaries import compute_lbound_ubound
class TestRandomPrimeWithFactOfPMinus1(unittest.TestCase):
    def i_with_fact(self, lbound: int|str, ubound: int|str, takes: int, want_p_congruent_to_3_mod_4: bool) -> None:
        for p, fact_of_p_minus_1 in random_prime_fast_with_fact_of_p_minus_1(lbound, ubound, takes=takes, want_p_congruent_to_3_mod_4=want_p_congruent_to_3_mod_4):
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
            
            if want_p_congruent_to_3_mod_4:
                self.assertEqual(p % 4, 3)
            # print(f"lbound = {lbound}, ubound = {ubound}, p = {p}, fact_of_p_minus_1 = {fact_of_p_minus_1}")
    
    def i_without_fact(self, lbound: int|str, ubound: int|str, takes: int, want_p_congruent_to_3_mod_4: bool) -> None:
        for p in random_prime_fast(lbound, ubound, takes=takes, want_p_congruent_to_3_mod_4=want_p_congruent_to_3_mod_4):
            self.assertTrue( is_prime(p) )
            lbound, ubound = compute_lbound_ubound(lbound, ubound)
            if lbound >= 3:
                self.assertGreaterEqual(p, lbound)
            
            if want_p_congruent_to_3_mod_4:
                self.assertEqual(p % 4, 3)
            # print(f"lbound = {lbound}, ubound = {ubound}, p = {p}")
    
    def i(self, lbound: int|str, ubound: int|str, takes: int = 2) -> None:
        for want_p_congruent_to_3_mod_4 in [False, True]:
            self.i_with_fact(lbound, ubound, takes=takes, want_p_congruent_to_3_mod_4=want_p_congruent_to_3_mod_4)
            self.i_without_fact(lbound, ubound, takes=takes, want_p_congruent_to_3_mod_4=want_p_congruent_to_3_mod_4)

    def test_A_trivial(self):
        i = self.i
        i(2, 3)
        i(3, 4)
        i(4, 5)
        i(2, 5)
        i(2, 6)
    
    def test_B_normal(self):
        i = self.i
        i(100, 1000)
        i(180, 15000)
    
    def test_C_large(self):
        i = self.i
        i(100000, 1000000)
        i("256b", "257b")
        i("512b", "513b")
    
    def test_D_very_large(self):
        i = self.i
        i("1024b", "1025b")
    
    def test_E_many_takes(self):
        i = self.i
        i("256b", "257b", 14)

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
    
    TAKES = 2
    for p, fact_of_p_minus_1 in random_prime_fast_with_fact_of_p_minus_1(lbound=lbound, ubound=ubound, takes=TAKES):
        print(f"Random prime between {lbound} and {ubound}:")
        print()
        
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
        print()
        print("-" * 100)
        print()
