from .elliptic_curve import EllipticCurve
from .prime import is_prime

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
