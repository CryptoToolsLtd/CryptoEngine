P_BITS = 512
Q_BITS = 512

from ..prime import is_prime, random_prime
from ..random_prime_fast import random_prime_fast_basic
from ..modpower import modpower
from ..extended_euclidean import inverse
from random import randint

def generate_p_q():
    """
    Returns p, q, p1, q1
    """

    candidates: list[int] = []
    def decide_num_candidates():
        base = max(P_BITS // 8, Q_BITS // 8, 32)
        while True:
            yield base
            yield base
            yield base
            yield base // 4
            base *= 2

    NUM_CANDIDATES_GENERATOR = decide_num_candidates()

    def generate_single(p_bits: int):
        p1_bits = p_bits // 2
        while True:
            while len(candidates) > 0:
                p1 = candidates.pop()
                p = p1 * 2 + 1
                if is_prime(p):
                    return p, p1
            N = next(NUM_CANDIDATES_GENERATOR)
            # print(f"Needed to generate {N} more candidates...", end=" ", flush=True)
            more_candidates = random_prime_fast_basic(lbound=f"{p1_bits}b", ubound=f"{p1_bits+1}b", takes=N)
            candidates.extend(more_candidates)
    
    p, p1 = generate_single(P_BITS)
    q, q1 = generate_single(Q_BITS)
    return p, q, p1, q1

def generate_alpha(p1: int, q1: int):
    """
    Returns alpha
    """
    p = 2 * p1 + 1
    q = 2 * q1 + 1
    n = p * q

    alpha = 2
    while True:
        if (
            modpower(alpha, p1, n) != 1 and modpower(alpha, q1, n) != 1 and modpower(alpha, p1*q1, n) != 1
            and
            modpower(alpha, 2*p1, n) != 1 and modpower(alpha, 2*q1, n) != 1 and modpower(alpha, 2*p1*q1, n) == 1
        ):
            return alpha

        if alpha == 2:
            alpha = 3
        else:
            alpha += 2

def generate_e_d(p: int, q: int):
    """
    Returns e, d
    """
    phi_n = (p - 1) * (q - 1)
    while True:
        e = random_prime(lbound=2, ubound=999)
        d = inverse(e, phi_n)
        if e < phi_n and d is not None:
            return e, d

def run_KeyExchangeGirault():
    print("Vũ Tùng Lâm 22028235")
    print("Thực hiện thuật toán Girault")
    print()
    print("Bước 1: Sinh n, p, q, p1, q1")
    p, q, p1, q1 = generate_p_q()
    n = p * q
    print(f"n = {n}")
    print(f"p = {p}")
    print(f"q = {q}")
    print(f"p1 = {p1}")
    print(f"q1 = {q1}")
    print()
    print("Bước 2: Sinh alpha")
    alpha = generate_alpha(p1, q1)
    print(f"alpha = {alpha}")
    print()
    print("Bước 3: Sinh e, d")
    e, d = generate_e_d(p, q)
    print(f"e = {e}")
    print(f"d = {d}")
    print()

    print("Bước 4: A chọn ngẫu nhiên r_A thuộc G, tính s_A = alpha ^ r_A mod n, và gửi cho B:")
    ID_A = 8235 + 10_000
    print(f"ID_A = {ID_A}")
    a_A = randint(1000, 9999)
    a_A = modpower(alpha, a_A, n)
    b_A = modpower(alpha, a_A, n)
    p_A = modpower(b_A - ID_A, d, n)
    print(f"a_A = {a_A}")
    print(f"b_A = {b_A}")
    print(f"p_A = {p_A}")
    r_A = randint(1000, 9999)
    r_A = modpower(alpha, r_A, n)
    s_A = modpower(alpha, r_A, n)
    print(f"s_A = {s_A}")
    print()

    print("Bước 5: B chọn ngẫu nhiên r_B thuộc G, tính s_B = alpha ^ r_B mod n, và gửi cho A:")
    ID_B = 8246 + 10_000
    print(f"ID_B = {ID_B}")
    a_B = randint(1000, 9999)
    a_B = modpower(alpha, a_B, n)
    b_B = modpower(alpha, a_B, n)
    p_B = modpower(b_B - ID_B, d, n)
    print(f"a_B = {a_B}")
    print(f"b_B = {b_B}")
    print(f"p_B = {p_B}")
    r_B = randint(1000, 9999)
    r_B = modpower(alpha, r_B, n)
    s_B = modpower(alpha, r_B, n)
    print(f"s_B = {s_B}")
    print()

    print("Bước 6: A tính k_A = s_B ^ a_A * (p_B ^ e + ID(B))^r_A mod n")
    k_A = modpower(s_B, a_A, n) * modpower(modpower(p_B, e, n) + ID_B, r_A, n) % n
    print(f"k_A = {k_A}")
    print()

    print("Bước 7: B tính k_B = s_A ^ a_B * (p_A ^ e + ID(A))^r_B mod n")
    k_B = modpower(s_A, a_B, n) * modpower(modpower(p_A, e, n) + ID_A, r_B, n) % n
    print(f"k_B = {k_B}")

    print()
    k = modpower(alpha, r_A * a_B + r_B * a_A, n)
    print(f"k = {k}")

    assert k == k_A and k == k_B, "Key was not exchanged correctly"
