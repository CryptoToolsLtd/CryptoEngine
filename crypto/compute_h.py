from math import sqrt, pi
from decimal import Decimal
from .kronecker import kronecker
from .CHECK_TESTING import CHECK_TESTING
from .fact import fact
import unittest

B = 10_000
EPSILON = Decimal(0.01)


def advance_bound(B: int, delta: Decimal, epsilon: Decimal) -> int:
    return round(B * delta / (delta - epsilon))


class NotFundamentalDiscriminantError(ValueError):
    pass


def is_square_free(n: int) -> bool:
    N = abs(n)
    if N <= 7:
        return True
    f = fact(abs(N))
    if 2 in f:
        del f[2]
    for [_base, exponent] in f.items():
        if exponent >= 2:
            return False
    return True


def check_fundamental_discriminant(D: int) -> None:
    def check_not_divisible_by_squared_primes(D: int) -> None:
        if not is_square_free(D):
            raise NotFundamentalDiscriminantError(D)

    if D > 0:
        raise NotImplementedError("Only negative discriminants are supported")
    if D <= 0 and D >= -2:
        raise NotFundamentalDiscriminantError(D)

    if D % 4 == 1:
        check_not_divisible_by_squared_primes(D)
        return
    elif D % 4 == 0:
        m = D // 4
        if m % 4 == 2 or m % 4 == 3:
            check_not_divisible_by_squared_primes(m)
            return
    raise NotFundamentalDiscriminantError(D)


double_pi = 2 * pi


def compute_K(D: int) -> Decimal:
    check_fundamental_discriminant(D)

    if D < -4:
        w = 2
    elif D == -4:
        w = 4
    elif D == -3:
        w = 6
    else:
        raise NotFundamentalDiscriminantError(D)

    m = D // 4
    if not (D % 4 == 1 or (D % 4 == 0 and (m % 4 == 2 or m % 4 == 3))):
        raise NotFundamentalDiscriminantError(D)

    return Decimal(sqrt(Decimal(abs(D)))) * w / Decimal(double_pi)


def dirichlet_L_function_with_s_equal_to_1(D: int, B0: int, B: int) -> Decimal:
    s = Decimal(0)
    for n in range(B0, B + 1):
        s += kronecker(D, n) / Decimal(n)
    return s


def compute_h(D: int) -> int:
    """
    Computes the class number h(D) of the quadratic field Q(sqrt(D)), where D <= -3.
    Raises NotFundamentalDiscriminantError if D is not a fundamental discriminant.
    """
    K = compute_K(D)
    b0 = 1
    b = B
    epsilon = EPSILON

    h = 0
    while True:
        h += K * dirichlet_L_function_with_s_equal_to_1(D, b0, b)
        i = round(h)
        delta = abs(i - h)
        if delta < epsilon:
            return i
        b0 = b + 1
        b = advance_bound(B, delta, epsilon)


# Generated using SageMath
# [[n for n in range(-1, -2000, -1) if is_fundamental_discriminant(n) and QuadraticField(n, 'a').class_number()==H] for H in range(1, 31)]
# Negative fundamental discriminants D of increasing class numbers h(D) (0 <= h(D) <= 30)
PRECOMPUTED_TABLE: list[list[int]] = [
    [], # yes there is no such D that h(D) = 0
    [-3, -4, -7, -8, -11, -19, -43, -67, -163], # h(D) = 1
    [-15, -20, -24, -35, -40, -51, -52, -88, -91, -115, -123, -148, -187, -232, -235, -267, -403, -427], # h(D) = 2, and so on
    [ -23, -31, -59, -83, -107, -139, -211, -283, -307, -331, -379, -499, -547, -643, -883, -907],
    [ -39, -55, -56, -68, -84, -120, -132, -136, -155, -168, -184, -195, -203, -219, -228, -259, -280, -291, -292, -312, -323, -328, -340, -355, -372, -388, -408, -435, -483, -520, -532, -555, -568, -595, -627, -667, -708, -715, -723, -760, -763, -772, -795, -955, -1003, -1012, -1027, -1227, -1243, -1387, -1411, -1435, -1507, -1555 ],
    [ -47, -79, -103, -127, -131, -179, -227, -347, -443, -523, -571, -619, -683, -691, -739, -787, -947, -1051, -1123, -1723, -1747, -1867 ],
    [ -87, -104, -116, -152, -212, -244, -247, -339, -411, -424, -436, -451, -472, -515, -628, -707, -771, -808, -835, -843, -856, -1048, -1059, -1099, -1108, -1147, -1192, -1203, -1219, -1267, -1315, -1347, -1363, -1432, -1563, -1588, -1603, -1843, -1915, -1963 ],
    [ -71, -151, -223, -251, -463, -467, -487, -587, -811, -827, -859, -1163, -1171, -1483, -1523, -1627, -1787, -1987    ],
]

