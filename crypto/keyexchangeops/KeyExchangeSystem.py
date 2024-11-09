import unittest
from typing import override

class KeyExchangeInitialization[PublicKey, PrivateKey]:
    def __init__(self, F1: PublicKey, K1: PublicKey, K2: PrivateKey):
        self.F1 = F1
        self.K1 = K1
        self.K2 = K2

class KeyExchangeSystem[PublicKey, PrivateKey]:
    def generate_keypair(self) -> tuple[PublicKey, PrivateKey]:
        raise NotImplementedError
    
    def generate_keypair_from_initializer_public_key(self, F1: PublicKey) -> tuple[PublicKey, PrivateKey]:
        raise NotImplementedError
    
    def generate_KAB(self, initialization: KeyExchangeInitialization[PublicKey, PrivateKey]) -> int:
        """Generate the common private (symmetric) key."""
        raise NotImplementedError
    
    def ask_public_key_interactively(self, prompt: str|None) -> PublicKey:
        raise NotImplementedError

class TestKeyExchangeSystem[PublicKey, PrivateKey](unittest.TestCase):
    def create_key_exchange_system(self) -> KeyExchangeSystem[PublicKey, PrivateKey]:
        raise NotImplementedError
    
    @override
    def setUp(self):
        try:
            self.key_exchange_system = self.create_key_exchange_system()
        except NotImplementedError:
            self.skipTest("create_key_exchange_system not implemented")
    
    def test_generate_keypair(self):
        try:
            self.key_exchange_system.generate_keypair()
        except Exception as e:
            self.fail(e)
    
    def test_generate_keypair_from_initializer_public_key(self):
        try:
            F1 = self.key_exchange_system.generate_keypair()[0]
            self.key_exchange_system.generate_keypair_from_initializer_public_key(F1)
        except Exception as e:
            self.fail(e)
    
    def test_generate_KAB(self):
        try:
            F1 = self.key_exchange_system.generate_keypair()[0]
            K1, K2 = self.key_exchange_system.generate_keypair_from_initializer_public_key(F1)
            self.key_exchange_system.generate_KAB(KeyExchangeInitialization(F1, K1, K2))
        except Exception as e:
            self.fail(e)
        
    def test_generate_KAB_2(self):
        try:
            K1, K2 = self.key_exchange_system.generate_keypair()
            F1 = self.key_exchange_system.generate_keypair_from_initializer_public_key(K1)[0]
            self.key_exchange_system.generate_KAB(KeyExchangeInitialization(F1, K1, K2))
        except Exception as e:
            self.fail(e)
