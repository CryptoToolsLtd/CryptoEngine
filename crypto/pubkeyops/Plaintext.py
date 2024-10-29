GRANULARITY = 15

from ..strint import str2int, int2str
import unittest

class Plaintext:
    def __init__(self, numbers: list[int]):
        self.numbers = list(numbers)
    
    def to_string(self) -> str:
        result = ""
        for number in self.numbers:
            result += int2str(number)
        return result
    
    def __repr__(self) -> str:
        return f"Plaintext({self.numbers})"
    
    def __str__(self) -> str:
        raise NotImplementedError("This method must never be invoked ; use to_string() instead")
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Plaintext):
            return False
        N = len(self.numbers)
        if N != len(other.numbers):
            return False
        for i in range(0, N):
            if self.numbers[i] != other.numbers[i]:
                return False
        return True
    
    @staticmethod
    def from_string(s: str) -> "Plaintext":
        numbers: list[int] = []        

        accumulation = ""
        for char in s:
            if not char.isalpha():
                raise ValueError("Plaintext can only contain alphabetic characters")
            char = char.upper()
            accumulation += char
            if len(accumulation) == GRANULARITY:
                numbers.append(str2int(accumulation))
                accumulation = ""
        
        if len(accumulation) > 0:
            numbers.append(str2int(accumulation))

        return Plaintext(numbers)

class TestPlaintext(unittest.TestCase):
    def test_validity(self):
        def i(s: str):
            expected = s
            actual = Plaintext.from_string(s).to_string()
            self.assertEqual(actual, expected, f'expected = {expected}, actual = {actual}')
        i("HELLOWORLD")
        i("HELLO")
        i("WORLD")
        i("INSANELYLONGMESSAGE")
