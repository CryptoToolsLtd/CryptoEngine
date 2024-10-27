CRYPTO_BITS = (2048, 2048)
SIGNATURE_BITS = (256, 256)

import sys
sys.set_int_max_str_digits(2147483647)

from typing import override

from .extended_euclidean import extended_euclidean
from .modpower import modpower
from .strint import str2int, int2str
from .prime import random_prime
from .random_prime_fast import random_prime_fast_with_fact_of_p_minus_1
from .pubkeyops import CryptoSystem, CryptoSystemTest, SignatureSystem, SignatureSystemTest, CryptoSystemAndSignatureSystemTest, PubkeyCommunicationDriver
from .CHECK_TESTING import CHECK_TESTING

# K1: public: encrypt, (n, e)
# K2: private: decrypt, (n, d)

def RSA_encrypt(K1: tuple[int, int], m: int) -> int:
    n, e = K1
    c = modpower(m, e, n)
    return c

def RSA_decrypt(K2: tuple[int, int], c: int) -> int:
    n, d = K2
    p = modpower(c, d, n)
    return p

def generate_RSA_keypair(
    pbits: int, qbits: int
) -> tuple[tuple[int, int], tuple[int, int]]:
    (p,_), (q,_) = random_prime_fast_with_fact_of_p_minus_1(lbound=2**pbits, ubound=2 ** (pbits + 1), takes=2)
    while q == p:
        q = random_prime(lbound=2**qbits, ubound=2 ** (qbits + 1))
    n = p * q
    phi_n = (p - 1) * (q - 1)

    while True:
        e = random_prime(lbound=2**10, ubound=2**11)
        gcd, d = extended_euclidean(e, phi_n)[:2]
        if gcd == 1:
            break

    if d is None:
        raise RuntimeError(
            f"e mod phi_n is not invertible, i.e. cannot calculate e^(-1) mod phi_n, with e = {e} and phi_n = {phi_n}"
        )
    return (n, e), (n, d)

def h(x: int) -> int:
    return x

def sig(k1: tuple[int, int], x: int) -> int:
    n, a = k1
    # print(f"... running modpower({h(x)},        {a},          {n})")
    return modpower(h(x), a, n)
    # return pow(h(x), a, n)

def ver(k2: tuple[int, int], x: int, y: int) -> bool:
    n, b = k2

    matched = h(x) % n == modpower(y, b, n) % n
    # if not matched:
    #     print("===========================")
    #     print(f"mismatch: {h(x) % n} vs {modpower(y, b, n) % n}")
    #     print(f"k2 = {k2}")
    #     print(f"x = {x}")
    #     print(f"y = {y}")
    #     print("===========================")
    return matched

class RSACryptoSystem(CryptoSystem[tuple[int, int], tuple[int, int], int, int]):
    @override
    def generate_keypair(self) -> tuple[tuple[int, int], tuple[int, int]]:
        return generate_RSA_keypair(CRYPTO_BITS[0], CRYPTO_BITS[1])
    
    @override
    def ask_public_key_interactively(self, prompt: str|None = None) -> tuple[int, int]:
        print(prompt)
        return int(input("n = ")), int(input("e = "))
    
    @override
    def ask_plain_text_interactively(self, public_key: tuple[int, int], prompt: str|None = None) -> int:
        return int(input((prompt or "Enter plaintext") + " (as number): "))

    @override    
    def ask_cipher_text_interactively(self, private_key: tuple[int, int], prompt: str|None = None) -> int:
        return int(input((prompt or "Enter ciphertext") + " (as number): "))
    
    @override
    def encrypt(self, public_key: tuple[int, int], plain_text: int) -> int:
        return RSA_encrypt(public_key, plain_text)
    
    @override
    def decrypt(self, private_key: tuple[int, int], cipher_text: int) -> int:
        return RSA_decrypt(private_key, cipher_text)
    
    @override
    def str2plaintext(self, public_key: tuple[int, int], string: str) -> int:
        return str2int(string)
    
    @override
    def plaintext2str(self, private_key: tuple[int, int], plain_text: int) -> str:
        return int2str(plain_text)

class RSASignatureSystem(SignatureSystem[tuple[int, int], tuple[int, int], int, int]):
    @override
    def generate_keypair(self) -> tuple[tuple[int, int], tuple[int, int]]:
        a, b = generate_RSA_keypair(SIGNATURE_BITS[0], SIGNATURE_BITS[1])
        return b, a
    
    @override
    def ask_verification_key_interactively(self, prompt: str|None = None) -> tuple[int, int]:
        print(prompt)
        return int(input("n = ")), int(input("b = "))
    
    @override
    def sign(self, signer_key: tuple[int, int], plain_text: int) -> int:
        return sig(signer_key, plain_text)
    
    @override
    def verify(self, verifier_key: tuple[int, int], plain_text: int, signature: int) -> bool:
        return ver(verifier_key, plain_text, signature)
    
    @override
    def str2plaintext_signer(self, signer_key: tuple[int, int], string: str) -> int:
        return str2int(string)
    
    @override
    def str2plaintext_verifier(self, verifier_key: tuple[int, int], string: str) -> int:
        return str2int(string)
    
    @override
    def signature2plaintext(self, signer_key: tuple[int, int], signature: int) -> int:
        return signature
    
    @override
    def plaintext2signature(self, verifier_key: tuple[int, int], plaintext: int) -> int:
        return plaintext

class RSACryptoSystemTest(CryptoSystemTest[tuple[int, int], tuple[int, int], int, int]):
    @override
    def create_crypto_system(self) -> RSACryptoSystem:
        return RSACryptoSystem()

class RSASignatureSystemTest(SignatureSystemTest[tuple[int, int], tuple[int, int], int, int]):
    @override
    def create_signature_system(self) -> RSASignatureSystem:
        return RSASignatureSystem()

class RSACryptoSystemAndSignatureSystemTest(CryptoSystemAndSignatureSystemTest[tuple[int, int], tuple[int, int], int, int, tuple[int, int], tuple[int, int], int]):
    @override
    def create_crypto_system(self) -> RSACryptoSystem:
        return RSACryptoSystem()
    
    @override
    def create_signature_system(self) -> RSASignatureSystem:
        return RSASignatureSystem()

if __name__ == "__main__":
    CHECK_TESTING()

    driver = PubkeyCommunicationDriver(RSACryptoSystem(), RSASignatureSystem())
    driver.run()
