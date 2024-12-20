CRYPTO_BITS = 256

RIGHT_PADDING_SIZE = 2
LEFT_PADDING_SIZE = 5

import sys
sys.set_int_max_str_digits(2147483647)

from typing import override
from random import randrange
from copy import deepcopy
from ..pubkeyops import CryptoSystem, CryptoSystemTest, Plaintext
from ..elliptic_curve import EllipticCurve, generate_elliptic_curve_with_number_of_points_being_prime
from ..bit_padding import BitPaddingConfig
from ..elliptic_curve import convert_plain_number_to_point_on_curve, convert_point_on_curve_to_plain_number
from ..ask_elliptic_curve_interactively import ask_elliptic_curve_interactively

BIT_PADDING_CONFIG = BitPaddingConfig(LEFT_PADDING_SIZE, RIGHT_PADDING_SIZE)

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
        P = ec.starting_point
        numbers = plain_text.numbers
        pairs: list[ECElGamalCiphertextPair] = []

        for number in numbers:
            M = convert_plain_number_to_point_on_curve(BIT_PADDING_CONFIG, ec, number)
            k = randrange(ec.p // 2, ec.p)
            M1 = ec.scale_point(k, P)
            M2 = ec.add_points(M, ec.scale_point(k, B))
            pairs.append(ECElGamalCiphertextPair(M1, M2))
        return ECElGamalCiphertext(pairs)
    
    @override
    def decrypt(self, private_key: ECElGamalPrivateKey, cipher_text: ECElGamalCiphertext) -> Plaintext:
        ec = private_key.ec
        s = private_key.s

        plain_numbers: list[int] = []
        for pair in cipher_text.pairs:
            M1, M2 = pair.M1, pair.M2
            M = ec.add_points(M2, ec.scale_point(-s, M1))
            plain_number = convert_point_on_curve_to_plain_number(BIT_PADDING_CONFIG, ec, M)
            plain_numbers.append(plain_number)
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
