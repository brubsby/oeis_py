import itertools
import sys
import logging

from oeispy.core import Sequence
from oeispy.utils import factor
import A104350


class A104367(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True)

    def calculate(self, n):

        work = 45 if n == 159 else None
        return factor.biggest_prime_factor(A104350(n) + 1, threads=12, work=work)


sys.modules[__name__] = A104367()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A104367()
    # seq.generate_b_file(term_cpu_time=10)
    for n, val in seq.enumerate():
        print(f"{n} {val}")
