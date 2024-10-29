SIGNATURE_BITS = 10

import sys
sys.set_int_max_str_digits(2147483647)

from typing import override
from random import randrange
from ..pubkeyops import SignatureSystem, SignatureSystemTest, Plaintext
from ..elliptic_curve import EllipticCurve, generate_elliptic_curve_with_number_of_points_being_prime
from ..prime import is_prime
from ..extended_euclidean import inverse

from .CryptoECElGamal import ask_elliptic_curve_interactively

class ECDSASignatureSignerKey:
    def __init__(self, ec: EllipticCurve, n: int, d: int):
        self.ec = ec
        self.n = n
        self.d = d
    
    def __repr__(self) -> str:
        return f"ECDSASignatureSignerKey(ec = {self.ec}, n = {self.n}, d = {self.d})"

class ECDSASignatureVerifierKey:
    def __init__(self, ec: EllipticCurve, n: int, Q: tuple[int, int]):
        self.ec = ec
        self.n = n
        self.Q = Q
    
    def __repr__(self) -> str:
        return f"ECDSASignatureVerifierKey(ec = {self.ec}, n = {self.n}, Q = {self.Q})"

class ECDSASignatureSystem(SignatureSystem[
    ECDSASignatureSignerKey,
    ECDSASignatureVerifierKey,
]):
    @override
    def generate_keypair(self) -> tuple[ECDSASignatureSignerKey, ECDSASignatureVerifierKey]:
        ec = generate_elliptic_curve_with_number_of_points_being_prime(pbits=SIGNATURE_BITS)
        n = ec.num_points_on_curve
        G = ec.starting_point

        nG = ec.scale_point(n, G)
        # print(f"G = {G}, nG = {nG}, n = {n}, p = {ec.p}")
        assert nG == (0, 0)
        d = randrange(1, n)
        Q = ec.scale_point(d, G)

        signer = ECDSASignatureSignerKey(ec, n, d)
        verifier = ECDSASignatureVerifierKey(ec, n, Q)

        return signer, verifier
    
    @override
    def ask_verification_key_interactively(self, prompt: str|None = None) -> ECDSASignatureVerifierKey:
        if prompt is not None:
            print(prompt)
        ec = ask_elliptic_curve_interactively()
        n = ec.num_points_on_curve
        if not is_prime(n):
            n = int(input("Enter the order of starting point G: "))
        print("Enter Q:")
        Q = (
            int(input("    x_Q = ")),
            int(input("    y_Q = ")),
        )
        return ECDSASignatureVerifierKey(ec, n, Q)
    
    @override
    def sign(self, signer_key: ECDSASignatureSignerKey, plain_text: Plaintext) -> Plaintext:
        ec = signer_key.ec
        n = signer_key.n
        d = signer_key.d
        G = ec.starting_point

        def sign_single(number: int) -> tuple[int, int]:
            s = 0
            r = 0
            while s == 0:
                r = 0
                k = 0
                while r == 0:
                    k = randrange(1, n - 1)
                    x1 = ec.scale_point(k, G)[0]
                    r = x1 % n
                
                h = number # maybe SHA-512 here
                one_per_k_mod_n = inverse(k, n)
                if one_per_k_mod_n is None:
                    raise RuntimeError(f"This case should not happen: Could not find the inverse of {k} mod {n}")

                s = (h + d * r) % n * one_per_k_mod_n % n
            
            return r, s
        
        r_s_pairs = [sign_single(number) for number in plain_text.numbers]
        numbers: list[int] = []
        for r, s in r_s_pairs:
            numbers.append(r)
            numbers.append(s)
        return Plaintext(numbers)
    
    @override
    def verify(self, verifier_key: ECDSASignatureVerifierKey, plain_text: Plaintext, signature: Plaintext) -> bool:
        ec = verifier_key.ec
        n = verifier_key.n
        Q = verifier_key.Q
        G = ec.starting_point

        def verify_single(r: int, s: int, number: int) -> bool:
            if r <= 0 or r >= n or s <= 0 or s >= n:
                return False
            w = inverse(s, n)
            if w is None:
                return False
            h = number
            u1 = h * w % n
            u2 = r * w % n
            x0 = ec.add_points(ec.scale_point(u1, G), ec.scale_point(u2, Q))[0]
            v = x0 % n

            if v != r:
                print(f"SIGNATURE MISMATCH, v = {v}, r = {r}, s = {s}, number = {number}, n = {n}")
            return v == r
        
        for i in range(len(plain_text.numbers)):
            number = plain_text.numbers[i]
            try:
                r = signature.numbers[2 * i]
                s = signature.numbers[2 * i + 1]
            except IndexError:
                return False
            if not verify_single(r, s, number):
                return False

        return True
    
    @override
    def str2plaintext_signer(self, signer_key: ECDSASignatureSignerKey, string: str) -> Plaintext:
        return Plaintext.from_string(string)
    
    @override
    def str2plaintext_verifier(self, verifier_key: ECDSASignatureVerifierKey, string: str) -> Plaintext:
        return Plaintext.from_string(string)

class ECDSASignatureSystemTest(SignatureSystemTest[
    ECDSASignatureSignerKey,
    ECDSASignatureVerifierKey,
]):
    @override
    def create_signature_system(self) -> SignatureSystem[ECDSASignatureSignerKey, ECDSASignatureVerifierKey]:
        return ECDSASignatureSystem()
