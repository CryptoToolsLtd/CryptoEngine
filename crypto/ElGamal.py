CRYPTO_BITS = 1024
SIGNATURE_BITS = 128 # Signature bits must be less than CRYPTO_BITS, otherwise the signature may not be able to be verified properly

GRANULARITY = 10

RIGHT_PADDING_SIZE = 2
LEFT_PADDING_SIZE = 5

import sys
sys.set_int_max_str_digits(2147483647)

from typing import override
from random import randrange
import unittest

from .extended_euclidean import inverse
from .modpower import modpower
from .strint import str2int, int2str
from .primitive_root import is_primitive_root_fast
from .random_prime_with_fact_of_p_minus_1 import random_prime_with_fact_of_p_minus_1
from .pubkeyops import CryptoSystem, CryptoSystemTest, SignatureSystem, SignatureSystemTest, CryptoSystemAndSignatureSystemTest, PubkeyCommunicationDriver
from .bit_padding import pad, unpad, BitPaddingConfig
from .CHECK_TESTING import CHECK_TESTING

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

from .fact import fact
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

class ElGamalPlaintext:
    def __init__(self, plain_numbers: list[int]):
        self.plain_numbers = list(plain_numbers)
    
    def __str__(self) -> str:
        result = ""
        for plain_number in self.plain_numbers:
            result += int2str(plain_number)
        return result
    
    def __repr__(self) -> str:
        return f"ElGamalPlaintext({self.plain_numbers})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ElGamalPlaintext):
            return False
        N = len(self.plain_numbers)
        if N != len(other.plain_numbers):
            return False
        for i in range(0, N):
            if self.plain_numbers[i] != other.plain_numbers[i]:
                return False
        return True
    
    @staticmethod
    def from_string(s: str) -> "ElGamalPlaintext":
        plain_numbers: list[int] = []        

        accumulation = ""
        for char in s:
            if not char.isalpha():
                raise ValueError("ElGamalPlaintext can only contain alphabetic characters")
            char = char.upper()
            accumulation += char
            if len(accumulation) == GRANULARITY:
                plain_numbers.append(str2int(accumulation))
                accumulation = ""
        
        if len(accumulation) > 0:
            plain_numbers.append(str2int(accumulation))

        return ElGamalPlaintext(plain_numbers)

class TestElGamalPlaintext(unittest.TestCase):
    def test_validity(self):
        def i(s: str):
            expected = s
            actual = str(ElGamalPlaintext.from_string(s))
            self.assertEqual(actual, expected, f'expected = {expected}, actual = {actual}')
        i("HELLOWORLD")
        i("HELLO")
        i("WORLD")
        i("INSANELYLONGMESSAGE")

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
    ElGamalPlaintext,
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
    def ask_plain_text_interactively(self, public_key: ElGamalCryptoPublicKey, prompt: str|None = None) -> ElGamalPlaintext:
        s = input((prompt or "Enter plaintext") + " (as string): ")
        return ElGamalPlaintext.from_string(s)

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
    def encrypt(self, public_key: ElGamalCryptoPublicKey, plain_text: ElGamalPlaintext) -> ElGamalCiphertext:
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
        
        cipher_pairs = [ encrypt_number(plain_number) for plain_number in plain_text.plain_numbers ]
        return ElGamalCiphertext(cipher_pairs)
    
    @override
    def decrypt(self, private_key: ElGamalCryptoPrivateKey, cipher_text: ElGamalCiphertext) -> ElGamalPlaintext:
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
        return ElGamalPlaintext(plain_numbers)

    @override
    def str2plaintext(self, public_key: ElGamalCryptoPublicKey, string: str) -> ElGamalPlaintext:
        plain_text = ElGamalPlaintext.from_string(string)
        return plain_text
    
    @override
    def plaintext2str(self, private_key: ElGamalCryptoPrivateKey, plain_text: ElGamalPlaintext) -> str:
        return str(plain_text)

class ElGamalSignature(ElGamalPlaintext):
    def get_gamma_of_number_by_index(self, index: int) -> int:
        return self.plain_numbers[2 * index]
    
    def get_delta_of_number_by_index(self, index: int) -> int:
        return self.plain_numbers[2 * index + 1]

