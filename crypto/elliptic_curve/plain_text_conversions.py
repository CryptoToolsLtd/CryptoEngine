from ..bit_padding import BitPaddingConfig, pad, unpad
from ..elliptic_curve import EllipticCurve
from ..modpower import modpower
from ..legendre import legendre

from random import random

def convert_plain_number_to_point_on_curve(bit_padding_config: BitPaddingConfig, ec: EllipticCurve, number: int) -> tuple[int, int]:
    p, a, b = ec.p, ec.a, ec.b
    # Because we always choose curves over F_p with p ≡ 3 mod 4,
    # the encoding scheme is simple. Suppose the plaintext number is m:
    # 1. Pad bits to m to get x till we have f(x) being a quadratic residue mod p,
    #       where f(x) = x^3 + ax + b.
    # 2. Then, we have to find a number y such that y^2 = f(x) mod p.
    #       This equation falls into a special case where p ≡ 3 mod 4 as we
    #       noted earlier, in which it could easily be solved:
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
    
    x = pad(bit_padding_config, number, check_f_x_being_quadratic_residue_mod_p)
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

    return M

def convert_point_on_curve_to_plain_number(bit_padding_config: BitPaddingConfig, ec: EllipticCurve, M: tuple[int, int]) -> int:
    x = M[0]
    return unpad(bit_padding_config, x)
