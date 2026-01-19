import itertools
import logging
import sys

import primesieve

from oeispy.utils import factor, base, prime, semiprime, primorial
from oeispy.core import Sequence
from oeispy.sequences import A002110


class A096177(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[	2, 3, 5, 7, 13, 29, 31, 37, 47, 59, 109, 223, 307, 389, 457, 1117, 1151, 2273, 9137, 10753, 15727, 25219, 26459, 29251, 30259, 52901, 194471], start_index=1)

    def calculate(self, n):
        p = self.load_checkpoint(default=self(n-1) if n > 1 else 2, n=n)
        prime_it = primesieve.Iterator()
        prime_it.skipto(p)
        val = primorial.primorial(p)//2
        while True:
            self.checkpoint(p, p, 1, n=n)
            p = prime_it.next_prime()
            val *= p
            if prime.is_prime(val+2):
                self.delete_checkpoint(n=n)
                return p


sys.modules[__name__] = A096177()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A096177()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
