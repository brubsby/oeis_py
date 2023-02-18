import cProfile
import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence

import A109313

class A131284(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else gmpy2.mpz(1), n=n)
        semiprime.generator(k)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 10000, n=n)
            if A109313(k) == k:
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A131284()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A131284()
    cProfile.run("""
import A131284
# seq.generate_b_file(term_cpu_time=30)
for n, val in A131284.enumerate(alert_time=60, quit_on_alert=True):
    print(f"{n} {val}")
    """)

