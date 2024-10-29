from ..pubkeyops import CryptoSystemAndSignatureSystemTest, PubkeyCommunicationDriver
from ..systems import (
    RSACryptoSystem, RSASignatureSystem,
    RSACryptoPublicKey, RSACryptoPrivateKey, RSACryptoCiphertext, RSASignatureSignerKey, RSASignatureVerifierKey,
)

from typing import override

class RSACryptoSystemAndSignatureSystemTest(CryptoSystemAndSignatureSystemTest[RSACryptoPublicKey, RSACryptoPrivateKey, RSACryptoCiphertext, RSASignatureSignerKey, RSASignatureVerifierKey]):
    @override
    def create_crypto_system(self) -> RSACryptoSystem:
        return RSACryptoSystem()
    
    @override
    def create_signature_system(self) -> RSASignatureSystem:
        return RSASignatureSystem()

def run_CryptoRSA_SignatureRSA():
    driver = PubkeyCommunicationDriver(RSACryptoSystem(), RSASignatureSystem())
    driver.run()
