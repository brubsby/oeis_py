import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence
from sequences import A007662


class A291351(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[9, 13, 23, 27, 33, 47, 61, 113, 145, 161, 191, 281, 291, 417, 869, 919, 1213, 1297, 1663, 2103, 2297, 2325, 3241, 3895, 4337, 6645, 7911, 8737, 13369, 13555, 19245, 34025, 47779, 48589, 54521, 91355], start_index=1)

    def calculate(self, n):
        addend = pow(2, 10)
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 1, n=n)
            if prime.is_prime(A007662(k) + addend):
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A291351()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A291351()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
