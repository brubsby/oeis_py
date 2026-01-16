import itertools
import logging
import sys

import primesieve

from oeispy.utils import factor, base, prime, semiprime, primorial
from oeispy.core import Sequence


class A096547(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[5, 7, 11, 13, 17, 19, 23, 31, 41, 53, 71, 103, 167, 431, 563, 673, 727, 829, 1801, 2699, 4481, 6121, 7283, 9413, 10321, 12491, 17807, 30307, 31891, 71917, 172517], start_index=1)

    def calculate(self, n):
        p = self.load_checkpoint(default=self(n-1) if n > 1 else 2, n=n)
        prime_it = primesieve.Iterator()
        prime_it.skipto(p)
        val = primorial.primorial(p)//2
        while True:
            self.checkpoint(p, p, 1, n=n)
            p = prime_it.next_prime()
            val *= p
            if prime.is_prime(val-2):
                self.delete_checkpoint(n=n)
                return p


sys.modules[__name__] = A096547()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A096547()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
