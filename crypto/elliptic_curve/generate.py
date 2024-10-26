from ..prime import is_prime, random_prime
from ..modpower import modpower
from .EllipticCurve import EllipticCurve

import sys
from random import randrange

def generate_elliptic_curve_with_number_of_points_being_prime(pbits: int) -> EllipticCurve:
    assert pbits >= 3

    while True:
        p = random_prime(lbound=f"{pbits}b", ubound=f"{pbits+1}b")
        p_is_prime = True

        x = random_prime(lbound=f"{pbits - 1}b", ubound=p)
        y = x
        while (y - x) % p == 0:
            y = random_prime(lbound=f"{pbits - 1}b", ubound=p)
        
        a = randrange(1, p)
        b = (modpower(y, 2, p) - modpower(x, 3, p) - a*x % p) % p

        try:
            ec = EllipticCurve(p, p_is_prime, a, b, (x, y))
        except AssertionError:
            continue
        if is_prime(ec.num_points_on_curve):
            return ec

def main():
    if len(sys.argv) >= 2:
        pbits = int(sys.argv[1])
    else:
        pbits = int(input("Enter number of bits for prime p = "))
    ec = generate_elliptic_curve_with_number_of_points_being_prime(pbits)
    print(ec)

if __name__ == "__main__":
    main()
