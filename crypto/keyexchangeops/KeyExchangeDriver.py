from .KeyExchangeSystem import KeyExchangeSystem, KeyExchangeInitialization
from ..pubkeyops.Plaintext import Plaintext
from ..systems import VigenereCryptoSystem
from ..strint import int2str

class KeyExchangeDriver[PublicKey, PrivateKey]:
    def __init__(self, key_exchange_system: KeyExchangeSystem[PublicKey, PrivateKey]) -> None:
        self.key_exchange_system = key_exchange_system

    def initialize_keys(self) -> KeyExchangeInitialization[PublicKey, PrivateKey]:
        def initializer():
            K1, K2 = self.key_exchange_system.generate_keypair()
            print(f"{self.myName}'s Public Key for Encryption (PKE):")
            print(f"      K1 = {K1}")
            print()
            F1 = self.key_exchange_system.ask_public_key_interactively(f"Please enter {self.friendName}'s PKE")
            return KeyExchangeInitialization(F1, K1, K2)
        
        def non_initializer():
            F1 = self.key_exchange_system.ask_public_key_interactively(f"Please enter {self.friendName}'s PKE")
            K1, K2 = self.key_exchange_system.generate_keypair_from_initializer_public_key(F1)
            print(f"{self.myName}'s Public Key for Encryption (PKE):")
            print(f"      K1 = {K1}")
            print()
            return KeyExchangeInitialization(F1, K1, K2)

        while True:
            ans = input("Are you the Initializer? (y/n): ").strip().upper()
            if ans == "Y":
                return initializer()
            elif ans == "N":
                return non_initializer()
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
    
    def run(self):
        self.myName = input("Your Name: ")
        self.friendName = input("Your Friend's Name: ")

        initialization = self.initialize_keys()

        print()
        print("=" * 79)
        print()
        print("REVEAL PRIVATE KEY:")
        print(f"{self.myName}'s Private Key for Decryption (pKD):")
        print(f"      K2 = {initialization.K2}")

        KAB = int2str( self.key_exchange_system.generate_KAB(initialization) )
        m = "HoiTruongNhanHaiMuoiNamThanhLapTruong"

        v = VigenereCryptoSystem()
        result = v.encrypt(KAB, Plaintext.from_string(m))
        print(f"\nShared key KAB:\n{KAB}\n")
        print(f"Encryption of \"{m}\" using Vigenere cipher with shared key KAB:\n{result}")
