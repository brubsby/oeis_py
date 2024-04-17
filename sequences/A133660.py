import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A133660(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[1, 3, 5, 87, 113, 1151, 5371, 199276, 32281747, 16946784207], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        prevlist = self.list(n-1)
        allsums = set()
        for i in range(1, len(prevlist)+1):
            for c in itertools.combinations(prevlist, i):
                allsums.add(gmpy2.mpz(sum(c)))
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 1000000, n=n)
            fail = False
            for s in allsums:
                if prime.is_prime(s+k):
                    fail = True
                    break
            if not fail:
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A133660()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A133660()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
