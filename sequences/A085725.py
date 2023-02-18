import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence
import A034386


class A085725(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else gmpy2.mpz(1), n=n)
        for k, primorial in enumerate(A034386.generator(start=k), start=k):
            self.checkpoint(k, k, n=n, cooldown=None)
            if semiprime.is_semi(primorial+1, threads=1) > 0:
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A085725()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A085725()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
