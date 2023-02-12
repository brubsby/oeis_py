import itertools
import logging
import sys
import time

import primesieve
import bitarray

import gmpy2

from sequence import Sequence


class A116622(Sequence):

    def __init__(self):
        super().__init__(start_index=1,
                         lookup_list=[1, 11, 140711, 863101, 1856455, 115602923, 566411084209, 706836043419179])

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n >= 2 else 1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 1000000, n=n, total=True)
            if gmpy2.powmod(13, k, k) == 2:
                self.delete_checkpoint(n=n)
                return k

    # 849733.07/s
    def calculate2(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n >= 2 else 1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 1000000, n=n, total=True)
            if gmpy2.powmod(13, k, k) == 2:
                self.delete_checkpoint(n=n)
                return k

    @staticmethod
    def calculate_pow_mod_values(b, p, c):
        congruence_classes_set = set()
        order = None
        ret_k = None
        for k in itertools.count(start=1):
            congruence_class = gmpy2.powmod(b, k, p)
            if not order and congruence_class == 1:
                order = k
            if not ret_k and congruence_class == c:
                ret_k = k
            if ret_k and order:
                return ret_k, order
            if congruence_class in congruence_classes_set:
                break
            congruence_classes_set.add(congruence_class)
        return ret_k, order

    # http://web.archive.org/web/20120104074313/http://www.immortaltheory.com/NumberTheory/2nmodn.htm
    # generate a list of primes that n is not allowed to be divisible by, given a base and c, to later rule out n with
    @staticmethod
    def get_incompatible_prime_factors(base, c, num_primes=1000):
        it = primesieve.Iterator()
        p = it.next_prime()
        incompatible_primes = []
        while len(incompatible_primes) < num_primes:
            ret_k, order = A116622.calculate_pow_mod_values(base, p, c)
            if not ret_k:
                yield p


sys.modules[__name__] = A116622()

# p1000, 0-10^7, 2813367 k/s
# p1000, 0-10^8, 2774790 k/s
# p1000, 0-10^9, 2883005 k/s
# 2168018


if __name__ == "__main__":
    # for n, val in A116622().enumerate(alert_time=10, quit_on_alert=True):
    #     print(f"{n} {val}")
    logging.basicConfig(level=logging.INFO)
    start_prime = 2
    sieve_limit = 5
    base = 13
    c = 2
    start_k = gmpy2.mpz(10000002640000000)  # int(pow(gmpy2.mpz(10), 16))
    limit_n = gmpy2.mpz(20000000000000000)
    prime_limit = limit_n / 2
    it = primesieve.Iterator()
    start_time = time.time() - 0.001
    p = 0
    counter = 0
    incompatible_primes = set()
    while p <= prime_limit:
        p = it.next_prime()
        k, h = A116622.calculate_pow_mod_values(base, p, c)
        # maybe gcd idk
        if not k or not h:
            incompatible_primes.add(p)
            continue
        if gmpy2.gcd(k, h) in incompatible_primes:
            continue
        counter += 1
        if counter % 100 == 0:
            print(f"{counter}, {int(counter // (time.time() - start_time))} lines/s")
        for x in itertools.count(start=max(1, (start_k//p - k)//h)):
            n = p * (h * x + k)
            if n > limit_n:
                break
            if gmpy2.powmod(base, n, n) == c:
                print(f"Found one!: {n}")







