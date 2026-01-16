import itertools
import logging
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A284498(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[1, 16, 15, 17, 2178, 299, 129, 110959, 116509, 1001159], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 10000, n=n)
            digrev = base.digrev(k)
            sigma_digrev = factor.sigma(digrev)
            if gmpy2.is_divisible(sigma_digrev, n):
                sigma = factor.sigma(k)
                if (sigma_digrev // n) == sigma:
                    self.delete_checkpoint(n=n)
                    return k


sys.modules[__name__] = A284498()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A284498()
    # seq.generate_b_file(term_cpu_time=30)
    # for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
    #     print(f"{n} {val}")
    print(seq(12))