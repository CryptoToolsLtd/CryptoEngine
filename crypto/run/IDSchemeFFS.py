P_OR_Q_BITS = 2048

from ..random_prime_fast import random_prime_fast
from ..extended_euclidean import inverse
from random import randint
from ..modpower import modpower

from typing import Literal
class Minus1:
    def __pow__(self, n: int) -> Literal[-1] | Literal[1]:
        return 1 if n % 2 == 0 else -1

minus1 = Minus1()

def run_IDSchemeFFS():
    print("Vũ Tùng Lâm 22028235")
    print("Thực hiện thuật toán Feige-Fiat-Shamir (FFS)")
    print()

    print("Bước 1. TA chọn p, q, b, công khai n=pq và b")
    p, q = random_prime_fast(lbound=f"{P_OR_Q_BITS}b", ubound=f"{P_OR_Q_BITS+1}b", takes=2, want_p_congruent_to_3_mod_4=True)
    n = p * q
    print("Công khai n = p * q =", n)
    b = random_prime_fast(lbound="40b", ubound="41b", takes=1)[0]
    print("Công khai b =", b)
    print()

    k = 3 ; t = 1
    print(f"Chọn k = {k}, t = {t}")

    print("Bước 2. A chọn bí mật k số nguyên ngẫu nhiên s_i (0 <= s_i <= n - 1) và k bit ngẫu nhiên b_i")
    sA = [randint(0, n - 1) for _ in range(k)]
    bA = [randint(0, 1) for _ in range(k)]
    vA: list[int] = []
    for s_i, b_i in zip(sA, bA):
        iii = inverse(modpower(s_i, 2, n), n)
        if iii is None:
            raise Exception("Không tìm được nghịch đảo")
        vA.append(minus1 ** b_i * iii)
    
    print("A chọn s_i =", sA)
    print("A chọn b_i =", bA)
    print("A gửi cho TA v_i =", vA)
    print()

    print("Bước 3. B chọn bí mật k số nguyên ngẫu nhiên s_i (0 <= s_i <= n - 1) và k bit ngẫu nhiên b_i")
    sB = [randint(0, n - 1) for _ in range(k)]
    bB = [randint(0, 1) for _ in range(k)]
    vB: list[int] = []
    for s_i, b_i in zip(sB, bB):
        iii = inverse(modpower(s_i, 2, n), n)
        if iii is None:
            raise Exception("Không tìm được nghịch đảo")
        vB.append(minus1 ** b_i * iii)
    
    print("B chọn s_i =", sB)
    print("B chọn b_i =", bB)
    print("B gửi cho TA v_i =", vB)
    print()

    print("Bước 4. B thử A")
    print("A chọn ngẫu nhiên r =", r := randint(0, n - 1))
    print("A chọn ngẫu nhiên bit b =", b := randint(0, 1))
    x = minus1 ** b * r ** 2 % n
    print("A gửi x cho B như một bằng chứng ; x =", x)
    print()
    print("B gửi cho A vector b_i =", bB)
    print()
    y = r
    for i in range(k):
        y = y * modpower(sB[i], bB[i], n) % n
    print("A gửi cho B số y =", y)
    print()
    z = modpower(y, 2, n)
    for i in range(k):
        z = z * modpower(vB[i], bB[i], n) % n
    print("B tính z =", z)
    print()
    z = z % n
    ok = (z == x % n or z == (-x) % n) and z != 0
    print("B kiểm tra z = +/-x mod n, và z != 0:", ok)

    print("=====================================================")
    print(f"Tiết lộ: p = {p}, q = {q}")

if __name__ == "__main__":
    run_IDSchemeFFS()
