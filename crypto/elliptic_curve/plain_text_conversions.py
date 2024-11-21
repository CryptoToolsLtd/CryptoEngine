from ..bit_padding import BitPaddingConfig, pad, unpad
from ..elliptic_curve import EllipticCurve
from ..modpower import modpower
from ..find_sq_roots import find_sq_roots

def convert_plain_number_to_point_on_curve(bit_padding_config: BitPaddingConfig, ec: EllipticCurve, number: int) -> tuple[int, int]:
    p, a, b = ec.p, ec.a, ec.b

    f_x = 0
    y = 0
    def check_f_x_being_quadratic_residue_mod_p(x: int) -> bool:
        nonlocal f_x, y
        f_x = ( modpower(x, 3, p) + a * x + b ) % p
        y = find_sq_roots(f_x, p, p % 2 != 0)
        if y is None:
            return False
        y = y[0]
        return True
    
    x = pad(bit_padding_config, number, check_f_x_being_quadratic_residue_mod_p)
    if x is None:
        raise RuntimeError(f"Could not find a suitable x for the number {number}")
    # We have calculated this earlier
    # f_x = ( modpower(x, 3, p) + a * x + b ) % p
    # y = sqrt(f_x) mod p

    M = (x, y)
    assert ec.is_point_on_curve(M)

    return M

def convert_point_on_curve_to_plain_number(bit_padding_config: BitPaddingConfig, ec: EllipticCurve, M: tuple[int, int]) -> int:
    x = M[0]
    return unpad(bit_padding_config, x)
