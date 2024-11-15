from .compute_h import compute_h, NotFundamentalDiscriminantError, PRECOMPUTED_TABLE
from .CHECK_TESTING import CHECK_TESTING
from typing import Generator

def generate_fundamental_discriminants_from_scratch(lower_bound: int, upper_bound: int) -> dict[int, list[int]]:
    collection: dict[int, list[int]] = {}
    for D in range(-lower_bound, -upper_bound, -1):
        try:
            h = compute_h(D)
        except NotFundamentalDiscriminantError:
            continue
        collection[h] = collection.get(h, list())
        collection[h].append(D)

    return collection

def generate_fundamental_discriminants_of_increasing_h_D() -> Generator[tuple[int, int], None, None]:
    """
    Yields tuple(h(D), D) of fundamental discriminants D in the order of increasing class numbers h(D).

    It's not strictly in the order of increasing h(D) though.
    When the precomputed table is exhausted, it will generate more discriminants,
    of which the class number might (hopefully!) be smaller than some of the
    previously generated discriminants."""
    for h, LD in enumerate(PRECOMPUTED_TABLE):
        for d in LD:
            yield h, d
    
    lower_bound = upper_bound = 2001

    while True:
        lower_bound = upper_bound
        upper_bound = lower_bound + 20
        collection = generate_fundamental_discriminants_from_scratch(lower_bound, upper_bound)
        for h in sorted(collection.keys()):
            for d in collection[h]:
                yield h, d

if __name__ == "__main__":
    CHECK_TESTING()

    def main():
        for h, d in generate_fundamental_discriminants_of_increasing_h_D():
            print(f"h(d) = {h}      d = {d}")

    main()
