CRYPTO_BITS = 256

RIGHT_PADDING_SIZE = 2
LEFT_PADDING_SIZE = 5

import sys
sys.set_int_max_str_digits(2147483647)

from typing import override
from random import randrange
from ..pubkeyops import ThreepassCryptoSystem, ThreepassCryptoSystemTest, Plaintext
from ..elliptic_curve import (
    EllipticCurve, generate_elliptic_curve_with_number_of_points_being_prime,
    convert_plain_number_to_point_on_curve,
    convert_point_on_curve_to_plain_number,
)
from ..extended_euclidean import inverse
from ..bit_padding import BitPaddingConfig
from ..ask_elliptic_curve_interactively import ask_elliptic_curve_interactively

BIT_PADDING_CONFIG = BitPaddingConfig(LEFT_PADDING_SIZE, RIGHT_PADDING_SIZE)

class MasseyOmuraPublicInfo:
    def __init__(self, ec: EllipticCurve):
        self.ec = ec

    def __repr__(self) -> str:
        return f"{self.ec}"

class MasseyOmuraEncryptionKey:
    def __init__(self, public_info: MasseyOmuraPublicInfo, s: int, gcd_s_cardinality_equals_1: bool):
        if not gcd_s_cardinality_equals_1:
            raise ValueError(f"Invalid")
        self.public_info = public_info
        self.s = s
    
    def __repr__(self) -> str:
        return f"MasseyOmuraEncryptionKey(s = {self.s})"

class MasseyOmuraDecryptionKey:
    def __init__(self, public_info: MasseyOmuraPublicInfo, s_inverse: int):
        self.public_info = public_info
        self.s_inverse = s_inverse
    
    def __repr__(self) -> str:
        return f"MasseyOmuraDecryptionKey(s^(-1) = {self.s_inverse})"

class MasseyOmuraSemiplaintextPoint(tuple[int, int]):
    def __repr__(self) -> str:
        return f"(x = {self[0]} , y = {self[1]})"

class MasseyOmuraSemiplaintext:
    def __init__(self, points: list[MasseyOmuraSemiplaintextPoint]):
        self.points = list(points)
    
    def __repr__(self) -> str:
        return '{\n    ' + "\n    ".join(map(str, self.points)) + '\n}'

class MasseyOmuraCryptoSystem(ThreepassCryptoSystem[
    MasseyOmuraPublicInfo,
    MasseyOmuraEncryptionKey,
    MasseyOmuraDecryptionKey,
    MasseyOmuraSemiplaintext,
]):
    @override
    def determine_public_info(self) -> MasseyOmuraPublicInfo:
        ec = generate_elliptic_curve_with_number_of_points_being_prime(CRYPTO_BITS)
        return MasseyOmuraPublicInfo(ec=ec)

    @override
    def ask_public_info_interactively(self, prompt: str|None = None) -> MasseyOmuraPublicInfo:
        if prompt is not None:
            print(prompt)
        ec = ask_elliptic_curve_interactively()
        return MasseyOmuraPublicInfo(ec=ec)
    
    @override
    def generate_private_keys(self, public_info: MasseyOmuraPublicInfo) -> tuple[MasseyOmuraEncryptionKey, MasseyOmuraDecryptionKey]:
        ec = public_info.ec
        N = ec.num_points_on_curve
        while True:
            s = randrange(2, N)
            s_inverse = inverse(s, N)
            if s_inverse is not None:
                break
        
        return (
            MasseyOmuraEncryptionKey(public_info, s, gcd_s_cardinality_equals_1=True),
            MasseyOmuraDecryptionKey(public_info, s_inverse),
        )
    
    @override
    def ask_plaintext_interactively(self, public_info: MasseyOmuraPublicInfo, prompt: str | None = None) -> Plaintext:
        text_string = input(prompt or "Enter the plaintext message" + " (as text): ")
        return Plaintext.from_string(text_string)
    
    @override
    def ask_semiplaintext_interactively(self, public_info: MasseyOmuraPublicInfo, prompt: str | None = None) -> MasseyOmuraSemiplaintext:
        print(prompt or "Enter the ciphertext:")
        NUM_POINTS = int(input("    Enter the number of points: "))
        return MasseyOmuraSemiplaintext(
            [
                MasseyOmuraSemiplaintextPoint((
                    int(input(f"Point {i+1} x = ")),
                    int(input(" " * len(f"Point {i+1} ") + f"y = "))
                )) for i in range(NUM_POINTS)
            ]
        )
    
    @override
    def encrypt(self, encryption_key: MasseyOmuraEncryptionKey, semiplaintext: MasseyOmuraSemiplaintext) -> MasseyOmuraSemiplaintext:
        ec = encryption_key.public_info.ec
        s = encryption_key.s
        return MasseyOmuraSemiplaintext([
            MasseyOmuraSemiplaintextPoint( ec.scale_point(s, M) )
            for M in semiplaintext.points
        ])
    
    @override
    def decrypt(self, decryption_key: MasseyOmuraDecryptionKey, semiplaintext: MasseyOmuraSemiplaintext) -> MasseyOmuraSemiplaintext:
        ec = decryption_key.public_info.ec
        s_inverse = decryption_key.s_inverse

        return MasseyOmuraSemiplaintext([
            MasseyOmuraSemiplaintextPoint( ec.scale_point(s_inverse, M) )
            for M in semiplaintext.points
        ])
    
    @override
    def str2plaintext(self, string: str) -> Plaintext:
        return Plaintext.from_string(string)
    
    @override
    def plaintext2str(self, plain_text: Plaintext) -> str:
        return plain_text.to_string()
    
    @override
    def plaintext2semiplaintext(self, public_info: MasseyOmuraPublicInfo, plaintext: Plaintext) -> MasseyOmuraSemiplaintext:
        ec = public_info.ec
        return MasseyOmuraSemiplaintext([
            MasseyOmuraSemiplaintextPoint(
                convert_plain_number_to_point_on_curve(BIT_PADDING_CONFIG, ec, plain_number)
            )

            for plain_number in plaintext.numbers
        ])
    
    @override
    def semiplaintext2plaintext(self, public_info: MasseyOmuraPublicInfo, semiplaintext: MasseyOmuraSemiplaintext) -> Plaintext:
        ec = public_info.ec
        return Plaintext([
            convert_point_on_curve_to_plain_number(BIT_PADDING_CONFIG, ec, M)
            for M in semiplaintext.points
        ])

class MasseyOmuraCryptoSystemTest(ThreepassCryptoSystemTest[
    MasseyOmuraPublicInfo,
    MasseyOmuraEncryptionKey,
    MasseyOmuraDecryptionKey,
    MasseyOmuraSemiplaintext,
]):
    @override
    def create_crypto_system(self) -> ThreepassCryptoSystem[MasseyOmuraPublicInfo, MasseyOmuraEncryptionKey, MasseyOmuraDecryptionKey, MasseyOmuraSemiplaintext]:
        return MasseyOmuraCryptoSystem()
