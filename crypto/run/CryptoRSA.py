from ..pubkeyops import PubkeyCryptoCommunicationDriver
from ..systems import RSACryptoSystem

def run_CryptoRSA():
    driver = PubkeyCryptoCommunicationDriver(RSACryptoSystem())
    driver.run()
