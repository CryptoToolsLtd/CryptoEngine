from ..pubkeyops import ThreepassCryptoCommunicationDriver
from ..systems import MasseyOmuraCryptoSystem

def run_CryptoMasseyOmura():
    driver = ThreepassCryptoCommunicationDriver(MasseyOmuraCryptoSystem())
    driver.run()
