import logging
import sys

import gmpy2

from modules import factor
from sequence import Sequence


class A037279(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(1)
        return gmpy2.mpz("".join([gmpy2.digits(divisor) for divisor in sorted(factor.proper_divisors(n))]))


sys.modules[__name__] = A037279()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A037279()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
