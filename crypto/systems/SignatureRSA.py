SIGNATURE_BITS = (256, 256)

import sys
sys.set_int_max_str_digits(2147483647)

from typing import override

from .CryptoRSA import generate_RSA_keypair
from ..modpower import modpower
from ..pubkeyops import SignatureSystem, SignatureSystemTest, Plaintext

def h(x: int) -> int:
    return x

class RSASignatureSignerKey:
    def __init__(self, n: int, a: int) -> None:
        self.n = n
        self.a = a

class RSASignatureVerifierKey:
    def __init__(self, n: int, b: int) -> None:
        self.n = n
        self.b = b

class RSASignatureSystem(SignatureSystem[RSASignatureSignerKey, RSASignatureVerifierKey]):
    @override
    def generate_keypair(self) -> tuple[RSASignatureSignerKey, RSASignatureVerifierKey]:
        (n, b), (n, a) = generate_RSA_keypair(SIGNATURE_BITS[0], SIGNATURE_BITS[1])
        return RSASignatureSignerKey(n, a), RSASignatureVerifierKey(n, b)
    
    @override
    def ask_verification_key_interactively(self, prompt: str|None = None) -> RSASignatureVerifierKey:
        print(prompt)
        n, b = int(input("n = ")), int(input("b = "))
        return RSASignatureVerifierKey(n, b)
    
    @override
    def sign(self, signer_key: RSASignatureSignerKey, plain_text: Plaintext) -> Plaintext:
        n, a = signer_key.n, signer_key.a
        signed_numbers: list[int] = []
        for x in plain_text.numbers:
            sig = modpower(h(x), a, n)
            signed_numbers.append(sig)
        return Plaintext(signed_numbers)
    
    @override
    def verify(self, verifier_key: RSASignatureVerifierKey, plain_text: Plaintext, signature: Plaintext) -> bool:
        n, b = verifier_key.n, verifier_key.b
        if len(plain_text.numbers) != len(signature.numbers):
            return False
        for i in range(len(plain_text.numbers)):
            x = plain_text.numbers[i]
            y = signature.numbers[i]
            matched = h(x) % n == modpower(y, b, n) % n
            if not matched:
                return False
        return True

    @override
    def str2plaintext_signer(self, signer_key: RSASignatureSignerKey, string: str) -> Plaintext:
        return Plaintext.from_string(string)
    
    @override
    def str2plaintext_verifier(self, verifier_key: RSASignatureVerifierKey, string: str) -> Plaintext:
        return Plaintext.from_string(string)

class RSASignatureSystemTest(SignatureSystemTest[RSASignatureSignerKey, RSASignatureVerifierKey]):
    @override
    def create_signature_system(self) -> RSASignatureSystem:
        return RSASignatureSystem()
