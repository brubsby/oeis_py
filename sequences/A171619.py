import itertools
import sys
import logging

from modules import prime
from sequence import Sequence

import A033491


class A171619(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, n=n, cooldown=5)
            if prime.is_prime(k) and prime.is_prime(A033491(k)):
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A171619()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A171619().enumerate():
        print(f"{n} {val}")
