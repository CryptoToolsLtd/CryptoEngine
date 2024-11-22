from .CHECK_TESTING import CHECK_TESTING
from typing import Callable
import unittest

class BitPaddingConfig:
    def __init__(self, LEFT_PADDING_SIZE: int, RIGHT_PADDING_SIZE: int):
        self.LEFT_PADDING_SIZE = LEFT_PADDING_SIZE
        self.RIGHT_PADDING_SIZE = RIGHT_PADDING_SIZE
    
    def __repr__(self) -> str:
        return f"BitPaddingConfig(LEFT_PADDING_SIZE={self.LEFT_PADDING_SIZE}, RIGHT_PADDING_SIZE={self.RIGHT_PADDING_SIZE})"

def pad(config: BitPaddingConfig, original_number: int, check_func: Callable[[int], bool]) -> int|None:
    LEFT_PADDING_SIZE = config.LEFT_PADDING_SIZE
    RIGHT_PADDING_SIZE = config.RIGHT_PADDING_SIZE

    if LEFT_PADDING_SIZE < 0 or RIGHT_PADDING_SIZE < 0:
        raise ValueError("LEFT_PADDING_SIZE and RIGHT_PADDING_SIZE must be at least 0")

    if RIGHT_PADDING_SIZE == 0:
        if LEFT_PADDING_SIZE == 0:
            return original_number if check_func(original_number) else None

    K = original_number.bit_length() + (LEFT_PADDING_SIZE - 1) + RIGHT_PADDING_SIZE
    left_pad_base = (1 << (K + 1))
    x = left_pad_base + original_number << RIGHT_PADDING_SIZE
    for left_pad_additional in range(0, max(0, int(2 ** (LEFT_PADDING_SIZE - 1)))):
        for right_pad in range(0, max(0, 2 ** RIGHT_PADDING_SIZE)):
                candidate = (left_pad_additional << K) + x + right_pad
                if check_func(candidate):
                    return candidate
    return None

def unpad(config: BitPaddingConfig, padded_number: int) -> int:
    LEFT_PADDING_SIZE = config.LEFT_PADDING_SIZE
    RIGHT_PADDING_SIZE = config.RIGHT_PADDING_SIZE

    if LEFT_PADDING_SIZE < 0 or RIGHT_PADDING_SIZE < 0:
        raise ValueError("LEFT_PADDING_SIZE and RIGHT_PADDING_SIZE must be at least 0")

    if RIGHT_PADDING_SIZE == 0:
        if LEFT_PADDING_SIZE == 0:
            return padded_number

    x = padded_number >> RIGHT_PADDING_SIZE
    x = x & ((1 << (x.bit_length() - LEFT_PADDING_SIZE - 1)) - 1)
    return x

class TestBitPadding(unittest.TestCase):
    def test_validity(self):
        for left in range(0, 10):
            for right in range(0, 10):
                config = BitPaddingConfig(LEFT_PADDING_SIZE=left, RIGHT_PADDING_SIZE=right)

                for original_number in range(0, 27000, 1):
                    padded_number = pad(config, original_number, lambda x: x % 3 == 0)
                    if padded_number is None:
                        # print(f"Failed for {config} and {original_number}")
                        pass
                    else:
                        self.assertEqual(unpad(config, padded_number), original_number)

if __name__ == '__main__':
    CHECK_TESTING()
