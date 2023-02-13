import logging
import sys

import A000422
from modules import factor
from sequence import Sequence


class A110757(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True)

    def calculate(self, n):
        return factor.number_of_divisors(A000422(n))


sys.modules[__name__] = A110757()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A110757()
    seq.generate_b_file(term_cpu_time=10)
    for n, val in seq.enumerate():
        print(f"{n} {val}")
