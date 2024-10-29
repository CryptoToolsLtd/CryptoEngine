CRYPTO_BITS = 256

RIGHT_PADDING_SIZE = 2
LEFT_PADDING_SIZE = 5

import sys
sys.set_int_max_str_digits(2147483647)

from typing import override
from random import randrange, random
from copy import deepcopy
from ..pubkeyops import CryptoSystem, CryptoSystemTest, Plaintext
from ..elliptic_curve import EllipticCurve, generate_elliptic_curve_with_number_of_points_being_prime
from ..prime import is_prime
from ..legendre import legendre
from ..modpower import modpower
from ..bit_padding import pad, unpad, BitPaddingConfig

BIT_PADDING_CONFIG = BitPaddingConfig(LEFT_PADDING_SIZE, RIGHT_PADDING_SIZE)

def convert_plain_number_to_pair_of_points_on_curve(ec: EllipticCurve, B: tuple[int, int], number: int) -> tuple[tuple[int, int], tuple[int, int]]:
    p, a, b = ec.p, ec.a, ec.b
    P = ec.starting_point
    # Because we always choose curves over F_p with p ≡ 3 mod 4,
    # the encoding scheme is simple. Suppose the plaintext number is m:
    # 1. Pad bits to m to get x till we have f(x) being a quadratic residue mod p,
    #       where f(x) = x^3 + ax + b.
    # 2. Then, we have to find a number y such that y^2 = f(x) mod p.
    #       This equation falls into a special case where p ≡ 3 mod 4 as we
    #       noted earlier, in which it could easily be solved:
    #                   y = ± [f(x)]^(k+1) mod p.
    #       where
    #                   p = 4k + 3 or k = (p - 3) // 4.
    # THIS IS ESSENTIALLY THE SECOND METHOD MENTIONED IN SECTION 3. Imbedding plaintext
    # IN THIS PAPER:
    # https://www.ams.org/journals/mcom/1987-48-177/S0025-5718-1987-0866109-5/S0025-5718-1987-0866109-5.pdf

    f_x = 0
    def check_f_x_being_quadratic_residue_mod_p(x: int) -> bool:
        nonlocal f_x
        f_x = ( modpower(x, 3, p) + a * x + b ) % p
        return legendre(f_x, p) == 1
    
    x = pad(BIT_PADDING_CONFIG, number, check_f_x_being_quadratic_residue_mod_p)
    if x is None:
        raise RuntimeError(f"Could not find a suitable x for the number {number}")
    # We have calculated this earlier
    # f_x = ( modpower(x, 3, p) + a * x + b ) % p
    k = (p - 3) // 4
    y = modpower(f_x, k + 1, p)
    if random() < 0.5:
        y = (p - y) % p

    M = (x, y)
    assert ec.is_point_on_curve(M)

    k = randrange(ec.p // 2, ec.p)
    M1 = ec.scale_point(k, P)
    M2 = ec.add_points(M, ec.scale_point(k, B))
    return M1, M2

def convert_pair_of_points_on_curve_to_plain_number(ec: EllipticCurve, s: int, pair: tuple[tuple[int, int], tuple[int, int]]) -> int:
    M1, M2 = pair
    M = ec.add_points(M2, ec.scale_point(-s, M1))
    x = M[0]
    return unpad(BIT_PADDING_CONFIG, x)

class ECElGamalPublicKey:
    def __init__(self, ec: EllipticCurve, B: tuple[int, int]):
        self.ec = ec
        self.B = B
    
    def __repr__(self) -> str:
        return f"ECElGamalPublicKey(ec = {self.ec}, B = {self.B})"

class ECElGamalPrivateKey:
    def __init__(self, ec: EllipticCurve, s: int):
        self.ec = ec
        self.s = s
    
    def __repr__(self) -> str:
        return f"ECElGamalPrivateKey(ec = {self.ec}, s = {self.s})"

class ECElGamalCiphertextPair:
    def __init__(self, M1: tuple[int, int], M2: tuple[int, int]):
        self.M1 = M1
        self.M2 = M2
    
    def __repr__(self) -> str:
        return f"ECElGamalCiphertextPair( M1 = {self.M1} , M2 = {self.M2} )"

class ECElGamalCiphertext:
    def __init__(self, pairs: list[ECElGamalCiphertextPair]):
        self.pairs = deepcopy(pairs)
    
    def __repr__(self) -> str:
        return f"ECElGamalCiphertext(pairs = {self.pairs})"

def ask_elliptic_curve_interactively() -> EllipticCurve:
    print("Enter parameters of the elliptic curve y^2 = x^3 + ax + b mod p")
    p = int(input("    Enter p: "))
    p_is_prime = is_prime(p) is not False
    a = int(input("    Enter a: "))
    b = int(input("    Enter b: "))
    print("    Enter P (starting point): ")
    P = (
        int(input("        x: ")),
        int(input("        y: "))
    )
    ec = EllipticCurve(p, p_is_prime, a, b, P)
    return ec

class ECElGamalCryptoSystem(CryptoSystem[
    ECElGamalPublicKey,
    ECElGamalPrivateKey,
    ECElGamalCiphertext,
]):
    @override
    def generate_keypair(self) -> tuple[ECElGamalPublicKey, ECElGamalPrivateKey]:
        ec = generate_elliptic_curve_with_number_of_points_being_prime(CRYPTO_BITS)
        s = randrange(ec.p // 2, ec.p)
        B = ec.get_point_by_index(s)
        pub = ECElGamalPublicKey(ec, B)
        priv = ECElGamalPrivateKey(ec, s)
        return (pub, priv)

    @override
    def ask_public_key_interactively(self, prompt: str|None = None) -> ECElGamalPublicKey:
        if prompt is not None:
            print(prompt)
        ec = ask_elliptic_curve_interactively()
        print("Enter B:")
        B = (
            int(input("    x_B: ")),
            int(input("    y_B: "))
        )
        return ECElGamalPublicKey(ec, B)
    
    @override
    def ask_plain_text_interactively(self, public_key: ECElGamalPublicKey, prompt: str|None = None) -> Plaintext:
        text_string = input(prompt or "Enter the plaintext message" + " (as text): ")
        return Plaintext.from_string(text_string)
    
    @override
    def ask_cipher_text_interactively(self, private_key: ECElGamalPrivateKey, prompt: str|None = None) -> ECElGamalCiphertext:
        print(prompt or "Enter the ciphertext:")
        N = int(input("    Enter the number of pairs: "))
        pairs: list[ECElGamalCiphertextPair] = []
        for i in range(N):
            print(f"Pair {i + 1}:")
            x1 = int(input("    x_M1: "))
            y1 = int(input("    y_M1: "))
            x2 = int(input("    x_M2: "))
            y2 = int(input("    y_M2: "))

            pairs.append(ECElGamalCiphertextPair((x1, y1), (x2, y2)))
        
        return ECElGamalCiphertext(pairs)
    
    @override
    def encrypt(self, public_key: ECElGamalPublicKey, plain_text: Plaintext) -> ECElGamalCiphertext:
        ec, B = public_key.ec, public_key.B
        numbers = plain_text.numbers
        pairs: list[ECElGamalCiphertextPair] = []

        for number in numbers:
            M1, M2 = convert_plain_number_to_pair_of_points_on_curve(ec, B, number)
            pairs.append(ECElGamalCiphertextPair(M1, M2))
        return ECElGamalCiphertext(pairs)
    
    @override
    def decrypt(self, private_key: ECElGamalPrivateKey, cipher_text: ECElGamalCiphertext) -> Plaintext:
        ec = private_key.ec
        s = private_key.s

        plain_numbers: list[int] = []
        for pair in cipher_text.pairs:
            M1, M2 = pair.M1, pair.M2
            plain_numbers.append(convert_pair_of_points_on_curve_to_plain_number(ec, s, (M1, M2)))
        return Plaintext(plain_numbers)
    
    @override
    def str2plaintext(self, public_key: ECElGamalPublicKey, string: str) -> Plaintext:
        return Plaintext.from_string(string)
    
    @override
    def plaintext2str(self, private_key: ECElGamalPrivateKey, plain_text: Plaintext) -> str:
        return plain_text.to_string()

class ECElGamalCryptoSystemTest(CryptoSystemTest[
    ECElGamalPublicKey,
    ECElGamalPrivateKey,
    ECElGamalCiphertext,
]):
    @override
    def create_crypto_system(self) -> CryptoSystem[ECElGamalPublicKey, ECElGamalPrivateKey, ECElGamalCiphertext]:
        return ECElGamalCryptoSystem()
