from ..pubkeyops import Plaintext, SymmetricCryptoSystem, TestSymmetricCryptoSystem
from typing import override
from ..strint import int2str
from ..CHECK_TESTING import CHECK_TESTING

class VigenereCryptoSystem(SymmetricCryptoSystem[str, str]):
    def __init__(self):
        self.alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    @override
    def encrypt(self, key: str, plaintext: Plaintext) -> str:
        L = len(key)
        accumulation = ""
        result = ""

        for number in plaintext.numbers:
            string = int2str(number)
            for c in string:
                accumulation += c
                if len(accumulation) == L:
                    for i in range(L):
                        ch = self.alphabet.index(accumulation[i].upper())
                        kh = self.alphabet.index(key[i].upper())
                        new_ch = (ch + kh) % 26
                        result += self.alphabet[new_ch]
                    accumulation = ""

        for i in range(L):
            try:
                ch = self.alphabet.index(accumulation[i].upper())
                kh = self.alphabet.index(key[i].upper())
                new_ch = (ch + kh) % 26
                result += self.alphabet[new_ch]
            except IndexError:
                break

        return result

    @override
    def decrypt(self, key: str, ciphertext: str) -> Plaintext:
        L = len(key)
        accumulation = ""
        result = ""

        for c in ciphertext:
            accumulation += c
            if len(accumulation) == L:
                for i in range(L):
                    ch = self.alphabet.index(accumulation[i].upper())
                    kh = self.alphabet.index(key[i].upper())
                    new_ch = (ch - kh) % 26
                    result += self.alphabet[new_ch]
                accumulation = ""

        for i in range(L):
            try:
                ch = self.alphabet.index(accumulation[i].upper())
                kh = self.alphabet.index(key[i].upper())
                new_ch = (ch - kh) % 26
                result += self.alphabet[new_ch]
            except IndexError:
                break

        return Plaintext.from_string(result)
    
    @override
    def plaintext2key(self, plaintext: Plaintext) -> str:
        return plaintext.to_string()
    
    @override
    def key2plaintext(self, key: str) -> Plaintext:
        return Plaintext.from_string(key)
    
    def str2plaintext(self, key: str, s: str) -> Plaintext:
        return Plaintext.from_string(s)
    
    def plaintext2str(self, key: str, plaintext: Plaintext) -> str:
        return plaintext.to_string()


class TestVigenereCryptoSystem(TestSymmetricCryptoSystem[str, str]):
    @override
    def create_crypto_system(self) -> VigenereCryptoSystem:
        return VigenereCryptoSystem()

if __name__ == "__main__":
    CHECK_TESTING()
