import itertools
import logging
import sys

import gmpy2
import primesieve

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A216666(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[1, 1, 1, 1, 6524, 809652228, 30717523794, 55779743835], start_index=1)
        self.divisors = primesieve.primes(2, 1000)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1) if n > 1 else 1, n=n)
        primes = [gmpy2.mpz(p) for p in primesieve.n_primes(n)]
        for k in itertools.count(start=k):
            k = gmpy2.mpz(k)
            self.checkpoint(k, k, 1000000, n=n)
            vals = []
            fail = False
            for p in primes:
                val = pow(k+1, p) - pow(k, p)
                if prime.trial_div_prime_test(val, divisors=self.divisors) == 0:
                    fail = True
                    break
                vals.append(val)
            if fail:
                continue
            if all(prime.is_prime(val) for val in vals):
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A216666()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A216666()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
