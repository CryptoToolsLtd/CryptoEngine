import sys
sys.set_int_max_str_digits(2147483647)

from typing import override
from random import randrange
from copy import deepcopy

from .pubkeyops import CryptoSystem, CryptoSystemTest, SignatureSystem, SignatureSystemTest, CryptoSystemAndSignatureSystemTest, PubkeyCommunicationDriver

from .elliptic_curve import EllipticCurve, generate_elliptic_curve_with_number_of_points_being_prime
from .prime import is_prime
from .extended_euclidean import inverse

from .CHECK_TESTING import CHECK_TESTING

class ECElGamalPlaintext:
    def __init__(self, numbers: list[int]):
        self.numbers = numbers
    
    def __repr__(self) -> str:
        return f"ECElGamalPlaintext(numbers = {self.numbers})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ECElGamalPlaintext):
            return False
        return self.numbers == other.numbers

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

class ECElGamalCiphertext:
    def __init__(self, pairs: list[tuple[tuple[int, int], tuple[int, int]]]):
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

def str_to_ECElGamalPlaintext(ec: EllipticCurve, string: str) -> ECElGamalPlaintext:
    string = string.upper()
    numbers: list[int] = []
    for c in string:
        if not c.isalpha():
            raise ValueError(f"Only alphabetic characters are allowed. Found character {c} in string '{string}'.")
        c = ord(c) - ord('A')
        assert c < ec.p
        numbers.append(c)
    return ECElGamalPlaintext(numbers)

def ECElGamalPlaintext_to_str(plain_text: ECElGamalPlaintext) -> str:
    return "".join([chr(c + ord('A')) for c in plain_text.numbers])

