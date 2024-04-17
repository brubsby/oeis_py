import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A087714(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        p = self.load_checkpoint(default=1 if n == 1 else self(n-1), n=n)
        prime_gen = prime.generator(p + 1)
        p = next(prime_gen)
        primorial = prime.primorial(p) if p > 1 else 1
        for p in prime_gen:
            if prime.is_prime(primorial + p) and prime.is_prime(primorial - p):
                self.delete_checkpoint(n=n)
                return prime.previous_prime(p)
            primorial = primorial * p
            self.checkpoint(p, p, 10000, n=n)


sys.modules[__name__] = A087714()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A087714()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
