from ..pubkeyops import CryptoSystemAndSignatureSystemTest, PubkeyCommunicationDriver

from ..systems import (
    ECElGamalCryptoSystem, ECDSASignatureSystem,

    ECElGamalPublicKey,
    ECElGamalPrivateKey,
    ECElGamalCiphertext,
    ECDSASignatureSignerKey,
    ECDSASignatureVerifierKey,
)

from typing import override

class ECElGamalCipherWithECDSASignatureSystemTest(CryptoSystemAndSignatureSystemTest[
    ECElGamalPublicKey,
    ECElGamalPrivateKey,
    ECElGamalCiphertext,
    ECDSASignatureSignerKey,
    ECDSASignatureVerifierKey,
]):
    @override
    def create_crypto_system(self) -> ECElGamalCryptoSystem:
        return ECElGamalCryptoSystem()
    
    @override
    def create_signature_system(self) -> ECDSASignatureSystem:
        return ECDSASignatureSystem()

def run_CryptoECElGamal_SignatureECDSA():
    driver = PubkeyCommunicationDriver(ECElGamalCryptoSystem(), ECDSASignatureSystem())
    driver.run()

    # crypto_system = ECElGamalCryptoSystem()
    # signature_system = ECDSASignatureSystem()

    # print("Generating crypto keypair...")
    # K1, K2 = crypto_system.generate_keypair()
    # print("Generating signature keypair...")
    # k1, k2 = signature_system.generate_keypair()

    # print(K1)
    # print(K2)
    # print(k1)
    # print(k2)

    # x_text = "H"
    # print(f"Text x: '{x_text}'")
    # x = crypto_system.str2plaintext(K1, x_text)
    # print(f"Plaintext x: {repr(x)}")

    # encrypted_x = crypto_system.encrypt(K1, x)
    # print(f"Encrypted x: {encrypted_x}")

    # signature_x = signature_system.sign(k1, signature_system.str2plaintext_signer(k1, x_text))
    # print(f"Signature x: {repr(signature_x)}")

    # encrypted_signature_x = crypto_system.encrypt(K1, signature_x)
    # print(f"Encrypted signature x: {encrypted_signature_x}")

    # print()

    # decrypted_x = crypto_system.decrypt(K2, encrypted_x)
    # print(f"Decrypted x: {repr(decrypted_x)}")

    # decrypted_x_text = crypto_system.plaintext2str(K2, decrypted_x)
    # print(f"Decrypted x text: '{decrypted_x_text}'")

    # decrypted_signature_x = crypto_system.decrypt(K2, encrypted_signature_x)
    # print(f"Decrypted signature x: {repr(decrypted_signature_x)}")

    # SUCCESS = signature_system.verify(k2, decrypted_x, decrypted_signature_x)
    # print(f"Verify: {"VALID" if SUCCESS else "NOT AUTHENTIC"}")

    # SUCCESS2 = signature_system.verify(k2, x, signature_x)
    # print(f"Verify: {"VALID" if SUCCESS2 else "NOT AUTHENTIC"}")

    # assert x_text == decrypted_x_text
