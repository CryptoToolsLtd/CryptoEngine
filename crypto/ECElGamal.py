CRYPTO_BITS = 256
SIGNATURE_BITS = 10

GRANULARITY = 10

RIGHT_PADDING_SIZE = 2
LEFT_PADDING_SIZE = 5

import sys
sys.set_int_max_str_digits(2147483647)

from typing import override
from random import randrange, random
from copy import deepcopy
from .pubkeyops import CryptoSystem, CryptoSystemTest, SignatureSystem, SignatureSystemTest, CryptoSystemAndSignatureSystemTest, PubkeyCommunicationDriver
from .elliptic_curve import EllipticCurve, generate_elliptic_curve_with_number_of_points_being_prime
from .prime import is_prime
from .legendre import legendre
from .modpower import modpower
from .extended_euclidean import inverse
from .strint import str2int, int2str
from .bit_padding import pad, unpad, BitPaddingConfig
from .CHECK_TESTING import CHECK_TESTING

BIT_PADDING_CONFIG = BitPaddingConfig(LEFT_PADDING_SIZE, RIGHT_PADDING_SIZE)

class ECElGamalPlaintext:
    def __init__(self, numbers: list[int]):
        self.numbers = numbers
    
    def __repr__(self) -> str:
        return f"ECElGamalPlaintext(numbers = {self.numbers})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ECElGamalPlaintext):
            return False
        return self.numbers == other.numbers
    
    @staticmethod
    def from_string(string: str) -> "ECElGamalPlaintext":
        plain_numbers: list[int] = []

        accumulation = ""
        for char in string:
            if not char.isalpha():
                raise ValueError("ECElGamalPlaintext can only contain alphabetic characters")
            char = char.upper()
            accumulation += char
            if len(accumulation) == GRANULARITY:
                plain_numbers.append(str2int(accumulation))
                accumulation = ""

        if len(accumulation) > 0:
            plain_numbers.append(str2int(accumulation))

        return ECElGamalPlaintext(plain_numbers)

    def __str__(self):
        result = ""
        for number in self.numbers:
            result += int2str(number)
        return result

def convert_plain_number_to_pair_of_points_on_curve(ec: EllipticCurve, B: tuple[int, int], number: int) -> tuple[tuple[int, int], tuple[int, int]]:
    p, a, b = ec.p, ec.a, ec.b
    P = ec.starting_point
    # Because we always choose curves over F_p with p ≡ 3 mod 4,
    # the encoding scheme is simple. Suppose the plaintext number is m:
    # 1. Pad bits to m to get x till we have f(x) being a quadratic residue mod p,
    #       where f(x) = x^3 + ax + b.
    # 2. Then, we have to find a number y such that y^2 = f(x) mod p.
    #       This equation falls into a special case where p ≡ 3 mod 4 as we
    #       noted earlier, in which it could be easily solved:
    #                   y = ± [f(x)]^(k+1) mod p.
    #       where
    #                   p = 4k + 3 or k = (p - 3) // 4.
    # THIS IS ESSENTIALLY THE SECOND METHOD MENTIONED IN SECTION 3. Imbedding plaintext
    # IN THIS PAPER:
    # https://www.ams.org/journals/mcom/1987-48-177/S0025-5718-1987-0866109-5/S0025-5718-1987-0866109-5.pdf

    f_x = 0
    def check_f_x_being_quadratic_residue_mod_p(x: int) -> bool:
        nonlocal f_x
        f_x = ( modpower(x, 3, p) + a * x + b ) % p
        return legendre(f_x, p) == 1
    
    x = pad(BIT_PADDING_CONFIG, number, check_f_x_being_quadratic_residue_mod_p)
    if x is None:
        raise RuntimeError(f"Could not find a suitable x for the number {number}")
    # We have calculated this earlier
    # f_x = ( modpower(x, 3, p) + a * x + b ) % p
    k = (p - 3) // 4
    y = modpower(f_x, k + 1, p)
    if random() < 0.5:
        y = (p - y) % p

    M = (x, y)
    assert ec.is_point_on_curve(M)

    k = randrange(ec.p // 2, ec.p)
    M1 = ec.scale_point(k, P)
    M2 = ec.add_points(M, ec.scale_point(k, B))
    return M1, M2

def convert_pair_of_points_on_curve_to_plain_number(ec: EllipticCurve, s: int, pair: tuple[tuple[int, int], tuple[int, int]]) -> int:
    M1, M2 = pair
    M = ec.add_points(M2, ec.scale_point(-s, M1))
    x = M[0]
    return unpad(BIT_PADDING_CONFIG, x)


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

class ECElGamalCryptoSystem(CryptoSystem[
    ECElGamalPublicKey,
    ECElGamalPrivateKey,
    ECElGamalCiphertext,
    ECElGamalPlaintext,
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
        ec, B = public_key.ec, public_key.B
        numbers = plain_text.numbers
        pairs: list[tuple[tuple[int, int], tuple[int, int]]] = []

        for number in numbers:
            pairs.append(convert_plain_number_to_pair_of_points_on_curve(ec, B, number))
        return ECElGamalCiphertext(pairs)
    
    @override
    def decrypt(self, private_key: ECElGamalPrivateKey, cipher_text: ECElGamalCiphertext) -> ECElGamalPlaintext:
        ec = private_key.ec
        s = private_key.s

        numbers: list[int] = []
        for pair in cipher_text.pairs:
            numbers.append(convert_pair_of_points_on_curve_to_plain_number(ec, s, pair))
        return ECElGamalPlaintext(numbers)
    
    @override
    def str2plaintext(self, public_key: ECElGamalPublicKey, string: str) -> ECElGamalPlaintext:
        return ECElGamalPlaintext.from_string(string)
    
    @override
    def plaintext2str(self, private_key: ECElGamalPrivateKey, plain_text: ECElGamalPlaintext) -> str:
        return str(plain_text)

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
        return ECElGamalPlaintext.from_string(string)
    
    @override
    def str2plaintext_verifier(self, verifier_key: ECDSASignatureVerifierKey, string: str) -> ECElGamalPlaintext:
        return ECElGamalPlaintext.from_string(string)
    
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
