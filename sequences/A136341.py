import itertools
import sys
import logging

import gmpy2

from modules import prime, semiprime
from sequence import Sequence
import A278637


class A136341(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 100000, n=n)
            if A278637.is_in(k) and A278637.is_in(k+1):
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A136341()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A136341().enumerate():
        print(f"{n} {val} # {gmpy2.fib(val)}")
