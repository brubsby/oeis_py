import itertools
import sys

import gmpy2

from sequence import Sequence


class A001003(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[1, 1], start_index=0, iterative_lookup=True)

    def calculate(self, n):
        m = gmpy2.mpz(n+1)
        return gmpy2.divexact(self(n-1) * (6 * m - 9) - (m - 3) * self(n-2), m)


sys.modules[__name__] = A001003()

if __name__ == "__main__":
    for n, val in A001003().enumerate():
        if n > 100:
            break
        print(f"{n} {val}")
