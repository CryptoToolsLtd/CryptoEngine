RIGHT_PADDING_SIZE = 2
LEFT_PADDING_SIZE = 3

import sys
sys.set_int_max_str_digits(2147483647)

from typing import override
from random import randrange
import unittest

from .extended_euclidean import inverse
from .modpower import modpower
from .strint import str2int, int2str
from .primitive_root import is_primitive_root
from .prime import random_prime
from .pubkeyops import CryptoSystem, CryptoSystemTest, SignatureSystem, SignatureSystemTest, CryptoSystemAndSignatureSystemTest, PubkeyCommunicationDriver

from .CHECK_TESTING import CHECK_TESTING

def convert_plaintext_to_primitive_root(p: int, original_number: int) -> int:
    K = original_number.bit_length() + (LEFT_PADDING_SIZE - 1) + RIGHT_PADDING_SIZE
    left_pad_base = (1 << (K + 1))
    x = left_pad_base + original_number << RIGHT_PADDING_SIZE
    for left_pad_additional in range(0, 2 ** (LEFT_PADDING_SIZE - 1)):
        for right_pad in range(0, 2 ** RIGHT_PADDING_SIZE):
                candidate = (left_pad_additional << K) + x + right_pad
                if is_primitive_root(p, candidate):
                    return candidate
    raise RuntimeError(f"Could not find a valid primitive root modulo p = {p} substituting original_number = {original_number}")

def convert_primitive_root_to_plaintext(primitive_root: int) -> int:
    x = primitive_root >> RIGHT_PADDING_SIZE
    x = x & ((1 << (x.bit_length() - LEFT_PADDING_SIZE - 1)) - 1)
    return x

class TestPrimitiveRootAndPlaintextConversions(unittest.TestCase):
    def test_validity(self):
        def i(p: int, original: int):
            actual = convert_primitive_root_to_plaintext(convert_plaintext_to_primitive_root(p, original))
            self.assertEqual(actual, original, f'p = {p}, expected = {original}, actual = {actual}')
        i(17, 5)
        i(17, 6)
        i(17, 7)
        i(17, 8)
        i(101, 13)
        i(6106151, 7)

class ElGamalPlaintext:
    def __init__(self, plain_numbers: tuple[int, int]):
        self.plain_numbers = plain_numbers
    
    def has_second_number(self) -> bool:
        return self.plain_numbers[1] != 0

    def __str__(self) -> str:
        words: list[str] = []

        for plain_number in self.plain_numbers:
            words.append(int2str(plain_number))

        return " ".join(words).rstrip()
    
    def __repr__(self) -> str:
        return f"ElGamalPlaintext({self.plain_numbers})"
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, int):
            return self.plain_numbers[0] == other
        if not isinstance(other, ElGamalPlaintext):
            return False
        return self.plain_numbers == other.plain_numbers
    
    @staticmethod
    def from_string(s: str) -> "ElGamalPlaintext":
        words = s.split(" ")
        if len(words) > 2:
            raise ValueError("ElGamalPlaintext can only contain 2 words")
        
        plain_numbers: list[int] = []
        for word in words:
            i = str2int(word)
            plain_numbers.append(i)
        
        while len(plain_numbers) < 2:
            plain_numbers.append(0)

        return ElGamalPlaintext((plain_numbers[0], plain_numbers[1]))

class TestElGamalPlaintext(unittest.TestCase):
    def test_validity(self):
        def i(s: str, expected: str):
            actual = str(ElGamalPlaintext.from_string(s))
            self.assertEqual(actual, expected, f'expected = {expected}, actual = {actual}')
        i("HELLO WORLD", "HELLO WORLD")
        i("HELLO", "HELLO")
        i(" WORLD", " WORLD")

class ElGamalCiphertextPair:
    def __init__(self, y1: int, y2: int):
        self.y1 = y1
        self.y2 = y2
    
    def __repr__(self) -> str:
        return f"ElGamalCiphertextPair(y1={self.y1}, y2={self.y2})"

