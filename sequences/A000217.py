import logging
import sys

import gmpy2

from sequence import Sequence


class A000217(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        return n*(n+gmpy2.mpz(1))//2


sys.modules[__name__] = A000217()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A000217()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
