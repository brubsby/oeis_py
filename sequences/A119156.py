import cProfile
import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A119156(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[3, 28, 3828, 828828, 388333828828, 223832333328828, 332828222833288828828, 28388332838238232223328828], start_index=1)
        self.tridigital_lookup = []
        self.tridigital_lookup_len = 0
        self.__lookup_depth = 15

    def tridigital_generator(self, digits, lower_length=1, upper_length=None):
        assert lower_length > 0, "lower_length must be at least 1"
        digits = list(map(gmpy2.mpz, digits))
        digit_iterables = [digits]
        x10_lambda = lambda x: x * 10
        while len(digit_iterables) < lower_length:
            last_digits = digit_iterables[0]
            digit_iterables.insert(0, list(map(x10_lambda, last_digits)))
        for digit_length in range(lower_length, upper_length+1):
            yield from self.tridigital_generator_helper(*digit_iterables)
            last_digits = digit_iterables[0]
            digit_iterables.insert(0, list(map(x10_lambda, last_digits)))

    def tridigital_generator_helper(self, *args):
        # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
        # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
        pools = [tuple(pool) for pool in args]
        if len(pools) == self.tridigital_lookup_len:
            yield from iter(self.tridigital_lookup)
        elif len(pools) < self.__lookup_depth and self.tridigital_lookup_len < len(pools):
            self.tridigital_lookup = list(self.tridigital_generator_helper_2(0, *pools))
            self.tridigital_lookup_len = len(pools)
            yield from iter(self.tridigital_lookup)
        else:
            yield from self.tridigital_generator_helper_2(0, *pools)

    def tridigital_generator_helper_2(self, number, *args):
        pools = [tuple(pool) for pool in args]
        if len(pools) == self.tridigital_lookup_len:
            for value in self.tridigital_lookup:
                yield number + value
            return
        if len(pools) == 0:
            yield number
            return
        if len(pools) == 1:
            for value in pools[0]:
                yield number + value
            return
        for value in pools[0]:
            yield from self.tridigital_generator_helper_2(number + value, *pools[1:])



    def generator(self, start):
        start_digits = len(str(start))
        digits = [2, 3, 8]
        digit_set = set(map(str, digits))
        digits = list(map(gmpy2.mpz, digits))
        digit_iterables = [digits]
        x10_lambda = lambda x: x * 10
        l = start_digits
        n = gmpy2.mpz(gmpy2.ceil((l+1)/2))
        while len(digit_iterables) < n:
            last_digits = digit_iterables[0]
            digit_iterables.insert(0, list(map(x10_lambda, last_digits)))
        for l in itertools.count(start=l):
            if gmpy2.mpz(gmpy2.ceil((l+1)/2)) > n:
                n = gmpy2.mpz(gmpy2.ceil((l+1)/2))
                last_digits = digit_iterables[0]
                digit_iterables.insert(0, list(map(x10_lambda, last_digits)))
            ln = l-n
            tentoln = pow(10, ln)
            for m in self.tridigital_generator_helper(*digit_iterables):
                t = gmpy2.isqrt(8 * m * tentoln) + 1
                if gmpy2.is_even(t):
                    t += 1
                q = (pow(t, 2) - 1) // 8
                if q//tentoln != m:
                    continue
                if set(gmpy2.digits(q)) <= digit_set and start <= q:
                    yield q
            self.checkpoint(l, l, cooldown=None, total=None)

sys.modules[__name__] = A119156()

def main():
    seq = A119156()
    for val in seq.generator(gmpy2.mpz("2" * 43)):
        print(f"{val}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A119156()
    # seq.generate_b_file(term_cpu_time=30)
    profile = False
    if profile:
        cProfile.run("""
import A119156
for val in A119156.generator(1):
    print(f"{val}")
        """)
    else:
        main()

