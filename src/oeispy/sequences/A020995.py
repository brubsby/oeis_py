import itertools
import sys
import logging

import gmpy2

from oeispy.utils import base
from oeispy.core import Sequence


class A020995(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 1000, n=n)
            if k == base.digsum(gmpy2.fib(k)):
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A020995()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A020995().enumerate():
        print(f"{n} {val}")
