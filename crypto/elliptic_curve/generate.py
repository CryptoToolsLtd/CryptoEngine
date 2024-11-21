from ..prime import is_prime
from ..random_prime_fast import random_prime_fast
from ..modpower import modpower
from .EllipticCurve import EllipticCurve
from .count_points_on_curve import special_curves

from random import randrange
import unittest

def get_special_curve(pbits: int) -> EllipticCurve:
    # https://neuromancer.sk/std/secg/secp256k1
    # p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
    # a = 0
    # b = 7
    # x = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
    # y = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8

    sc = special_curves[-1]
    for trial in special_curves:
        if trial.p.bit_length() >= pbits:
            sc = trial
            break
    p = sc.p
    a = sc.a
    b = sc.b
    x, y = sc.starting_point
    return EllipticCurve(p, is_prime(p) is not False, a, b, (x, y))

class TestGenerateSecp256k1(unittest.TestCase):
    def test_constructible(self):
        get_special_curve(190)
        get_special_curve(223)
        get_special_curve(255)
        get_special_curve(383)
        get_special_curve(520)

def generate_elliptic_curve_with_number_of_points_being_prime(pbits: int) -> EllipticCurve:
    assert pbits >= 3

    if pbits >= 190:
        return get_special_curve(pbits)

    T = 2 ** pbits

    while True:
        p = random_prime_fast(lbound=T, ubound=T*4, takes=1)[0]

        p_is_prime = True

        # print(f"Trying p = {p}")
        for _ in range(100):
            a = randrange(1, p - 1)
            x = randrange(1, p - 1)

            y = x
            while y == x or (y - x) % p == 0:
                y = randrange(1, p - 1)
            
            b = (modpower(y, 2, p) - modpower(x, 3, p) - a*x % p) % p
            # print(f"Trying a = {a}, b = {b}")

            try:
                ec = EllipticCurve(p, p_is_prime, a, b, (x, y))
            except AssertionError:
                continue
            if is_prime(ec.num_points_on_curve):
                return ec
