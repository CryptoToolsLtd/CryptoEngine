SIGNATURE_BITS = 128 # Signature bits must be less than CRYPTO_BITS, otherwise the signature may not be able to be verified properly

import sys
sys.set_int_max_str_digits(2147483647)

from typing import override
from random import randrange

from ..extended_euclidean import inverse
from ..modpower import modpower
from ..fact import fact
from ..pubkeyops import SignatureSystem, SignatureSystemTest, Plaintext

from .CryptoElGamal import ElGamal_generate_keypair, convert_plain_number_to_primitive_root

def sig_get_gamma_of_number_by_index(sig: Plaintext, index: int) -> int:
    return sig.numbers[2 * index]
    
def sig_get_delta_of_number_by_index(sig: Plaintext, index: int) -> int:
    return sig.numbers[2 * index + 1]

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
    def sign(self, signer_key: ElGamalSignatureSignerKey, plain_text: Plaintext) -> Plaintext:
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
        for plain_number in plain_text.numbers:
            signature_numbers.extend(sign_number(plain_number))
        # signature_numbers.extend(sign_number(len(plain_text.plain_numbers)))
        return Plaintext(signature_numbers)
        
    @override
    def verify(self, verifier_key: ElGamalSignatureVerifierKey, plain_text: Plaintext, signature: Plaintext) -> bool:
        p, alpha, beta, fact_of_p_minus_1 = verifier_key.p, verifier_key.alpha, verifier_key.beta, verifier_key.fact_of_p_minus_1

        def verify_number(plain_number: int, gamma: int, delta: int) -> bool:
            x = convert_plain_number_to_primitive_root(p, plain_number, fact_of_p_minus_1)

            LHS = modpower(beta, gamma, p) * modpower(gamma, delta, p) % p
            RHS = modpower(alpha, x, p) % p

            number_signature_ok = (LHS - RHS) % p == 0
            if not number_signature_ok:
                print(f"Signature verification per number failed. LHS = {LHS}, RHS = {RHS}, p = {p}, gamma = {gamma}, delta = {delta}, alpha = {alpha}, x (primitive root) = {x}, plain_number = {plain_number}")
            return (LHS - RHS) % p == 0
        
        N = len(plain_text.numbers)

        if len(signature.numbers) != 2 * N:
            return False
        for i in range(0, N):
            plain_number = plain_text.numbers[i]
            gamma = sig_get_gamma_of_number_by_index(signature, i)
            delta = sig_get_delta_of_number_by_index(signature, i)
            number_signature_ok = verify_number(plain_number, gamma, delta)
            if not number_signature_ok:
                return False
        
        # gamma = sig_get_gamma_of_number_by_index(signature, N)
        # delta = sig_get_delta_of_number_by_index(signature, N)
        # len_signature_ok = verify_number(N, gamma, delta)
        # if not len_signature_ok:
        #     print(f"(verify length failed)")
        #     return False
        return True
    
    @override
    def str2plaintext_signer(self, signer_key: ElGamalSignatureSignerKey, string: str) -> Plaintext:
        return Plaintext.from_string(string)
    
    @override
    def str2plaintext_verifier(self, verifier_key: ElGamalSignatureVerifierKey, string: str) -> Plaintext:
        return Plaintext.from_string(string)

class ElGamalSignatureSystemTest(SignatureSystemTest[ElGamalSignatureSignerKey, ElGamalSignatureVerifierKey]):
    @override
    def create_signature_system(self) -> ElGamalSignatureSystem:
        return ElGamalSignatureSystem()

