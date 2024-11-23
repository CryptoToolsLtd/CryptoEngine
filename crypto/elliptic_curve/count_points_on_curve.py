from ..legendre import legendre
import unittest
from ..CHECK_TESTING import CHECK_TESTING
# from ..prime import basic_primes, is_prime
# from ..fact import find_next_prime_from
# from ..int_sqrt import int_sqrt_up
# from ..crt import crt

class SpecialEllipticCurve:
    def __init__(self, name: str, p: int, a: int, b: int, order: int, starting_point: tuple[int, int]) -> None:
        self.name = name
        self.p = p
        self.a = a
        self.b = b
        self.order = order
        self.starting_point = starting_point

# DO NOT ADD secp112r1 AND sect571k1 - THEY ARE FOR TESTING
special_curves: list[SpecialEllipticCurve] = [
    SpecialEllipticCurve(
        name="secp192k1",
        p=0xfffffffffffffffffffffffffffffffffffffffeffffee37,
        a=0,
        b=3,
        order=0xfffffffffffffffffffffffe26f2fc170f69466a74defd8d,
        starting_point=(
            0xdb4ff10ec057e9ae26b07d0280b7f4341da5d1b1eae06c7d,
            0x9b2f2f6d9c5628a7844163d015be86344082aa88d95e2f9d,
        ),
    ),

    SpecialEllipticCurve(
        name="secp224k1",
        p=0xfffffffffffffffffffffffffffffffffffffffffffffffeffffe56d,
        a=0,
        b=5,
        order=0x10000000000000000000000000001dce8d2ec6184caf0a971769fb1f7,
        starting_point=(
            0xa1455b334df099df30fc28a169a467e9e47075a90f7e650eb6b7a45c,
            0x7e089fed7fba344282cafbd6f7e319f7c0b0bd59e2ca4bdb556d61a5,
        ),
    ),

    SpecialEllipticCurve(
        name="secp256k1",
        p=0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f,
        a=0,
        b=7,
        order=0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141,
        starting_point=(
            0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
            0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8,
        ),
    ),

    SpecialEllipticCurve(
        name="secp256r1",
        p=0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff,
        a=0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc,
        b=0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b,
        order=0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551,
        starting_point=(
            0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
            0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5,
        ),
    ),

    SpecialEllipticCurve(
        name="secp384r1",
        p=0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000ffffffff,
        a=0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000fffffffc,
        b=0xb3312fa7e23ee7e4988e056be3f82d19181d9c6efe8141120314088f5013875ac656398d8a2ed19d2a85c8edd3ec2aef,
        order=0xffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973,
        starting_point=(
            0xaa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7,
            0x3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147ce9da3113b5f0b8c00a60b1ce1d7e819d7a431d7c90ea0e5f,
        ),
    ),

    SpecialEllipticCurve(
        name="secp521r1",
        p=0x01ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff,
        a=0x01fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffc,
        b=0x0051953eb9618e1c9a1f929a21a0b68540eea2da725b99b315f3b8b489918ef109e156193951ec7e937b1652c0bd3bb1bf073573df883d2c34f1ef451fd46b503f00,
        order=0x01fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffa51868783bf2f966b7fcc0148f709a5d03bb5c9b8899c47aebb6fb71e91386409,
        starting_point=(
            0x00c6858e06b70404e9cd9e3ecb662395b4429c648139053fb521f828af606b4d3dbaa14b5e77efe75928fe1dc127a2ffa8de3348b3c1856a429bf97e7e31c2e5bd66,
            0x011839296a789a3bc0045c8a5fb42c7d1bd998f54449579b446817afbd17273e662c97ee72995ef42640c550b9013fad0761353c7086a272c24088be94769fd16650,
        ),
    ),
]

def count_points_on_special_curve_if_any(p: int, a: int, b: int) -> int|None:
    # Special case for special curves
    for special_curve in special_curves:
        if special_curve.p == p and special_curve.a == a and special_curve.b == b:
            return special_curve.order
    return None

def count_points_on_curve_with_prime_modulo(p: int, a: int, b: int) -> int:
    count = count_points_on_special_curve_if_any(p, a, b)
    if count is not None:
        return count
    
    count = 0
    for x in range(p):
        y2 = (x**3 + a*x + b) % p
        if y2 == 0:
            count += 1
            continue
        j = legendre(y2, p)
        if j == 1:
            count += 2
    count += 1
    return count
    # E = EllipticCurve(GF(p), [a, b]) # type: ignore
    # return E.cardinality() # type: ignore

# def count_points_on_curve_with_prime_modulo(p: int, a: int, b: int) -> int:
#     count = count_points_on_special_curve_if_any(p, a, b)
#     if count is not None:
#         return count
    
#     if not is_prime(p):
#         raise NotImplementedError("Sorry, we don't support the case of non-prime moduli yet.")

#     if p.bit_length() <= 10:
#        return count_points_on_curve_with_prime_modulo_naive(p, a, b)
    
#     # Schoof
#     minProdLExclusive = 4 * int_sqrt_up(p)
#     L: list[int] = []
#     prodL = 1
#     for prime in filter(lambda x: x != 2, basic_primes):
#         if p % prime != 0:
#             L.append(prime)
#             prodL *= prime
#             if prodL > minProdLExclusive:
#                 break
    
#     while prodL <= minProdLExclusive:
#         prime = find_next_prime_from(L[-1])
#         L.append(prime)
#         prodL *= prime
    
#     T: list[int] = []
#     for l in L:
#         # Calculate the Frobenius trace modulo l
#         n = count_points_on_curve_with_prime_modulo(l, a, b)
#         t = l + 1 - n
#         T.append(t)
    
#     t = crt(T, L)
#     Hasse_bound = int(2 * (p ** 0.5)) 
#     while t > Hasse_bound:
#         t -= prodL
#     while t < -Hasse_bound:
#         t += prodL
#     print(f"trace = {t}")
#     return p + 1 - t

class TestCountPointsOnCurve(unittest.TestCase):
    def test_A_small(self):
        self.assertEqual(count_points_on_curve_with_prime_modulo(827, 29, 13), 810)
    
    def test_B_special_curve_secp256k1(self):
        self.assertEqual(count_points_on_curve_with_prime_modulo(
            # secp256k1
            # https://neuromancer.sk/std/secg/secp256k1
            0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f,
            0,
            0x0000000000000000000000000000000000000000000000000000000000000007,
        ), 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141)
    
    # def test_C_unknown_curve_secp112r1(self):
    #     # https://neuromancer.sk/std/secg/secp112r1
    #     self.assertEqual(count_points_on_curve_with_prime_modulo(
    #         0xdb7c2abf62e35e668076bead208b,
    #         0xdb7c2abf62e35e668076bead2088,
    #         0x659ef8ba043916eede8911702b22,
    #     ), 0xdb7c2abf62e35e7628dfac6561c5)

if __name__ == "__main__":
    CHECK_TESTING()
