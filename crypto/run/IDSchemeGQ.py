P_OR_Q_BITS = 2048

from ..random_prime_fast import random_prime_fast
from ..extended_euclidean import inverse
from ..systems.SignatureRSA import RSASignatureSystem
from random import randint
from ..modpower import modpower
from ..pubkeyops.Plaintext import Plaintext

def run_IDSchemeGQ():
    print("Vũ Tùng Lâm 22028235")
    print("Thực hiện thuật toán Guillou-Quisquater")
    signature_system = RSASignatureSystem()
    signer_key, verifier_key = signature_system.generate_keypair()

    print("Bước 1. TA chọn p, q, b, công khai n=pq và b")
    p, q = random_prime_fast(lbound=f"{P_OR_Q_BITS}b", ubound=f"{P_OR_Q_BITS+1}b", takes=2)
    n = p * q
    print("Công khai n = p * q =", n)
    b = random_prime_fast(lbound="40b", ubound="41b", takes=1)[0]
    print("Công khai b =", b)
    print()

    print("Bước 2. TA xác lập danh tính của A")
    ID_A = 22028235
    print("ID_A =", ID_A)
    print()

    print("Bước 3. A chọn bí mật số u (0 <= u <= n - 1), tính v = (u^(-1))^b mod n")
    while True:
        u = random_prime_fast(lbound="40b", ubound="41b", takes=1)[0]
        u_inverse = inverse(u, n)
        if u_inverse is not None:
            break
    v = pow(u_inverse, b, n)
    print("A gửi cho TA số u =", u)
    print()

    print("Bước 4: TA tạo s = sig(ID_A, v) và cấp cho A chứng chỉ C(A) = (ID_A, v, s)")
    s = signature_system.sign(signer_key, Plaintext([ID_A, v]))
    print("TA tạo s =", s)
    print("C(A) = (ID_A, v, s)")
    print()

    print("Bước 5: A chọn thêm k và gửi cho B thông tin C(A) và gamma")
    k = randint(0, n - 1)
    gamma = modpower(k, b, n)
    print(f"A chọn k = {k}")
    print(f"A gửi cho B: C(A) = (ID_A={ID_A}, v={v}, s={s}), gamma = {gamma}")
    print()

    print("Bước 6: B kiểm tra chữ ký TA trong chứng chỉ C(A)")
    ok = signature_system.verify(verifier_key, Plaintext([ID_A, v]), s)
    print("B kiểm tra chữ ký TA trong chứng chỉ C(A):", ok)
    print()

    print("Bước 7: B chọn số ngẫu nhiên r (0 <= r <= n - 1) và gửi cho A")
    r = randint(0, n - 1)
    print("B chọn r =", r)
    print()

    print("Bước 8: A tính y = k * u^r mod n và gửi cho B")
    y = k * modpower(u, r, n) % n
    print("A tính y =", y)
    print()

    print("Bước 9: B kiểm tra gamma = v^r * y^b mod n")
    ok = gamma % n == (modpower(v, r, n) * modpower(y, b, n)) % n
    print("B kiểm tra y = gamma^r * s^ID_A mod n:", ok)

    print("=====================================================")
    print(f"Tiết lộ: p = {p}, q = {q}")

if __name__ == "__main__":
    run_IDSchemeGQ()
