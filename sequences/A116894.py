import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A116894(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[1, 5427, 41255, 43755, 208161], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else gmpy2.mpz(1), n=n)
        fac = gmpy2.fac(k-1)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, n=n, total=False)
            fac *= k
            gcd = gmpy2.gcd(fac + 1, pow(k, k) + 1)
            if gcd != 1 and gcd != 2 * k + 1:
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A116894()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A116894()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
