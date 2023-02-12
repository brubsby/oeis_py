import logging
import sys

import A007942

from modules import factor
from sequence import Sequence


class A110760(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        return factor.number_of_divisors(A007942(n))


sys.modules[__name__] = A110760()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A110760().enumerate():
        print(f"{n} {val}")
