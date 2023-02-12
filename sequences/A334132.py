import logging
import sys

import gmpy2
import primesieve

import modules.factor
import modules.semiprime as semiprime
from sequence import Sequence
import A005150


def prime_gen():
    it = primesieve.Iterator()
    while True:
        yield it.next_prime()


class A334132(Sequence):

    def __init__(self):
        super().__init__(start_index=1, lookup_list=[1])
        self._prime_list = primesieve.n_primes(int(1e6), 2)
        self._prime_set = set(self._prime_list)

    def calculate(self, n):
        batch_size = 100000
        prime = self.load_checkpoint(default=2, n=n)
        counter = 0
        to_div = gmpy2.mpz(A005150(n))
        logging.debug(f"A005150({n}) calculated")
        if to_div == 1 or (to_div < self._prime_list[-1] and to_div in self._prime_set):
            self.delete_checkpoint(n)
            return to_div
        logging.debug(f"{n} is not in the first 1e6 primes")
        self.checkpoint(prime, counter, n=n, total=True, log=False)
        while True:
            divisors = primesieve.n_primes(batch_size, prime)
            prime = divisors[-1]
            factors = modules.factor.trial_div_until(to_div, 2, divisors)
            if len(factors) > 1:
                self.delete_checkpoint(n)
                return factors[0]
            self.checkpoint(prime, counter, n=n, total=True)
            counter += batch_size



sys.modules[__name__] = A334132()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    A334132 = A334132()
    # for i, val in enumerate(A334132.generate_with_timeout(timeout=300)):
    #     print(f"{i+A334132.start_index} {val}")
    #     # print(f"{val}, ", end="")
    A334132.calculate(62)
