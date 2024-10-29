CRYPTO_BITS = (2048, 2048)

import sys
sys.set_int_max_str_digits(2147483647)

from typing import override

from ..extended_euclidean import extended_euclidean
from ..modpower import modpower
from ..prime import random_prime
from ..random_prime_fast import random_prime_fast
from ..pubkeyops import CryptoSystem, CryptoSystemTest, Plaintext

# K1: public: encrypt, (n, e)
# K2: private: decrypt, (n, d)

class RSACryptoPublicKey:
    def __init__(self, n: int, e: int) -> None:
        self.n = n
        self.e = e
    
    def __repr__(self) -> str:
        return f"RSACryptoPublicKey(n = {self.n} , e = {self.e})"

class RSACryptoPrivateKey:
    def __init__(self, n: int, d: int) -> None:
        self.n = n
        self.d = d
    
    def __repr__(self) -> str:
        return f"RSACryptoPrivateKey(n = {self.n} , d = {self.d})"

class RSACryptoCiphertext:
    def __init__(self, numbers: list[int]) -> None:
        self.numbers = list(numbers)
    
    def __repr__(self) -> str:
        return f"RSACryptoCiphertext(<Array [{len(self.numbers)}]>{self.numbers})"

def generate_RSA_keypair(
    pbits: int, qbits: int
) -> tuple[tuple[int, int], tuple[int, int]]:
    p, q = random_prime_fast(lbound=2**pbits, ubound=2 ** (pbits + 1), takes=2)
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

class RSACryptoSystem(CryptoSystem[RSACryptoPublicKey, RSACryptoPrivateKey, RSACryptoCiphertext]):
    @override
    def generate_keypair(self) -> tuple[RSACryptoPublicKey, RSACryptoPrivateKey]:
        (n, e), (n, d) = generate_RSA_keypair(CRYPTO_BITS[0], CRYPTO_BITS[1])
        return RSACryptoPublicKey(n, e), RSACryptoPrivateKey(n, d)
    
    @override
    def ask_public_key_interactively(self, prompt: str|None = None) -> RSACryptoPublicKey:
        print(prompt)
        n, e = int(input("n = ")), int(input("e = "))
        return RSACryptoPublicKey(n, e)
    
    @override
    def ask_plain_text_interactively(self, public_key: RSACryptoPublicKey, prompt: str|None = None) -> Plaintext:
        text_string = input((prompt or "Enter plaintext") + ": ")
        return Plaintext.from_string(text_string)

    @override    
    def ask_cipher_text_interactively(self, private_key: RSACryptoPrivateKey, prompt: str|None = None) -> RSACryptoCiphertext:
        print(prompt)
        N = int(input("Enter the number of ciphertext numbers: "))
        numbers: list[int] = []
        for i in range(N):
            numbers.append(int(input(f"Enter ciphertext number {i + 1}: ")))
        return RSACryptoCiphertext(numbers)
    
    @override
    def encrypt(self, public_key: RSACryptoPublicKey, plain_text: Plaintext) -> RSACryptoCiphertext:
        n, e = public_key.n, public_key.e
        cipher_numbers: list[int] = []
        for m in plain_text.numbers:
            c = modpower(m, e, n)
            cipher_numbers.append(c)
        return RSACryptoCiphertext(cipher_numbers)
    
    @override
    def decrypt(self, private_key: RSACryptoPrivateKey, cipher_text: RSACryptoCiphertext) -> Plaintext:
        n, d = private_key.n, private_key.d
        plain_numbers: list[int] = []
        for c in cipher_text.numbers:
            p = modpower(c, d, n)
            plain_numbers.append(p)
        return Plaintext(plain_numbers)
    
    @override
    def str2plaintext(self, public_key: RSACryptoPublicKey, string: str) -> Plaintext:
        return Plaintext.from_string(string)
    
    @override
    def plaintext2str(self, private_key: RSACryptoPrivateKey, plain_text: Plaintext) -> str:
        return plain_text.to_string()

class RSACryptoSystemTest(CryptoSystemTest[RSACryptoPublicKey, RSACryptoPrivateKey, RSACryptoCiphertext]):
    @override
    def create_crypto_system(self) -> RSACryptoSystem:
        return RSACryptoSystem()
