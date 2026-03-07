import itertools
import sys

import gmpy2
import sympy

from oeispy.core import Sequence


class A000073(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[0, 0, 1], start_index=0)

    def calculate(self, n):
        if self.lookup(n-1) is None or self.lookup(n-2) is None or self.lookup(n-3) is None:
            return gmpy2.mpz(sympy.tribonacci(n-1))  # sympy trib index is not the same as oeis
        return self(n-1) + self(n-2) + self(n-3)


sys.modules[__name__] = A000073()

if __name__ == "__main__":
    seq = A000073()
    for n, val in seq.enumerate():
        if n > 100:
            break
        print(f"{n} {val}")
