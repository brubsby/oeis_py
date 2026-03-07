import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A252790(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, n=n)
            if semiprime.is_semi(k * pow(gmpy2.mpz(5), k)):
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A252790()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A252790()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
