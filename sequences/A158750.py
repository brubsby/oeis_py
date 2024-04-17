import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence

from sequences import A078795


class A158750(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def generator(self, start):
        for k in itertools.count(start):
            logging.info(k)
            if prime.is_prime(gmpy2.mpz(A078795(k))):
                yield gmpy2.mpz(A078795(k))


sys.modules[__name__] = A158750()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A158750()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
