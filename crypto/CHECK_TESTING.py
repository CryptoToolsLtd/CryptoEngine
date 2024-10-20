import sys
import unittest

def CHECK_TESTING():
    if len(sys.argv) == 2 and sys.argv[1] == 'test':
        unittest.main(argv=[sys.argv[0], *sys.argv[2:]], exit=True)
