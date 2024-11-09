from ..keyexchangeops import KeyExchangeSystem, KeyExchangeInitialization, TestKeyExchangeSystem
from ..systems import ElGamalCryptoSystem, ElGamalCryptoPublicKey, ElGamalCryptoPrivateKey
from ..random_prime_with_fact_of_p_minus_1 import random_prime_with_fact_of_p_minus_1
from ..modpower import modpower
from ..fact import fact
from ..CHECK_TESTING import CHECK_TESTING
from typing import override

class KeyExchangeDHElGamal(KeyExchangeSystem[ElGamalCryptoPublicKey, ElGamalCryptoPrivateKey]):
    def __init__(self) -> None:
        super().__init__()
        self.crypto_system = ElGamalCryptoSystem()
    
    @override
    def generate_keypair(self) -> tuple[ElGamalCryptoPublicKey, ElGamalCryptoPrivateKey]:
        return self.crypto_system.generate_keypair()
    
    @override
    def generate_keypair_from_initializer_public_key(self, F1: ElGamalCryptoPublicKey) -> tuple[ElGamalCryptoPublicKey, ElGamalCryptoPrivateKey]:
        p = F1.p
        fact_of_p_minus_1 = fact(p - 1)
        alpha = F1.alpha

        a = random_prime_with_fact_of_p_minus_1(lbound=p // 3, ubound=p - 1)[0]
        beta = modpower(alpha, a, p)
        
        K1 = ElGamalCryptoPublicKey(p, alpha, beta, fact_of_p_minus_1)
        K2 = ElGamalCryptoPrivateKey(p, a)

        return K1, K2
    
    @override
    def generate_KAB(self, initialization: KeyExchangeInitialization[ElGamalCryptoPublicKey, ElGamalCryptoPrivateKey]) -> int:
        F1, K1, K2 = initialization.F1, initialization.K1, initialization.K2
        beta = F1.beta
        a = K2.a
        p = K1.p
        KAB = modpower(beta, a, p)
        return KAB
    
    @override
    def ask_public_key_interactively(self, prompt: str | None) -> ElGamalCryptoPublicKey:
        return self.crypto_system.ask_public_key_interactively(prompt)

class TestKeyExchangeDHElGamal(TestKeyExchangeSystem[ElGamalCryptoPublicKey, ElGamalCryptoPrivateKey]):
    @override
    def create_key_exchange_system(self) -> KeyExchangeSystem[ElGamalCryptoPublicKey, ElGamalCryptoPrivateKey]:
        return KeyExchangeDHElGamal()

if __name__ == "__main__":
    CHECK_TESTING()
