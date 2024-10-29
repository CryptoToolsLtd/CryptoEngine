from ..modpower import modpower
from .count_points_on_curve import count_points_on_curve_with_prime_modulo
from .add import add
from .double_and_add import double_and_add

class EllipticCurve:
    def __init__(self, p: int, p_is_prime: bool, a: int, b: int, starting_point: tuple[int, int]):
        if not p_is_prime:
            # In the future: add algo to count points on curve with non-prime modulo to support this case!
            raise ValueError("p must be prime")
        self.p = p
        self.a = a
        self.b = b
        self.starting_point = starting_point

        self.num_points_on_curve = count_points_on_curve_with_prime_modulo(p, a, b)

        x, y = starting_point
        assert (4 * modpower(a, 3, p) + 27 * modpower(b, 2, p)) % p != 0
        assert self.is_point_on_curve((x, y))
    
    def __repr__(self) -> str:
        return f"EllipticCurve(p = {self.p}, a = {self.a}, b = {self.b}, starting point P = {self.starting_point})"
    
    def get_point_by_index(self, s: int) -> tuple[int, int]:
        return self.scale_point(s, self.starting_point)
    
    def add_points(self, A: tuple[int, int], B: tuple[int, int]) -> tuple[int, int]:
        return add(self.p, self.a, self.b, A, B)
    
    def scale_point(self, s: int, B: tuple[int, int]) -> tuple[int, int]:
        p = self.p
        a = self.a
        b = self.b
        if s < 0:
            C = (B[0], (p-B[1]) % p)
            s = -s
            x, y = self.scale_point(s, C)
        elif s == 0:
            x, y = (0, 0)
        else:
            x, y = double_and_add(p, a, b, s, B)
        
        assert self.is_point_on_curve((x, y)), f"Point {x, y} is not on the curve {self}"
        return x, y
    
    def search_point(self, B: tuple[int, int], P: tuple[int, int], ubound: int, lbound: int = 0) -> None | int:
        """Returns s such that sP = B. Only search within bounds."""
        if ubound < lbound:
            return None

        o = self.scale_point(lbound, P)
        for s in range(lbound, ubound + 1):
            if o == B:
                return s
            o = self.add_points(o, P)
        return None
    
    def is_point_on_curve(self, point: tuple[int, int]) -> bool:
        x, y = point
        p = self.p
        a = self.a
        b = self.b

        if x % p == 0 and y % p == 0:
            return True

        return (modpower(y, 2, p) - modpower(x, 3, p) - a*x%p - b) % p == 0
