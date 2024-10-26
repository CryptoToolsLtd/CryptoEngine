def compute_bound(bound: int|str) -> int:
    if isinstance(bound, str):
        if bound.endswith('b'):
            bound = bound[:-1]
            bound = 2 ** int(bound) # Pylance could not guaranteet this is int, so we need the following line:
            bound = int(bound)
        else:
            bound = int(bound)
    return bound

def compute_lbound_ubound(lbound: int|str, ubound: int|str, lbound_min: int|None = None) -> tuple[int, int]:
    lbound = compute_bound(lbound)
    ubound = compute_bound(ubound)

    if lbound >= ubound:
        raise ValueError(f"lbound must be less than ubound (lbound = {lbound}, ubound = {ubound})")

    if lbound_min is not None:
        lbound = max(lbound, lbound_min)
        ubound = max(ubound, lbound + 2)

    return lbound, ubound
