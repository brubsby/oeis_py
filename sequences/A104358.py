import itertools
import sys
import logging

from sequence import Sequence
from modules import factor
import A104350


class A104358(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=2, b_file_lookup=True)

    def calculate(self, n):
        return factor.smallest_prime_factor(A104350(n) - 1)

sys.modules[__name__] = A104358()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A104358()
    seq.generate_b_file(term_cpu_time=10)
    for n, val in seq.enumerate():
        print(f"{n} {val}")
