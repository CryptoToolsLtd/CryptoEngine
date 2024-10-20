import unittest
from .CHECK_TESTING import CHECK_TESTING

def str2int(m: str) -> int:
    p = 0
    b = 1
    for i in range(len(m) - 1, -1, -1):
        p_i = ((ord(m[i].upper()) - 65) % 26 + 26) % 26
        p += p_i * b
        b *= 26
    return p

def int2str(p: int) -> str:
    m = ""
    while p > 0:
        r = p % 26
        m = chr(r + 65) + m
        p = (p - r) // 26
    return m

class StrIntConvTest(unittest.TestCase):
    def test_str2int_int2str(self):
        s = "HELLOXINCHAO"
        self.assertEqual(s, int2str(str2int(s)))

        s = "whatawonderfulsubject"
        self.assertEqual(s.upper(), int2str(str2int(s)))

        s = "itishardbutINteresting"
        self.assertEqual(s.upper(), int2str(str2int(s)))

if __name__ == "__main__":
    CHECK_TESTING()