PRECOMPUTED_TABLE_FOR_TESTING: list[list[int]] = [
    [ -95, -111, -164, -183, -248, -260, -264, -276, -295, -299, -308, -371, -376, -395, -420, -452, -456, -548, -552, -564, -579, -580, -583, -616, -632, -651, -660, -712, -820, -840, -852, -868, -904, -915, -939, -952, -979, -987, -995, -1032, -1043, -1060, -1092, -1128, -1131, -1155, -1195, -1204, -1240, -1252, -1288, -1299, -1320, -1339, -1348, -1380, -1428, -1443, -1528, -1540, -1635, -1651, -1659, -1672, -1731, -1752, -1768, -1771, -1780, -1795, -1803, -1828, -1848, -1864, -1912, -1939, -1947, -1992, -1995 ],
    [-199, -367, -419, -491, -563, -823, -1087, -1187, -1291, -1423, -1579],
    [ -119, -143, -159, -296, -303, -319, -344, -415, -488, -611, -635, -664, -699, -724, -779, -788, -803, -851, -872, -916, -923, -1115, -1268, -1384, -1492, -1576, -1643, -1684, -1688, -1707, -1779, -1819, -1835, -1891, -1923 ],
    [-167, -271, -659, -967, -1283, -1303, -1307, -1459, -1531, -1699],
    [ -231, -255, -327, -356, -440, -516, -543, -655, -680, -687, -696, -728, -731, -744, -755, -804, -888, -932, -948, -964, -984, -996, -1011, -1067, -1096, -1144, -1208, -1235, -1236, -1255, -1272, -1336, -1355, -1371, -1419, -1464, -1480, -1491, -1515, -1547, -1572, -1668, -1720, -1732, -1763, -1807, -1812, -1892, -1955, -1972],
    [-191, -263, -607, -631, -727, -1019, -1451, -1499, -1667, -1907],
    [ -215, -287, -391, -404, -447, -511, -535, -536, -596, -692, -703, -807, -899, -1112, -1211, -1396, -1403, -1527, -1816, -1851, -1883],
    [-239, -439, -751, -971, -1259, -1327, -1427, -1567, -1619],
    [ -399, -407, -471, -559, -584, -644, -663, -740, -799, -884, -895, -903, -943, -1015, -1016, -1023, -1028, -1047, -1139, -1140, -1159, -1220, -1379, -1412, -1416, -1508, -1560, -1595, -1608, -1624, -1636, -1640, -1716, -1860, -1876, -1924, -1983],
    [-383, -991, -1091, -1571, -1663, -1783],
    [-335, -519, -527, -679, -1135, -1172, -1207, -1383, -1448, -1687, -1691, -1927],
    [-311, -359, -919, -1063, -1543, -1831],
    [ -455, -615, -776, -824, -836, -920, -1064, -1124, -1160, -1263, -1284, -1460, -1495, -1524, -1544, -1592, -1604, -1652, -1695, -1739, -1748, -1796, -1880, -1887, -1896, -1928, -1940, -1956],
    [-431, -503, -743, -863, -1931],
    [ -591, -623, -767, -871, -879, -1076, -1111, -1167, -1304, -1556, -1591, -1639, -1903],
    [-647, -1039, -1103, -1279, -1447, -1471, -1811, -1979],
    [-695, -759, -1191, -1316, -1351, -1407, -1615, -1704, -1736, -1743, -1988],
    [-479, -599, -1367],
    [-551, -951, -1247, -1256, -1735, -1832],
    [-983, -1231, -1399, -1607, -1759, -1879, -1999],
    [ -831, -935, -1095, -1311, -1335, -1364, -1455, -1479, -1496, -1623, -1703, -1711, -1855, -1976],
    [-887],
    [-671, -815, -1007, -1844],
]

class TestComputeClassNumber(unittest.TestCase):
    def setUp(self):
        self.L = PRECOMPUTED_TABLE + PRECOMPUTED_TABLE_FOR_TESTING

    def test_against_precomputed_table_L(self):
        for expected_h, LD in enumerate(self.L):
            for D in LD:
                with self.subTest(D=D):
                    actual_h = compute_h(D)
                    self.assertEqual(
                        actual_h,
                        expected_h,
                        f"Expecting h({D}) = {expected_h}, got {actual_h}",
                    )

    def test_generation(self):
        for D in range(-3, -1000, -1):
            try:
                h = compute_h(D)
            except NotFundamentalDiscriminantError:
                for expected_h, LD in enumerate(self.L):
                    with self.subTest(expected_h=expected_h):
                        if D in LD:
                            self.fail(
                                f"Expected h({D}) to be {expected_h}, but it is not a fundamental discriminant"
                            )
            else:
                if h >= len(self.L):
                    # print(f"h({D}) = {h}")
                    continue
                with self.subTest(h=h):
                    self.assertIn(D, self.L[h], f"Expected h({D}) != {h} instead")

    def test_generation_2(self):
        collection: dict[int, list[int]] = {}
        for D in range(-1, -2000, -1):
            try:
                h = compute_h(D)
            except NotFundamentalDiscriminantError:
                continue
            collection[h] = collection.get(h, list())
            collection[h].append(D)

        for h, LD in collection.items():
            with self.subTest(h=h):
                if h >= len(self.L):
                    continue
                self.assertEqual(set(self.L[h]), set(LD))

import sys
if __name__ == "__main__":
    CHECK_TESTING()

    def main():
        if len(sys.argv) > 1:
            D = int(sys.argv[1])
            try:
                print(compute_h(D))
            except NotFundamentalDiscriminantError:
                print(f"{D} is not a fundamental discriminant ; not computing h({D})")
            except NotImplementedError as e:
                print(e)

    main()