class ECElGamalCryptoSystem(CryptoSystem[
    ECElGamalPublicKey,
    ECElGamalPrivateKey,
    ECElGamalCiphertext,
    ECElGamalPlaintext,
]):
    @override
    def generate_keypair(self) -> tuple[ECElGamalPublicKey, ECElGamalPrivateKey]:
        ec = generate_elliptic_curve_with_number_of_points_being_prime(18)
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
    def ask_plain_text_interactively(self, public_key: ECElGamalPublicKey, prompt: str|None = None) -> ECElGamalPlaintext:
        x = input(prompt or "Enter the plaintext message" + " (as text): ")
        numbers: list[int] = []
        for c in x:
            numbers.append(ord(c))
        return ECElGamalPlaintext(numbers)
    
    @override
    def ask_cipher_text_interactively(self, private_key: ECElGamalPrivateKey, prompt: str|None = None) -> ECElGamalCiphertext:
        print(prompt or "Enter the ciphertext:")
        N = int(input("    Enter the number of pairs: "))
        pairs: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for i in range(N):
            print(f"Pair {i + 1}:")
            x1 = int(input("    x_M1: "))
            y1 = int(input("    y_M1: "))
            x2 = int(input("    x_M2: "))
            y2 = int(input("    y_M2: "))

            pairs.append(((x1, y1), (x2, y2)))
        
        return ECElGamalCiphertext(pairs)
    
    @override
    def encrypt(self, public_key: ECElGamalPublicKey, plain_text: ECElGamalPlaintext) -> ECElGamalCiphertext:
        ec = public_key.ec
        P = ec.starting_point
        B = public_key.B
        numbers = plain_text.numbers
        pairs: list[tuple[tuple[int, int], tuple[int, int]]] = []

        def encrypt_single(number: int) -> tuple[tuple[int, int], tuple[int, int]]:
            M = ec.get_point_by_index(number)

            k = randrange(ec.p // 2, ec.p)
            M1 = ec.scale_point(k, P)
            M2 = ec.add_points(M, ec.scale_point(k, B))
            return M1, M2

        for number in numbers:
            pairs.append(encrypt_single(number))
        return ECElGamalCiphertext(pairs)
    
    @override
    def decrypt(self, private_key: ECElGamalPrivateKey, cipher_text: ECElGamalCiphertext) -> ECElGamalPlaintext:
        ec = private_key.ec
        s = private_key.s

        def decrypt_single(pair: tuple[tuple[int, int], tuple[int, int]]) -> int:
            M1, M2 = pair
            M = ec.add_points(M2, ec.scale_point(-s, M1))
            P = ec.starting_point
            c = ec.search_point(M, P, 128, 0) # because 128 = 2^7 ; ECDSA below uses 5-bit p elliptic curve.
            if c is None:
                raise RuntimeError(f"Decryption failed. Could not find the point {M} on the curve {ec}.")
            return c
        
        numbers: list[int] = []
        for pair in cipher_text.pairs:
            numbers.append(decrypt_single(pair))
        return ECElGamalPlaintext(numbers)
    
    @override
    def str2plaintext(self, public_key: ECElGamalPublicKey, string: str) -> ECElGamalPlaintext:
        return str_to_ECElGamalPlaintext(public_key.ec, string)
    
    @override
    def plaintext2str(self, private_key: ECElGamalPrivateKey, plain_text: ECElGamalPlaintext) -> str:
        return ECElGamalPlaintext_to_str(plain_text)

class ECElGamalCryptoSystemTest(CryptoSystemTest[
    ECElGamalPublicKey,
    ECElGamalPrivateKey,
    ECElGamalCiphertext,
    ECElGamalPlaintext,
]):
    @override
    def create_crypto_system(self) -> CryptoSystem[ECElGamalPublicKey, ECElGamalPrivateKey, ECElGamalCiphertext, ECElGamalPlaintext]:
        return ECElGamalCryptoSystem()

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

class ECDSASignature(ECElGamalPlaintext):
    pass

class ECDSASignatureSystem(SignatureSystem[
    ECDSASignatureSignerKey,
    ECDSASignatureVerifierKey,
    ECElGamalPlaintext,
    ECDSASignature,
]):
    @override
    def generate_keypair(self) -> tuple[ECDSASignatureSignerKey, ECDSASignatureVerifierKey]:
        ec = generate_elliptic_curve_with_number_of_points_being_prime(pbits=5)
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
    def sign(self, signer_key: ECDSASignatureSignerKey, plain_text: ECElGamalPlaintext) -> ECDSASignature:
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
        return ECDSASignature(numbers)
    
    @override
    def verify(self, verifier_key: ECDSASignatureVerifierKey, plain_text: ECElGamalPlaintext, signature: ECDSASignature) -> bool:
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
    def str2plaintext_signer(self, signer_key: ECDSASignatureSignerKey, string: str) -> ECElGamalPlaintext:
        return str_to_ECElGamalPlaintext(signer_key.ec, string)
    
    @override
    def str2plaintext_verifier(self, verifier_key: ECDSASignatureVerifierKey, string: str) -> ECElGamalPlaintext:
        return str_to_ECElGamalPlaintext(verifier_key.ec, string)
    
    @override
    def signature2plaintext(self, signer_key: ECDSASignatureSignerKey, signature: ECDSASignature) -> ECElGamalPlaintext:
        return signature
    
    @override
    def plaintext2signature(self, verifier_key: ECDSASignatureVerifierKey, plaintext: ECElGamalPlaintext) -> ECDSASignature:
        return ECDSASignature(plaintext.numbers)

class ECDSASignatureSystemTest(SignatureSystemTest[
    ECDSASignatureSignerKey,
    ECDSASignatureVerifierKey,
    ECElGamalPlaintext,
    ECDSASignature,
]):
    @override
    def create_signature_system(self) -> SignatureSystem[ECDSASignatureSignerKey, ECDSASignatureVerifierKey, ECElGamalPlaintext, ECDSASignature]:
        return ECDSASignatureSystem()

def main():
    crypto_system = ECElGamalCryptoSystem()
    signature_system = ECDSASignatureSystem()

    print("Generating crypto keypair...")
    K1, K2 = crypto_system.generate_keypair()
    print("Generating signature keypair...")
    k1, k2 = signature_system.generate_keypair()

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

class ECElGamalCipherWithECDSASignatureSystemTest(CryptoSystemAndSignatureSystemTest[
    ECElGamalPublicKey,
    ECElGamalPrivateKey,
    ECElGamalCiphertext,
    ECElGamalPlaintext,
    ECDSASignatureSignerKey,
    ECDSASignatureVerifierKey,
    ECDSASignature,
]):
    @override
    def create_crypto_system(self) -> ECElGamalCryptoSystem:
        return ECElGamalCryptoSystem()
    
    @override
    def create_signature_system(self) -> ECDSASignatureSystem:
        return ECDSASignatureSystem()

if __name__ == "__main__":
    CHECK_TESTING()

    driver = PubkeyCommunicationDriver(ECElGamalCryptoSystem(), ECDSASignatureSystem())
    driver.run()

    # main()
