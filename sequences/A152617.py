import cProfile
import copy
import itertools
import logging
import math
import sys
import heapq
import gmpy2
import primesieve

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A152617(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[2, 6, 60, 1140, 22230, 778050, 28787850, 1237877550, 82937795850, 6054459097050, 802693813972050, 126022928793611850], start_index=1)

    def calculate(self, n):
        n = gmpy2.mpz(n)
        counter = 0
        seen_sigma = set()
        for m, factors in self.numbers_with_n_distinct_factors_generator(n):
            counter += 1
            self.checkpoint(m, counter, 10000, n=n, total=True)
            sigma = factor.sigma(m, factors=factors)
            if sigma in seen_sigma:
                continue
            if len(factor.distinct_factors(sigma)) == n:
                self.delete_checkpoint(n=n)
                return m
            seen_sigma.add(sigma)

    def numbers_with_n_distinct_factors_generator(n):
        size_limit = gmpy2.mpz(gmpy2.floor(gmpy2.exp(4 * n - 6)))
        exponent_sum_size_limit = n + 3  # 2 * gmpy2.mpz(gmpy2.floor(gmpy2.log2(n))) + 4
        prime_it = primesieve.Iterator()
        prime_generator = prime.generator()
        primes = list(itertools.islice(prime_generator, n))
        factors = copy.copy(primes)
        factors = dict([(prime_factor, 1) for prime_factor in factors])
        value = gmpy2.mpz(factor.factor_dict_to_value(factors))
        heap = [(value, factors)]
        seen_set = set()
        # old_value = 0
        for _ in itertools.count(start=1):
            value, factors = heapq.heappop(heap)
            # logging.debug(f"heap size: {len(heap)}")
            # while value == old_value:
            #     value, factors = heapq.heappop(heap)
            for prime_factor, multiplicity in factors.items():
                if prime_factor == 2:
                    new_factors = copy.copy(factors)
                    new_factors[prime_factor] += 1
                    new_value = value * prime_factor
                    if new_value < size_limit and new_value not in seen_set:
                        heapq.heappush(heap, (new_value, new_factors))
                        seen_set.add(new_value)
                prime_it.skipto(prime_factor)
                next_prime = prime_it.next_prime()
                if next_prime not in factors and multiplicity == 1:
                    new_factors = copy.copy(factors)
                    del new_factors[prime_factor]
                    new_factors[next_prime] = 1
                    new_value = (value // prime_factor) * next_prime
                    if new_value < size_limit and new_value not in seen_set:
                        heapq.heappush(heap, (new_value, new_factors))
                        seen_set.add(new_value)
                elif next_prime in factors and multiplicity > 1:
                    new_factors = copy.copy(factors)
                    new_factors[prime_factor] -= 1
                    new_factors[next_prime] += 1
                    new_value = (value // prime_factor) * next_prime
                    if new_value < size_limit and new_value not in seen_set:
                        heapq.heappush(heap, (new_value, new_factors))
                        seen_set.add(new_value)
            yield value, factors





sys.modules[__name__] = A152617()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A152617()
    # seq.generate_b_file(term_cpu_time=30)
#     cProfile.run("""
# import A152617
# A152617(10)
#     """)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
