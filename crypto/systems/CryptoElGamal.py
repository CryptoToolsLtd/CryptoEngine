CRYPTO_BITS = 1024

RIGHT_PADDING_SIZE = 2
LEFT_PADDING_SIZE = 5

import sys
sys.set_int_max_str_digits(2147483647)

from typing import override
from random import randrange
import unittest

from ..extended_euclidean import inverse
from ..modpower import modpower
from ..primitive_root import is_primitive_root_fast
from ..random_prime_with_fact_of_p_minus_1 import random_prime_with_fact_of_p_minus_1
from ..pubkeyops import CryptoSystem, CryptoSystemTest, Plaintext
from ..bit_padding import pad, unpad, BitPaddingConfig
from ..fact import fact

BIT_PADDING_CONFIG = BitPaddingConfig(LEFT_PADDING_SIZE, RIGHT_PADDING_SIZE)

def convert_plain_number_to_primitive_root(p: int, original_number: int, fact_of_p_minus_1: dict[int, int]) -> int:
    def check_func(candidate: int) -> bool:
        return is_primitive_root_fast(p, candidate, fact_of_p_minus_1)
    padded_number = pad(BIT_PADDING_CONFIG, original_number, check_func)
    if padded_number is None:
        raise RuntimeError(f"Could not find a valid primitive root modulo p = {p} substituting original_number = {original_number}")
    return padded_number

def convert_primitive_root_to_plain_number(primitive_root: int) -> int:
    return unpad(BIT_PADDING_CONFIG, primitive_root)

class TestPrimitiveRootAndPlainNumberConversions(unittest.TestCase):
    def test_validity(self):
        def i(p: int, original: int):
            actual = convert_primitive_root_to_plain_number(convert_plain_number_to_primitive_root(p, original, fact(p - 1)))
            self.assertEqual(actual, original, f'p = {p}, expected = {original}, actual = {actual}')
        i(17, 5)
        i(17, 6)
        i(17, 7)
        i(17, 8)
        i(101, 13)
        i(6106151, 7)

class ElGamalCiphertextPair:
    def __init__(self, y1: int, y2: int):
        self.y1 = y1
        self.y2 = y2
    
    def __repr__(self) -> str:
        return f"ElGamalCiphertextPair(y1 = {self.y1}, y2 = {self.y2})"

class ElGamalCiphertext:
    def __init__(self, cipher_pairs: list[ElGamalCiphertextPair]):
        self.cipher_pairs = list(cipher_pairs)
    
    def __repr__(self) -> str:
        return f"ElGamalCiphertext(\n    {'\n    '.join([str(x) for x in self.cipher_pairs])}\n)"

