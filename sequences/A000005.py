import itertools
import sys
import logging
from modules import factor

from sequence import Sequence


class A000005(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, caching=False)

    def calculate(self, n):
        return factor.number_of_divisors(n)


sys.modules[__name__] = A000005()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A000005().enumerate():
        print(f"{n} {val}")
