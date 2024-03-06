import logging
import sys

import gmpy2

from sequence import Sequence


class A003056(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0)

    def calculate(self, n):
        return (gmpy2.isqrt(gmpy2.mpz(8)*n + 1)-1)//2


sys.modules[__name__] = A003056()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A003056()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        if n > 100:
            break
        print(f"{n} {val}")
