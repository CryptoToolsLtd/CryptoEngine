from ..pubkeyops import PubkeyCryptoCommunicationDriver
from ..systems import ECElGamalCryptoSystem

def run_CryptoECElGamal():
    driver = PubkeyCryptoCommunicationDriver(ECElGamalCryptoSystem())
    driver.run()