class ElGamalCiphertext:
    def __init__(self, cipher_pairs: tuple[ElGamalCiphertextPair, ElGamalCiphertextPair]):
        self.cipher_pairs = cipher_pairs
    
    def __repr__(self) -> str:
        return f"ElGamalCiphertext(({self.cipher_pairs[0]}, {self.cipher_pairs[1]}))"

def ElGamal_generate_keypair(pbits: int) -> tuple[tuple[int, int, int], tuple[int, int]]:
    p = random_prime(lbound=f"{pbits}b", ubound=f"{pbits + 1}b")
    alpha = p // 2
    while not is_primitive_root(alpha, p):
        alpha += 1
    a = random_prime(lbound=p // 3, ubound=p - 1)
    beta = modpower(alpha, a, p)

    return (p, alpha, beta), (p, a)

class ElGamalCryptoSystem(CryptoSystem[
    tuple[int, int, int],   # CryptoPublicKey
    tuple[int, int],        # CryptoPrivateKey
    ElGamalCiphertext,      # Ciphertext
    ElGamalPlaintext,       # Plaintext
]):
    @override
    def generate_keypair(self) -> tuple[tuple[int, int, int], tuple[int, int]]:
        # Note: if pbits is too small, the cryptosystem may not work properly
        # (e.g. the plaintext may not be able to be encrypted or decrypted properly)
        # due to modulo p operations.
        return ElGamal_generate_keypair(27)
    
    @override
    def ask_public_key_interactively(self, prompt: str|None = None) -> tuple[int, int, int]:
        print(prompt)
        p = int(input("Enter p: "))
        alpha = int(input("Enter alpha: "))
        beta = int(input("Enter beta: "))
        return p, alpha, beta
    
    @override
    def ask_plain_text_interactively(self, public_key: tuple[int, int, int], prompt: str|None = None) -> ElGamalPlaintext:
        s = input((prompt or "Enter plaintext") + " (as string): ")
        return ElGamalPlaintext.from_string(s)

    @override
    def ask_cipher_text_interactively(self, private_key: tuple[int, int], prompt: str|None = None) -> ElGamalCiphertext:
        print(prompt)
        print("Enter pair 1")
        y1 = int(input("Enter y1: "))
        y2 = int(input("Enter y2: "))
        print("Enter pair 2")
        z1 = int(input("Enter y1: "))
        z2 = int(input("Enter y2: "))
        return ElGamalCiphertext((
            ElGamalCiphertextPair(y1, y2),
            ElGamalCiphertextPair(z1, z2),
        ))
    
    @override
    def encrypt(self, public_key: tuple[int, int, int], plain_text: ElGamalPlaintext) -> ElGamalCiphertext:
        p, alpha, beta = public_key
        def encrypt_number(plain_number: int) -> ElGamalCiphertextPair:
            if plain_number == 0:
                return ElGamalCiphertextPair(0, 0)
            
            n = convert_plaintext_to_primitive_root(p, plain_number)

            one_per_n = inverse(n, p)
            if one_per_n is None:
                raise ValueError(f"n is not invertible in Z_p (this should not happen). n = {n}, p = {p}")

            k = randrange(2, p - 1)
            y1 = modpower(alpha, k, p)
            y2 = n * modpower(beta, k, p) % p

            return ElGamalCiphertextPair(y1, y2)
        
        cipher_pairs = encrypt_number(plain_text.plain_numbers[0]), encrypt_number(plain_text.plain_numbers[1])
        return ElGamalCiphertext(cipher_pairs)
    
    @override
    def decrypt(self, private_key: tuple[int, int], cipher_text: ElGamalCiphertext) -> ElGamalPlaintext:
        p, a = private_key
        def decrypt_number(cipher_pair: ElGamalCiphertextPair) -> int:
            y1 = cipher_pair.y1
            y2 = cipher_pair.y2
            if y1 == 0 and y2 == 0:
                return 0
            x = y2 * modpower(y1, p - 1 - a, p) % p
            return convert_primitive_root_to_plaintext(x)
        
        plain_numbers = decrypt_number(cipher_text.cipher_pairs[0]), decrypt_number(cipher_text.cipher_pairs[1])
        return ElGamalPlaintext(plain_numbers)

    @override
    def str2plaintext(self, public_key: tuple[int, int, int], string: str) -> ElGamalPlaintext:
        plain_text = ElGamalPlaintext.from_string(string)
        return plain_text
    
    @override
    def plaintext2str(self, private_key: tuple[int, int], plain_text: ElGamalPlaintext) -> str:
        return str(plain_text)

class ElGamalSignature(ElGamalPlaintext):
    def __init__(self, p: int, gamma: int, delta: int):
        super().__init__((gamma, delta))
    
    def get_gamma(self) -> int:
        return self.plain_numbers[0]
    
    def get_delta(self) -> int:
        return self.plain_numbers[1]

class ElGamalSignatureSystem(SignatureSystem[
    tuple[int, int, int],                           # SignatureSignerKey (p, alpha, a)
    tuple[int, int, int],                           # SignatureVerifierKey (p, alpha, beta)
    ElGamalPlaintext,                               # Plaintext
    ElGamalSignature,                               # Signature
]):
    @override
    def generate_keypair(self) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
        (p, alpha, beta), (p, a) = ElGamal_generate_keypair(10)
        return (p, alpha, a), (p, alpha, beta)
    
    @override
    def ask_verification_key_interactively(self, prompt: str|None = None) -> tuple[int, int, int]:
        print(prompt)
        p = int(input("Enter p: "))
        alpha = int(input("Enter alpha: "))
        beta = int(input("Enter beta: "))
        return p, alpha, beta
    
    @override
    def sign(self, signer_key: tuple[int, int, int], plain_text: ElGamalPlaintext) -> ElGamalSignature:
        if plain_text.has_second_number():
            raise ValueError("Cannot sign this type of plaintext.")

        p, alpha, a = signer_key
        p_1 = p - 1
        x = convert_plaintext_to_primitive_root(p, plain_text.plain_numbers[0])

        k = randrange(2, p_1)
        one_per_k = inverse(k, p_1)
        while one_per_k is None:
            k = (k + 1) % (p_1)
            one_per_k = inverse(k, p_1)
        # while True:
        #     k = random_prime(lbound=2, ubound=p_1 - 1)
        #     one_per_k = inverse(k, p_1)
        #     if one_per_k is not None:
        #         break

        gamma = modpower(alpha, k, p)
        delta = (x - a * gamma) % p_1 * one_per_k % p_1
        return ElGamalSignature(p, gamma, delta)
    
    @override
    def verify(self, verifier_key: tuple[int, int, int], plain_text: ElGamalPlaintext, signature: ElGamalSignature) -> bool:
        if plain_text.has_second_number():
            raise ValueError("Cannot verify this type of plaintext.")
        
        p, alpha, beta = verifier_key
        gamma = signature.get_gamma()
        delta = signature.get_delta()
        x = convert_plaintext_to_primitive_root(p, plain_text.plain_numbers[0])

        LHS = modpower(beta, gamma, p) * modpower(gamma, delta, p) % p
        RHS = modpower(alpha, x, p) % p
        signature_ok = (LHS - RHS) % p == 0
        if not signature_ok:
            print(f"Signature verification failed. LHS = {LHS}, RHS = {RHS}")

        return signature_ok
    
    @override
    def str2plaintext_signer(self, signer_key: tuple[int, int, int], string: str) -> ElGamalPlaintext:
        return ElGamalPlaintext.from_string(string)
    
    @override
    def str2plaintext_verifier(self, verifier_key: tuple[int, int, int], string: str) -> ElGamalPlaintext:
        return ElGamalPlaintext.from_string(string)
    
    @override
    def signature2plaintext(self, signer_key: tuple[int, int, int], signature: ElGamalSignature) -> ElGamalPlaintext:
        return signature
    
    @override
    def plaintext2signature(self, verifier_key: tuple[int, int, int], plaintext: ElGamalPlaintext) -> ElGamalSignature:
        p = verifier_key[0]
        return ElGamalSignature(p, plaintext.plain_numbers[0], plaintext.plain_numbers[1])

class ElGamalCryptoSystemTest(CryptoSystemTest[tuple[int, int, int], tuple[int, int], ElGamalCiphertext, ElGamalPlaintext]):
    @override
    def create_crypto_system(self) -> ElGamalCryptoSystem:
        return ElGamalCryptoSystem()

class ElGamalSignatureSystemTest(SignatureSystemTest[tuple[int, int, int], tuple[int, int, int], ElGamalPlaintext, ElGamalSignature]):
    @override
    def create_signature_system(self) -> ElGamalSignatureSystem:
        return ElGamalSignatureSystem()

class ElGamalCryptoSystemAndSignatureSystemTest(CryptoSystemAndSignatureSystemTest[tuple[int, int, int], tuple[int, int], ElGamalCiphertext, ElGamalPlaintext, tuple[int, int, int], tuple[int, int, int], ElGamalSignature]):
    @override
    def create_crypto_system(self) -> ElGamalCryptoSystem:
        return ElGamalCryptoSystem()
    
    @override
    def create_signature_system(self) -> ElGamalSignatureSystem:
        return ElGamalSignatureSystem()

def main():
    crypto_system = ElGamalCryptoSystem()
    signature_system = ElGamalSignatureSystem()

    print("Generating crypto keypair...")
    K1, K2 = crypto_system.generate_keypair()
    print("Generating signature keypair...")
    k1, k2 = signature_system.generate_keypair()

    # p, alpha, beta = K1
    # a = K2[1]
    # k2, k1 = (p, alpha, beta), (p, alpha, a)

    print(K1)
    print(K2)
    print(k1)
    print(k2)

    x_text = "H"
    print(f"Text x: '{x_text}'")
    x = crypto_system.str2plaintext(K1, x_text)
    print(f"Plaintext x: {repr(x)}")

    encrypted_x = crypto_system.encrypt(K1, x)
    print(f"Encrypted x: {encrypted_x}")

    signature_x = signature_system.sign(k1, signature_system.str2plaintext_signer(k1, x_text))
    print(f"Signature x: {repr(signature_x)}")

    encrypted_signature_x = crypto_system.encrypt(K1, signature_system.signature2plaintext(k1, signature_x))
    print(f"Encrypted signature x: {encrypted_signature_x}")

    print()

    decrypted_x = crypto_system.decrypt(K2, encrypted_x)
    print(f"Decrypted x: {repr(decrypted_x)}")

    decrypted_x_text = crypto_system.plaintext2str(K2, decrypted_x)
    print(f"Decrypted x text: '{decrypted_x_text}'")

    decrypted_signature_x = crypto_system.decrypt(K2, encrypted_signature_x)
    print(f"Decrypted signature x: {repr(decrypted_signature_x)}")

    SUCCESS = signature_system.verify(k2, decrypted_x, signature_system.plaintext2signature(k2, decrypted_signature_x))
    print(f"Verify: {"VALID" if SUCCESS else "NOT AUTHENTIC"}")

    SUCCESS2 = signature_system.verify(k2, x, signature_system.plaintext2signature(k2, signature_x))
    print(f"Verify: {"VALID" if SUCCESS2 else "NOT AUTHENTIC"}")

    assert x_text == decrypted_x_text

if __name__ == "__main__":
    CHECK_TESTING()

    driver = PubkeyCommunicationDriver(ElGamalCryptoSystem(), ElGamalSignatureSystem())
    driver.run()

    # main()
