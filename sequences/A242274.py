import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A242274(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, n=n)
            k = gmpy2.mpz(k)
            val = k*pow(3,k)-1
            is_semi = semiprime.is_semi(val)
            if is_semi in [1, 2]:
                self.delete_checkpoint(n=n)
                return k
            if is_semi in [-1]:
                logging.info(f"yafu time, k={k}: http://factordb.com/index.php?query={val}")
                exit(1)


sys.modules[__name__] = A242274()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A242274()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
