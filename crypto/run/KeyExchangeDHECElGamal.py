from ..keyexchangeops import KeyExchangeDriver
from ..systems import KeyExchangeDHECElGamal

def run_KeyExchangeDHECElGamal():
    driver = KeyExchangeDriver(KeyExchangeDHECElGamal())
    driver.run()