class ElGamalSignatureSignerKey:
    def __init__(self, p: int, alpha: int, a: int, fact_of_p_minus_1: dict[int, int]):
        self.p = p
        self.alpha = alpha
        self.a = a
        self.fact_of_p_minus_1 = dict(fact_of_p_minus_1)
    
    def __repr__(self) -> str:
        return f"ElGamalSignatureSignerKey(p = {self.p}, alpha = {self.alpha}, a = {self.a})"

class ElGamalSignatureVerifierKey:
    def __init__(self, p: int, alpha: int, beta: int, fact_of_p_minus_1: dict[int, int]):
        self.p = p
        self.alpha = alpha
        self.beta = beta
        self.fact_of_p_minus_1 = dict(fact_of_p_minus_1)
    
    def __repr__(self) -> str:
        return f"ElGamalSignatureVerifierKey(p = {self.p}, alpha = {self.alpha}, beta = {self.beta})"

class ElGamalSignatureSystem(SignatureSystem[
    ElGamalSignatureSignerKey,
    ElGamalSignatureVerifierKey,
    ElGamalPlaintext,
    ElGamalSignature,
]):
    @override
    def generate_keypair(self) -> tuple[ElGamalSignatureSignerKey, ElGamalSignatureVerifierKey]:
        (p, alpha, beta), (p, a), fact_of_p_minus_1 = ElGamal_generate_keypair(SIGNATURE_BITS)
        return ElGamalSignatureSignerKey(p, alpha, a, fact_of_p_minus_1), ElGamalSignatureVerifierKey(p, alpha, beta, fact_of_p_minus_1)
    
    @override
    def ask_verification_key_interactively(self, prompt: str|None = None) -> ElGamalSignatureVerifierKey:
        print(prompt)
        p = int(input("Enter p: "))
        alpha = int(input("Enter alpha: "))
        beta = int(input("Enter beta: "))
        return ElGamalSignatureVerifierKey(p, alpha, beta, fact(p - 1)) # TODO: do partner need to share fact_of_p_minus_1?
    
    @override
    def sign(self, signer_key: ElGamalSignatureSignerKey, plain_text: ElGamalPlaintext) -> ElGamalSignature:
        p, alpha, a, fact_of_p_minus_1 = signer_key.p, signer_key.alpha, signer_key.a, signer_key.fact_of_p_minus_1
        p_1 = p - 1

        def sign_number(plain_number: int) -> tuple[int, int]:
            x = convert_plain_number_to_primitive_root(p, plain_number, fact_of_p_minus_1)

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
            return gamma, delta
        
        signature_numbers: list[int] = []
        for plain_number in plain_text.plain_numbers:
            signature_numbers.extend(sign_number(plain_number))
        signature_numbers.extend(sign_number(len(plain_text.plain_numbers)))
        return ElGamalSignature(signature_numbers)
        
    @override
    def verify(self, verifier_key: ElGamalSignatureVerifierKey, plain_text: ElGamalPlaintext, signature: ElGamalSignature) -> bool:
        p, alpha, beta, fact_of_p_minus_1 = verifier_key.p, verifier_key.alpha, verifier_key.beta, verifier_key.fact_of_p_minus_1

        def verify_number(plain_number: int, gamma: int, delta: int) -> bool:
            x = convert_plain_number_to_primitive_root(p, plain_number, fact_of_p_minus_1)

            LHS = modpower(beta, gamma, p) * modpower(gamma, delta, p) % p
            RHS = modpower(alpha, x, p) % p

            number_signature_ok = (LHS - RHS) % p == 0
            if not number_signature_ok:
                print(f"Signature verification per number failed. LHS = {LHS}, RHS = {RHS}, p = {p}, gamma = {gamma}, delta = {delta}, alpha = {alpha}, x (primitive root) = {x}, plain_number = {plain_number}")
            return (LHS - RHS) % p == 0
        
        try:
            N = len(plain_text.plain_numbers)
            for i in range(0, N):
                plain_number = plain_text.plain_numbers[i]
                gamma = signature.get_gamma_of_number_by_index(i)
                delta = signature.get_delta_of_number_by_index(i)
                number_signature_ok = verify_number(plain_number, gamma, delta)
                if not number_signature_ok:
                    return False
            
            gamma = signature.get_gamma_of_number_by_index(N)
            delta = signature.get_delta_of_number_by_index(N)
            len_signature_ok = verify_number(N, gamma, delta)
            if not len_signature_ok:
                print(f"(verify length failed)")
                return False
            return True
        except IndexError as e:
            print(f"IndexError while verifying signature: {e}")
            return False
    
    @override
    def str2plaintext_signer(self, signer_key: ElGamalSignatureSignerKey, string: str) -> ElGamalPlaintext:
        return ElGamalPlaintext.from_string(string)
    
    @override
    def str2plaintext_verifier(self, verifier_key: ElGamalSignatureVerifierKey, string: str) -> ElGamalPlaintext:
        return ElGamalPlaintext.from_string(string)
    
    @override
    def signature2plaintext(self, signer_key: ElGamalSignatureSignerKey, signature: ElGamalSignature) -> ElGamalPlaintext:
        return ElGamalPlaintext(signature.plain_numbers)
    
    @override
    def plaintext2signature(self, verifier_key: ElGamalSignatureVerifierKey, plaintext: ElGamalPlaintext) -> ElGamalSignature:
        return ElGamalSignature(plaintext.plain_numbers)

