from ..keyexchangeops import KeyExchangeSystem, KeyExchangeInitialization, TestKeyExchangeSystem
from ..systems import ECElGamalCryptoSystem, ECElGamalPublicKey, ECElGamalPrivateKey
from ..CHECK_TESTING import CHECK_TESTING

from typing import override
from random import randrange

class KeyExchangeDHECElGamal(KeyExchangeSystem[ECElGamalPublicKey, ECElGamalPrivateKey]):
    def __init__(self):
        super().__init__()
        self.crypto_system = ECElGamalCryptoSystem()
    
    @override
    def generate_keypair(self) -> tuple[ECElGamalPublicKey, ECElGamalPrivateKey]:
        return self.crypto_system.generate_keypair()
    
    @override
    def generate_keypair_from_initializer_public_key(self, F1: ECElGamalPublicKey) -> tuple[ECElGamalPublicKey, ECElGamalPrivateKey]:
        ec = F1.ec
        p = ec.p
        s = randrange(p // 2, p)
        B = ec.get_point_by_index(s)
        K1 = ECElGamalPublicKey(ec=ec, B=B)
        K2 = ECElGamalPrivateKey(ec=ec, s=s)
        return K1, K2
    
    @override
    def generate_KAB(self, initialization: KeyExchangeInitialization[ECElGamalPublicKey, ECElGamalPrivateKey]) -> int:
        F1, K2 = initialization.F1, initialization.K2
        return F1.ec.scale_point(K2.s, F1.B)[0]
    
    @override
    def ask_public_key_interactively(self, prompt: str | None) -> ECElGamalPublicKey:
        return self.crypto_system.ask_public_key_interactively(prompt)

class TestKeyExchangeDHECElGamal(TestKeyExchangeSystem[ECElGamalPublicKey, ECElGamalPrivateKey]):
    @override
    def create_key_exchange_system(self) -> KeyExchangeSystem[ECElGamalPublicKey, ECElGamalPrivateKey]:
        return KeyExchangeDHECElGamal()

if __name__ == "__main__":
    CHECK_TESTING()
