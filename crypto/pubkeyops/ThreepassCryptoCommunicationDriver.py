from .ThreepassCryptoSystem import ThreepassCryptoSystem

class ThreepassCryptoCommunicationDriver[
    CryptoPublicInfo,
    CryptoEncryptionKey,
    CryptoDecryptionKey,
    Semiplaintext,
]:
    def __init__(
        self,
        crypto_system: ThreepassCryptoSystem[CryptoPublicInfo, CryptoEncryptionKey, CryptoDecryptionKey, Semiplaintext],
    ):
        self.crypto_system = crypto_system
    
    def run(self):
        myName = "unknown"
        friendName = "unknown"
        while True:
            ans = input("Are you the Sender or the Receiver? (S=Sender, R=Receiver) > ")
            ans = ans.upper()
            if ans == 'S':
                myName, friendName = "Sender", "Receiver"
            elif ans == 'R':
                myName, friendName = "Receiver", "Sender"
            else:
                print("Invalid choice.")
                continue
            break

        def act_as_sender():
            print("Generating public info...")
            PUB = self.crypto_system.determine_public_info()
            print(f"Public Info ({friendName} must adhere to this):")
            print(PUB)
            print()

            m = input("Text message to send: ")
            E, D = self.crypto_system.generate_private_keys(PUB)
            M = self.crypto_system.convert2semiplaintext(PUB, m)

            M1 = self.crypto_system.encrypt(E, M)
            print(f"Send encrypted message M1: {M1}")

            M2 = self.crypto_system.ask_semiplaintext_interactively(PUB, f"Enter received encrypted message M2 from {friendName}")

            M3 = self.crypto_system.decrypt(D, M2)
            print(f"Send partially-decrypted message M3: {M3}")

            print()
            print("=" * 79)
            print()
            print("REVEAL PRIVATE KEYS:")
            print(f"       m_A      = {E}")
            print(f"       m_A^(-1) = {D}")
            print()
        
        def act_as_receiver():
            PUB = self.crypto_system.ask_public_info_interactively(f"Please enter the Public Info that {friendName} has determined")

            M1 = self.crypto_system.ask_semiplaintext_interactively(PUB, f"Enter received encrypted message M1 from {friendName}")
            E, D = self.crypto_system.generate_private_keys(PUB)

            M2 = self.crypto_system.encrypt(E, M1)
            print(f"Send encrypted message M2: {M2}")

            M3 = self.crypto_system.ask_semiplaintext_interactively(PUB, f"Enter received partially-decrypted message M3 from {friendName}")
            M = self.crypto_system.decrypt(D, M3)
            x = self.crypto_system.convert2plaintext(PUB, M)
            m = x.to_string()

            print()
            print("=" * 79)
            print()
            print("DONE, message received from {friendName} is:")
            print(f"    {m}")
            print(f"    plain number(s): {x}")
            print(f"    point(s) on curve: {M}")
            print()
            print("=" * 79)
            print()
            print()
            print("=" * 79)
            print()

            print("REVEAL PRIVATE KEYS:")
            print(f"       m_B      = {E}")
            print(f"       m_B^(-1) = {D}")
            print()

        if myName == 'Sender':
            act_as_sender()
        else:
            act_as_receiver()
