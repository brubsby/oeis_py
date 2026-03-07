import sys
import logging
import sys

import gmpy2

from oeispy.utils import factor
from oeispy.core import Sequence


class A001578(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=False, iterative_lookup=True)
        self._seen_factors = {1}

    def calculate(self, n):
        factors = factor.factordb_factor(gmpy2.fib(n))
        to_return = 1
        for this_factor in factors:
            if this_factor not in self._seen_factors:
                to_return = this_factor
                break
        self._seen_factors.update(factors)
        return to_return


sys.modules[__name__] = A001578()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A001578()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate():
        print(f"{n} {val}")
