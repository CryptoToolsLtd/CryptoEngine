import sys
from ..CHECK_TESTING import CHECK_TESTING
from . import *

def main_generate(argv: list[str]) -> None:
    if len(argv) >= 2:
        pbits = int(argv[1])
    else:
        pbits = int(input("Enter number of bits for prime p = "))
    ec = generate_elliptic_curve_with_number_of_points_being_prime(pbits)
    print(ec)

if __name__ == "__main__":
    CHECK_TESTING()

    cmd = sys.argv[1]
    if cmd == "generate":
        main_generate([sys.argv[0], *sys.argv[2:]])
    else:
        raise ValueError(f"Unknown command {cmd}")
