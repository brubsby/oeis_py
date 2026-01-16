import itertools
import sys
import logging

import primesieve

from oeispy.core import Sequence


class A000040(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, caching=False)

    def calculate(self, n):
        return primesieve.nth_prime(n)



sys.modules[__name__] = A000040()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A000040().enumerate():
        if n > 100:
            break
        print(f"{n} {val}")
