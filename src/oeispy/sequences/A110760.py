import logging
import sys

import A007942

from oeispy.utils import factor
from oeispy.core import Sequence


class A110760(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True)

    def calculate(self, n):
        return factor.number_of_divisors(A007942(n), threads=16)


sys.modules[__name__] = A110760()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A110760()
    # seq.generate_b_file(term_cpu_time=10)
    for n, val in seq.enumerate():
        print(f"{n} {val}")
