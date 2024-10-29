from ..pubkeyops import (
    CryptoSystemAndSignatureSystemTest,
    PubkeyCommunicationDriver,
)
from ..systems import (
    ElGamalCryptoSystem, ElGamalSignatureSystem,
    ElGamalCryptoPublicKey, ElGamalCryptoPrivateKey, ElGamalCiphertext,
    ElGamalSignatureSignerKey, ElGamalSignatureVerifierKey,
)

from typing import override

class ElGamalCryptoSystemAndSignatureSystemTest(CryptoSystemAndSignatureSystemTest[ElGamalCryptoPublicKey, ElGamalCryptoPrivateKey, ElGamalCiphertext, ElGamalSignatureSignerKey, ElGamalSignatureVerifierKey]):
    @override
    def create_crypto_system(self) -> ElGamalCryptoSystem:
        return ElGamalCryptoSystem()
    
    @override
    def create_signature_system(self) -> ElGamalSignatureSystem:
        return ElGamalSignatureSystem()

def run_CryptoElGamal_SignatureElGamal():
    driver = PubkeyCommunicationDriver(ElGamalCryptoSystem(), ElGamalSignatureSystem())
    driver.run()

    # crypto_system = ElGamalCryptoSystem()
    # signature_system = ElGamalSignatureSystem()

    # print("Generating crypto keypair...")
    # K1, K2 = crypto_system.generate_keypair()
    # print("Generating signature keypair...")
    # k1, k2 = signature_system.generate_keypair()

    # # p, alpha, beta = K1
    # # a = K2[1]
    # # k2, k1 = (p, alpha, beta), (p, alpha, a)

    # print(K1)
    # print(K2)
    # print(k1)
    # print(k2)

    # x_text = "HAHELLOWORLD"
    # print(f"Text x: '{x_text}'")
    # print()
    # x = crypto_system.str2plaintext(K1, x_text)
    # print(f"Plaintext x: {repr(x)}")
    # print()

    # encrypted_x = crypto_system.encrypt(K1, x)
    # print(f"Encrypted x: {encrypted_x}")
    # print()

    # signature_x = signature_system.sign(k1, signature_system.str2plaintext_signer(k1, x_text))
    # print(f"Signature x: {repr(signature_x)}")
    # print()

    # encrypted_signature_x = crypto_system.encrypt(K1, signature_x)
    # print(f"Encrypted signature x: {encrypted_signature_x}")
    # print()

    # print()

    # decrypted_x = crypto_system.decrypt(K2, encrypted_x)
    # print(f"Decrypted x: {repr(decrypted_x)}")
    # print()

    # decrypted_x_text = crypto_system.plaintext2str(K2, decrypted_x)
    # print(f"Decrypted x text: '{decrypted_x_text}'")
    # print()

    # decrypted_signature_x = crypto_system.decrypt(K2, encrypted_signature_x)
    # print(f"Decrypted signature x: {repr(decrypted_signature_x)}")
    # print()

    # success = signature_system.verify(k2, decrypted_x, decrypted_signature_x)
    # print(f"Verify: {"VALID" if success else "NOT AUTHENTIC"}")
    # print()

    # success = signature_system.verify(k2, decrypted_x, signature_x)
    # print(f"Verify: {"VALID" if success else "NOT AUTHENTIC"}")
    # print()

    # success = signature_system.verify(k2, x, decrypted_signature_x)
    # print(f"Verify: {"VALID" if success else "NOT AUTHENTIC"}")
    # print()

    # success = signature_system.verify(k2, x, signature_x)
    # print(f"Verify: {"VALID" if success else "NOT AUTHENTIC"}")
    # print()

    # assert x_text == decrypted_x_text
    # assert decrypted_signature_x == signature_x, f"decrypted_signature_x = {decrypted_signature_x}, numbers {decrypted_signature_x.numbers}, signature_x = {signature_x}, numbers {signature_x.numbers}"
