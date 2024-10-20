from .fact import fact
from .extended_euclidean import inverse
from .modpower import modpower
import unittest
import typing
from .CHECK_TESTING import CHECK_TESTING

def _is_primitive_root_very_trivial(P: int, A: int) -> bool|typing.Literal["unknown"]:
    if P == 1:
        return A == 0

    a = A % P
    if a == 0:
        return False
    return "unknown"

def is_primitive_root_trivial(P: int, A: int) -> bool:
    if P <= 0:
        return False
    a = A % P

    res = _is_primitive_root_very_trivial(P, A)
    if res != "unknown":
        return res

    order = 1
    while a != 1:
        if order > P - 1:
            return False
        a = (a * A) % P
        order += 1
    
    return order == P - 1

def is_primitive_root(P: int, A: int) -> bool:
    if P < 10:
        return is_primitive_root_trivial(P, A)
    a = A % P

    res = _is_primitive_root_very_trivial(P, A)
    if res != "unknown":
        return res
    
    P_1 = P - 1
    FACT_P_1 = fact(P_1)
    for pk in FACT_P_1.keys():
        one_per_pk = inverse(pk, P)
        if one_per_pk is None:
            return False
        if modpower(a, P_1 * one_per_pk % P, P) % P == 1:
            return False
    return True

class TestIsPrimitiveRoot(unittest.TestCase):
    def test(self):
        self.assertEqual( is_primitive_root(1, 0), True )
        self.assertEqual( is_primitive_root(1, 1), False )

        self.assertEqual( is_primitive_root(2, 1), True )
        self.assertEqual( is_primitive_root(2, 2), False )

        self.assertEqual( is_primitive_root(3, 1), False )
        self.assertEqual( is_primitive_root(3, 2), True )

        for a in range(1, 31):
            self.assertEqual( is_primitive_root(31, a), a in [3, 11, 12, 13, 17, 21, 22, 24] )

        for a in range(1, 13):
            self.assertEqual( is_primitive_root(13, a), a in [2, 6, 7, 11] )

if __name__ == "__main__":
    CHECK_TESTING()
