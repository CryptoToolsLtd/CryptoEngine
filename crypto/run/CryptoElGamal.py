from ..pubkeyops import PubkeyCryptoCommunicationDriver
from ..systems import ElGamalCryptoSystem

def run_CryptoElGamal():
    driver = PubkeyCryptoCommunicationDriver(ElGamalCryptoSystem())
    driver.run()
