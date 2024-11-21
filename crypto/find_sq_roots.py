from .legendre import legendre

def find_sq_roots(u: int, n: int, n_is_odd_prime: bool) -> tuple[int, int] | None:
    if not n_is_odd_prime or n % 2 == 0:
        raise NotImplementedError("This function only works for odd prime numbers")

    if legendre(u, n) != 1:
        return None
    if n % 4 == 3:
        x = pow(u, (n + 1) // 4, n)
        return (x, n - x)
    if n % 8 == 5:
        v = pow(u, (n - 1) // 4, n)
        if (v * v) % n == u:
            return (v, n - v)
        v = (v * pow(2, (n - 1) // 4, n)) % n
        return (v, n - v)
    if n % 8 == 1:
        x = pow(u, (n - 1) // 4, n)
        return (x, n - x)
    return
