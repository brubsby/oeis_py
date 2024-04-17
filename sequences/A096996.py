import itertools
import logging
import sys

from sympy import divisor_sigma, totient

from modules import factor, base, prime, semiprime
from sequence import Sequence
from sequences import A062402


class A096996(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 1000, n)
            seen = []
            val = k
            while True:
                seen.append(val)
                val = A062402(val)
                if val in seen:
                    if n == len(seen) - seen.index(val):
                        self.delete_checkpoint(n)
                        return k
                    else:
                        break


sys.modules[__name__] = A096996()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A096996()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
