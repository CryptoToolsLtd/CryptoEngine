import sys
sys.set_int_max_str_digits(2147483647) # 2^31 - 1

from .is_prime import is_prime
from ..CHECK_TESTING import CHECK_TESTING
from .boundaries import compute_lbound_ubound
from random import randrange

def random_prime(lbound: int|str, ubound: int|str) -> int:
    lbound, ubound = compute_lbound_ubound(lbound, ubound)

    n = randrange(lbound, ubound)
    while not is_prime(n):
        n = randrange(lbound, ubound)
    return n
    # N = n if n % 2 != 0 else n + 1

    # while n < ubound:
    #     if is_prime(n):
    #         return n
    #     n += 2
    # n = N - 2
    # while n > lbound:
    #     if is_prime(n):
    #         return n
    #     n -= 2
    # raise ValueError(f"Could not find a prime between {lbound} and {ubound}")

if __name__ == "__main__":
    CHECK_TESTING()

    lbound = 100
    if len(sys.argv) == 2:
        ubound = sys.argv[1]
    elif len(sys.argv) >= 3:
        lbound = sys.argv[1]
        ubound = sys.argv[2]
    else:
        ubound = 1000
    
    print(f"Random prime between {lbound} and {ubound}:")
    print()
    print(random_prime(lbound=lbound, ubound=ubound))
