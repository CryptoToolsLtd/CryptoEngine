from ..keyexchangeops import KeyExchangeDriver
from ..systems import KeyExchangeDHElGamal

def run_KeyExchangeDHElGamal():
    driver = KeyExchangeDriver(KeyExchangeDHElGamal())
    driver.run()
