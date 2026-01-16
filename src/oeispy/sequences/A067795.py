import itertools
import logging
import sys

import primesieve

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A067795(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        prime_it = primesieve.Iterator()
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 1, n=n)
            prime_it.skipto(factor.sigma(k))
            p = prime_it.next_prime()
            if p == 2 * k + 1:
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A067795()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A067795()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
