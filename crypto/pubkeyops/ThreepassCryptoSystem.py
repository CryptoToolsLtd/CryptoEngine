# The Massey-Omura cryptosystem utilizing elliptic curves
# embraces the idea of a three-pass protocol.
# https://en.wikipedia.org/wiki/Three-pass_protocol

from .Plaintext import Plaintext
import unittest
from typing import override
import random

class ThreepassCryptoSystem[CryptoPublicInfo, CryptoEncryptionKey, CryptoDecryptionKey, Semiplaintext]:
    """
    This cryptosystem has some public info and two private keys for encryption
    and decryption.

    The public info is essentially some information that both parties have agreed to
    use for private key generation, even before the communication session
    starts.

    For certain public info, there can be a huge (if not infinite) number of
    private key pairs that satisfy that info. This is different from the regular
    public-key cryptosystems (as defined in CryptoSystem.py), where the public key
    and private key almost form a one-to-one relationship.
    """

    def determine_public_info(self) -> CryptoPublicInfo:
        raise NotImplementedError
    
    def ask_public_info_interactively(self, prompt: str|None = None) -> CryptoPublicInfo:
        raise NotImplementedError

    def generate_private_keys(self, public_info: CryptoPublicInfo) -> tuple[CryptoEncryptionKey, CryptoDecryptionKey]:
        raise NotImplementedError

    def ask_plaintext_interactively(self, public_info: CryptoPublicInfo, prompt: str|None = None) -> Plaintext:
        raise NotImplementedError
    
    def ask_semiplaintext_interactively(self, public_info: CryptoPublicInfo, prompt: str|None = None) -> Semiplaintext:
        raise NotImplementedError
    
    def encrypt(self, encryption_key: CryptoEncryptionKey, semiplaintext: Semiplaintext) -> Semiplaintext:
        raise NotImplementedError
    
    def decrypt(self, decryption_key: CryptoDecryptionKey, semiplaintext: Semiplaintext) -> Semiplaintext:
        raise NotImplementedError
    
    def str2plaintext(self, string: str) -> Plaintext:
        raise NotImplementedError
    
    def plaintext2str(self, plain_text: Plaintext) -> str:
        raise NotImplementedError

    def plaintext2semiplaintext(self, public_info: CryptoPublicInfo, plaintext: Plaintext) -> Semiplaintext:
        raise NotImplementedError
    
    def semiplaintext2plaintext(self, public_info: CryptoPublicInfo, semiplaintext: Semiplaintext) -> Plaintext:
        raise NotImplementedError
    
    ############################################################
    # THE FOLLOWING NEED NOT (AND SHOULD NOT) BE REIMPLEMENTED #
    ############################################################

    def convert2semiplaintext(self, public_info: CryptoPublicInfo, s: Plaintext|Semiplaintext|str) -> Semiplaintext:
        if isinstance(s, str):
            s = self.str2plaintext(s)
        if isinstance(s, Plaintext):
            s = self.plaintext2semiplaintext(public_info, s)
        return s
    
    def convert2plaintext(self, public_info: CryptoPublicInfo, s: Plaintext|Semiplaintext|str) -> Plaintext:
        if isinstance(s, str):
            s = self.str2plaintext(s)
        elif isinstance(s, Plaintext):
            pass
        else:
            s = self.semiplaintext2plaintext(public_info, s)
        return s
    
    def convert2str(self, public_info: CryptoPublicInfo, s: Plaintext|Semiplaintext|str) -> str:
        if isinstance(s, str):
            pass
        elif isinstance(s, Plaintext):
            s = s.to_string()
        else:
            s = self.semiplaintext2plaintext(public_info, s)
            s = self.plaintext2str(s)
        return s

class ThreepassCryptoSystemTest[CryptoPublicInfo, CryptoEncryptionKey, CryptoDecryptionKey, Semiplaintext](unittest.TestCase):
    def create_crypto_system(self) -> ThreepassCryptoSystem[CryptoPublicInfo, CryptoEncryptionKey, CryptoDecryptionKey, Semiplaintext]:
        raise NotImplementedError
    
    @override
    def setUp(self):
        try:
            self.crypto_system = self.create_crypto_system()
        except NotImplementedError:
            self.skipTest("create_crypto_system() is not implemented")
    
    def i(self, shuffled: bool = False):
        NUM_ROUNDS = 10
        m = "DZAX"

        PUB = self.crypto_system.determine_public_info()
        x = self.crypto_system.str2plaintext(m)
        ed_pairs: list[tuple[CryptoEncryptionKey, CryptoDecryptionKey]] = []

        assert NUM_ROUNDS >= 1
        for _ in range(0, NUM_ROUNDS):
            e, d = self.crypto_system.generate_private_keys(PUB)
            ed_pairs.append((e, d))
            x = self.crypto_system.encrypt(e, self.crypto_system.convert2semiplaintext(PUB, x))
        
        if shuffled:
            random.shuffle(ed_pairs)
        
        while len(ed_pairs) > 0:
            e, d = ed_pairs.pop()
            x = self.crypto_system.decrypt(d, self.crypto_system.convert2semiplaintext(PUB, x))
        
        x = self.crypto_system.convert2plaintext(PUB, x)
        m2 = self.crypto_system.convert2str(PUB, x)

        self.assertEqual(m2, m)
    
    def test_identity(self):
        self.i(shuffled=False)
    
    def test_commutativity(self):
        self.i(shuffled=True)
