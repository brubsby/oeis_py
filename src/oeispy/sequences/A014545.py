import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence
from oeispy.sequences import A006862


class A014545(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[0, 1, 2, 3, 4, 5, 11, 75, 171, 172, 384, 457, 616, 643, 1391, 1613, 2122, 2647, 2673, 4413, 13494, 31260, 33237], start_index=1)

    # probably should sieve this before trying seriously
    def calculate(self, n):
        start = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 0, n=n)
        for k, euclid_number in A006862.enumerate(start=start):
            self.checkpoint(k, k, n=n)
            if prime.is_prime(euclid_number):
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A014545()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A014545()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
