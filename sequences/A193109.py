import cProfile
import itertools
import logging
import sys

import primesieve
from gmpy2 import gmpy2

from modules import prime

from sequence import Sequence


class A193109(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[0, 1, 9, 3, 225, 15, 65835, 1605, 19425, 2397347205, 153535525935], start_index=1)
        self.__trial_divisors = primesieve.primes(2, 27)

    # only check 15 mod 30 k, do trial div rejection first,
    # then try to really prove all the numbers are prime if possible
    def calculate(self, n):
        two = gmpy2.mpz(2)
        pow2s = [pow(two, x) for x in range(n+2)]
        k = self.load_checkpoint(default=0 if n <= 4 else 15, n=n)
        if n > 4:
            assert gmpy2.is_congruent(k, 15, 30)
            counter = itertools.count(start=k, step=30)
        else:
            counter = itertools.count(start=k)
        for k in counter:
            self.checkpoint(k, k, 100000005, n=n)  # iterations must be congruent to 15 mod 30
            fail = False
            for x in range(1, n + 1):
                if prime.trial_div_prime_test(pow2s[x] + k, divisors=self.__trial_divisors) == 0:
                    fail = True
                    break
            if fail:
                continue
            if prime.trial_div_prime_test(pow2s[n + 1] + k, divisors=self.__trial_divisors) == 2:
                continue
            # logging.debug(f"{k} passed phase 1")
            # passed all the fast tests, continue to the more strenuous ones
            for x in range(1, n + 1):
                if not prime.is_prime(pow2s[x] + k):
                    fail = True
                    break
            if fail:
                continue
            if prime.is_prime(pow2s[n + 1] + k):
                continue
            self.delete_checkpoint(n=n)
            return k




sys.modules[__name__] = A193109()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    for n, val in A193109().enumerate(alert_time=10, quit_on_alert=True):
        print(f"{n} {val}")
