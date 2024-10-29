from . import *
from ..CHECK_TESTING import CHECK_TESTING

import sys
from typing import Callable

CHOICES: dict[str, Callable[[], None]] = {
    "CryptoECElGamal_SignatureECDSA": run_CryptoECElGamal_SignatureECDSA,
    "CryptoElGamal_SignatureElGamal": run_CryptoElGamal_SignatureElGamal,
    "CryptoRSA_SignatureRSA": run_CryptoRSA_SignatureRSA,
}

if __name__ == "__main__":
    CHECK_TESTING()

    if len(sys.argv) >= 2:
        choice = sys.argv[1]
        try:
            func = CHOICES[choice]
        except KeyError:
            print(f"Unknown choice: {choice}")
            print(f"Available choices:\n    {"\n    ".join(CHOICES.keys())}")
            sys.exit(1)
        func()
