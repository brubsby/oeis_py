import itertools
import sys
import logging

from sequence import Sequence
from modules import factor
import A104350


class A104367(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=2, b_file_lookup=True)

    def calculate(self, n):
        return factor.biggest_prime_factor(A104350(n) + 1)


sys.modules[__name__] = A104367()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A104367()
    seq.generate_b_file(term_cpu_time=10)
    for n, val in seq.enumerate():
        print(f"{n} {val}")
