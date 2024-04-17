import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A137582(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 0, n=n)
        val = gmpy2.fac(k)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 1, n=n)
            chars = str(val).replace('0',' ')
            chars = chars.strip()
            if ' ' not in chars:
                self.delete_checkpoint(n=n)
                return k
            val *= k+1


sys.modules[__name__] = A137582()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A137582()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
