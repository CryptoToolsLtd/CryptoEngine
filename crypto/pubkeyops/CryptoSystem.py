import unittest
from typing import override

class CryptoSystem[CryptoPublicKey, CryptoPrivateKey, Ciphertext, Plaintext]:
    def generate_keypair(self) -> tuple[CryptoPublicKey, CryptoPrivateKey]:
        raise NotImplementedError

    def ask_public_key_interactively(self, prompt: str|None = None) -> CryptoPublicKey:
        raise NotImplementedError
    
    def ask_plain_text_interactively(self, public_key: CryptoPublicKey, prompt: str|None = None) -> Plaintext:
        raise NotImplementedError
    
    def ask_cipher_text_interactively(self, private_key: CryptoPrivateKey, prompt: str|None = None) -> Ciphertext:
        raise NotImplementedError
    
    def encrypt(self, public_key: CryptoPublicKey, plain_text: Plaintext) -> Ciphertext:
        raise NotImplementedError
    
    def decrypt(self, private_key: CryptoPrivateKey, cipher_text: Ciphertext) -> Plaintext:
        raise NotImplementedError
    
    def str2plaintext(self, public_key: CryptoPublicKey, string: str) -> Plaintext:
        raise NotImplementedError
    
    def plaintext2str(self, private_key: CryptoPrivateKey, plain_text: Plaintext) -> str:
        raise NotImplementedError

class CryptoSystemTest[CryptoPublicKey, CryptoPrivateKey, Ciphertext, Plaintext](unittest.TestCase):
    def create_crypto_system(self) -> CryptoSystem[CryptoPublicKey, CryptoPrivateKey, Ciphertext, Plaintext]:
        raise NotImplementedError

    @override
    def setUp(self):
        try:
            self.crypto_system = self.create_crypto_system()
        except NotImplementedError:
            self.skipTest("create_crypto_system() is not implemented")

    def test_cipher(self):
        K1, K2 = self.crypto_system.generate_keypair()
        x = "DZ"
        encrypted_x = self.crypto_system.encrypt(K1, self.crypto_system.str2plaintext(K1, x))
        decrypted_x = self.crypto_system.decrypt(K2, encrypted_x)
        self.assertEqual(x, self.crypto_system.plaintext2str(K2, decrypted_x))