def ElGamal_generate_keypair(pbits: int) -> tuple[tuple[int, int, int], tuple[int, int], dict[int, int]]:
    p, fact_of_p_minus_1 = random_prime_with_fact_of_p_minus_1(lbound=f"{pbits}b", ubound=f"{pbits + 1}b")
    # alpha = p // 2
    alpha = 2
    while not is_primitive_root_fast(alpha, p, fact_of_p_minus_1):
        alpha += 1
    a = random_prime_with_fact_of_p_minus_1(lbound=p // 3, ubound=p - 1)[0]
    beta = modpower(alpha, a, p)

    return (p, alpha, beta), (p, a), fact_of_p_minus_1

class ElGamalCryptoPublicKey:
    def __init__(self, p: int, alpha: int, beta: int, fact_of_p_minus_1: dict[int, int]):
        self.p = p
        self.alpha = alpha
        self.beta = beta
        self.fact_of_p_minus_1 = dict(fact_of_p_minus_1)
    
    def __repr__(self) -> str:
        return f"ElGamalCryptoPublicKey(p = {self.p}, alpha = {self.alpha}, beta = {self.beta})"

class ElGamalCryptoPrivateKey:
    def __init__(self, p: int, a: int):
        self.p = p
        self.a = a
    
    def __repr__(self) -> str:
        return f"ElGamalCryptoPrivateKey(p = {self.p}, a = {self.a})"

class ElGamalCryptoSystem(CryptoSystem[
    ElGamalCryptoPublicKey,
    ElGamalCryptoPrivateKey,
    ElGamalCiphertext,
]):
    @override
    def generate_keypair(self) -> tuple[ElGamalCryptoPublicKey, ElGamalCryptoPrivateKey]:
        # Note: if pbits is too small, the cryptosystem may not work properly
        # (e.g. the plaintext may not be able to be encrypted or decrypted properly)
        # due to modulo p operations.
        (p, alpha, beta), (p, a), fact_of_p_minus_1 = ElGamal_generate_keypair(CRYPTO_BITS)
        return ElGamalCryptoPublicKey(p, alpha, beta, fact_of_p_minus_1), ElGamalCryptoPrivateKey(p, a)
    
    @override
    def ask_public_key_interactively(self, prompt: str|None = None) -> ElGamalCryptoPublicKey:
        print(prompt)
        p = int(input("Enter p: "))
        alpha = int(input("Enter alpha: "))
        beta = int(input("Enter beta: "))
        return ElGamalCryptoPublicKey(p, alpha, beta, fact(p - 1)) # TODO: do partner need to share fact_of_p_minus_1?
    
    @override
    def ask_plain_text_interactively(self, public_key: ElGamalCryptoPublicKey, prompt: str|None = None) -> Plaintext:
        s = input((prompt or "Enter plaintext") + " (as string): ")
        return Plaintext.from_string(s)

    @override
    def ask_cipher_text_interactively(self, private_key: ElGamalCryptoPrivateKey, prompt: str|None = None) -> ElGamalCiphertext:
        print(prompt)
        N = int(input("Enter number of pairs: "))
        cipher_pairs: list[ElGamalCiphertextPair] = []
        for i in range(0, N):
            print(f"Enter pair {i + 1}: ")
            y1 = int(input("Enter y1: "))
            y2 = int(input("Enter y2: "))
            cipher_pairs.append(ElGamalCiphertextPair(y1, y2))
        return ElGamalCiphertext(cipher_pairs)
    
    @override
    def encrypt(self, public_key: ElGamalCryptoPublicKey, plain_text: Plaintext) -> ElGamalCiphertext:
        p, alpha, beta, fact_of_p_minus_1 = public_key.p, public_key.alpha, public_key.beta, public_key.fact_of_p_minus_1
        def encrypt_number(plain_number: int) -> ElGamalCiphertextPair:
            n = convert_plain_number_to_primitive_root(p, plain_number, fact_of_p_minus_1)

            one_per_n = inverse(n, p)
            if one_per_n is None:
                raise ValueError(f"n is not invertible in Z_p (this should not happen). n = {n}, p = {p}")

            k = randrange(2, p - 1)
            y1 = modpower(alpha, k, p)
            y2 = n * modpower(beta, k, p) % p

            return ElGamalCiphertextPair(y1, y2)
        
        cipher_pairs = [ encrypt_number(plain_number) for plain_number in plain_text.numbers ]
        return ElGamalCiphertext(cipher_pairs)
    
    @override
    def decrypt(self, private_key: ElGamalCryptoPrivateKey, cipher_text: ElGamalCiphertext) -> Plaintext:
        p, a = private_key.p, private_key.a
        def decrypt_number(cipher_pair: ElGamalCiphertextPair) -> int:
            y1 = cipher_pair.y1
            y2 = cipher_pair.y2
            # x = y2 * modpower(y1, p - 1 - a, p) % p
            s = modpower(y1, a, p)
            s = inverse(s, p)
            if s is None:
                raise RuntimeError(f"Could not find s such that y1^a * s = 1 mod p. y1 = {y1}, a = {a}, p = {p}")
            x = y2 * s % p
            return convert_primitive_root_to_plain_number(x)
        
        plain_numbers = [ decrypt_number(cipher_pair) for cipher_pair in cipher_text.cipher_pairs ]
        return Plaintext(plain_numbers)

    @override
    def str2plaintext(self, public_key: ElGamalCryptoPublicKey, string: str) -> Plaintext:
        return Plaintext.from_string(string)
    
    @override
    def plaintext2str(self, private_key: ElGamalCryptoPrivateKey, plain_text: Plaintext) -> str:
        return plain_text.to_string()

class ElGamalCryptoSystemTest(CryptoSystemTest[ElGamalCryptoPublicKey, ElGamalCryptoPrivateKey, ElGamalCiphertext]):
    @override
    def create_crypto_system(self) -> ElGamalCryptoSystem:
        return ElGamalCryptoSystem()
