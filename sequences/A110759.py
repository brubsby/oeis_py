import logging
import sys

import A173426
from modules import factor
from sequence import Sequence


class A110759(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True)

    def calculate(self, n):
        return factor.number_of_divisors(A173426(n))


sys.modules[__name__] = A110759()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A110759()
    seq.generate_b_file(term_cpu_time=10)
    for n, val in seq.enumerate():
        print(f"{n} {val}")
