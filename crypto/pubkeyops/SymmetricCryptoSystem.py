from .Plaintext import Plaintext
from ..CHECK_TESTING import CHECK_TESTING
import unittest
from typing import override

class SymmetricCryptoSystem[Key, Ciphertext]:
    def encrypt(self, key: Key, plaintext: Plaintext) -> Ciphertext:
        raise NotImplementedError
    
    def decrypt(self, key: Key, ciphertext: Ciphertext) -> Plaintext:
        raise NotImplementedError
    
    def plaintext2key(self, plaintext: Plaintext) -> Key:
        raise NotImplementedError
    
    def key2plaintext(self, key: Key) -> Plaintext:
        raise NotImplementedError
    
    def str2plaintext(self, key: Key, s: str) -> Plaintext:
        raise NotImplementedError
    
    def plaintext2str(self, key: Key, plaintext: Plaintext) -> str:
        raise NotImplementedError

import random
class TestSymmetricCryptoSystem[Key, Ciphertext](unittest.TestCase):
    def create_crypto_system(self) -> SymmetricCryptoSystem[Key, Ciphertext]:
        raise NotImplementedError
    
    @override
    def setUp(self):
        try:
            self.crypto_system = self.create_crypto_system()
        except NotImplementedError:
            self.skipTest("create_crypto_system() is not implemented")

    def test_encrypt_decrypt(self):
        for _ in range(100):
            key = self.crypto_system.plaintext2key(Plaintext([random.randint(120, 999999999)]))
            s = chr(random.randint(66, 90)) + "".join([chr(random.randint(65, 90)) for _ in range(random.randint(0, 4))])
            plaintext = self.crypto_system.str2plaintext(key, s)
            ciphertext = self.crypto_system.encrypt(key, plaintext)
            decrypted_plaintext = self.crypto_system.decrypt(key, ciphertext)
            self.assertEqual(plaintext, decrypted_plaintext)
    
    def test_str2plaintext_plaintext2str(self):
        for _ in range(100):
            key = self.crypto_system.plaintext2key(Plaintext([random.randint(120, 999999999)]))
            s = chr(random.randint(66, 90)) + "".join([chr(random.randint(65, 90)) for _ in range(random.randint(0, 4))])
            plaintext = self.crypto_system.str2plaintext(key, s)
            self.assertEqual(s, self.crypto_system.plaintext2str(key, plaintext))

if __name__ == "__main__":
    CHECK_TESTING()
