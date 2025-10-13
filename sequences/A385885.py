import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence

from sequences import A001414


class A385885(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[1, 4, 366, 1095, 51846, 258410, 982815, 10653351], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 100000, n=n)
            if not prime.is_prime(k) and gmpy2.is_square(pow(k, gmpy2.mpz(2)) - pow(A001414(k), 2)):
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A385885()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A385885()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
