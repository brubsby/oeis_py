import itertools
import sys
import logging

import gmpy2

from oeispy.utils import prime, semiprime
from oeispy.core import Sequence


class A278637(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, n=n, cooldown=None)
            fib1 = gmpy2.fib(k)
            if prime.is_prime(fib1) in [1, 2] or semiprime.is_semi(fib1) in [1, 2]:
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A278637()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A278637()
    # seq.generate_b_file(term_cpu_time=60)
    for n, val in seq.enumerate():
        print(f"{n} {val}")
