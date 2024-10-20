from ..extended_euclidean import inverse

def add(p: int, a: int, b: int, P: tuple[int, int], Q: tuple[int, int]) -> tuple[int, int]:
    x1, y1 = P
    x2, y2 = Q
    if x1 % p == 0 and y1 % p == 0:
        return Q
    if x2 % p == 0 and y2 % p == 0:
        return P
    
    if (x1 - x2) % p == 0 and (y1 + y2) % p == 0:
        return (0, 0)
    if (x1 - x2) % p == 0 and (y1 - y2) % p == 0:
        i = inverse(2*y1 % p, p)
        if i is None:
            raise RuntimeError(f"Please review this algorithm. FAIL TEST: 2*y1 must be invertible mod p (2*y1 = {2*y1}, p = {p}, y1 = {y1})")
        lmbda = (3*x1**2 + a) * i % p
    else:
        i = inverse((x2 - x1) % p, p)
        if i is None:
            raise RuntimeError(f"Please review this algorithm. FAIL TEST: (x2 - x1) must be invertible mod p (x2 - x1 = {x2 - x1}, p = {p}, x1 = {x1}, x2 = {x2})")
        lmbda = (y2 - y1) * i % p
    x3 = (lmbda**2 - x1 - x2) % p
    y3 = (lmbda * (x1 - x3) - y1) % p
    return (x3, y3)