class ElGamalCryptoSystemTest(CryptoSystemTest[ElGamalCryptoPublicKey, ElGamalCryptoPrivateKey, ElGamalCiphertext, ElGamalPlaintext]):
    @override
    def create_crypto_system(self) -> ElGamalCryptoSystem:
        return ElGamalCryptoSystem()

class ElGamalSignatureSystemTest(SignatureSystemTest[ElGamalSignatureSignerKey, ElGamalSignatureVerifierKey, ElGamalPlaintext, ElGamalSignature]):
    @override
    def create_signature_system(self) -> ElGamalSignatureSystem:
        return ElGamalSignatureSystem()

class ElGamalCryptoSystemAndSignatureSystemTest(CryptoSystemAndSignatureSystemTest[ElGamalCryptoPublicKey, ElGamalCryptoPrivateKey, ElGamalCiphertext, ElGamalPlaintext, ElGamalSignatureSignerKey, ElGamalSignatureVerifierKey, ElGamalSignature]):
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

    x_text = "HAHELLOWORLD"
    print(f"Text x: '{x_text}'")
    print()
    x = crypto_system.str2plaintext(K1, x_text)
    print(f"Plaintext x: {repr(x)}")
    print()

    encrypted_x = crypto_system.encrypt(K1, x)
    print(f"Encrypted x: {encrypted_x}")
    print()

    signature_x = signature_system.sign(k1, signature_system.str2plaintext_signer(k1, x_text))
    print(f"Signature x: {repr(signature_x)}")
    print()

    encrypted_signature_x = crypto_system.encrypt(K1, signature_system.signature2plaintext(k1, signature_x))
    print(f"Encrypted signature x: {encrypted_signature_x}")
    print()

    print()

    decrypted_x = crypto_system.decrypt(K2, encrypted_x)
    print(f"Decrypted x: {repr(decrypted_x)}")
    print()

    decrypted_x_text = crypto_system.plaintext2str(K2, decrypted_x)
    print(f"Decrypted x text: '{decrypted_x_text}'")
    print()

    decrypted_signature_x = crypto_system.decrypt(K2, encrypted_signature_x)
    print(f"Decrypted signature x: {repr(decrypted_signature_x)}")
    print()

    success = signature_system.verify(k2, decrypted_x, signature_system.plaintext2signature(k2, decrypted_signature_x))
    print(f"Verify: {"VALID" if success else "NOT AUTHENTIC"}")
    print()

    success = signature_system.verify(k2, decrypted_x, signature_system.plaintext2signature(k2, signature_x))
    print(f"Verify: {"VALID" if success else "NOT AUTHENTIC"}")
    print()

    success = signature_system.verify(k2, x, signature_system.plaintext2signature(k2, decrypted_signature_x))
    print(f"Verify: {"VALID" if success else "NOT AUTHENTIC"}")
    print()

    success = signature_system.verify(k2, x, signature_system.plaintext2signature(k2, signature_x))
    print(f"Verify: {"VALID" if success else "NOT AUTHENTIC"}")
    print()

    assert x_text == decrypted_x_text
    assert decrypted_signature_x == signature_x, f"decrypted_signature_x = {decrypted_signature_x}, numbers {decrypted_signature_x.plain_numbers}, signature_x = {signature_x}, numbers {signature_x.plain_numbers}"

if __name__ == "__main__":
    CHECK_TESTING()

    driver = PubkeyCommunicationDriver(ElGamalCryptoSystem(), ElGamalSignatureSystem())
    driver.run()

    # main()
