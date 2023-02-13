import itertools
import sys
import logging

from sequence import Sequence
import A000005
import A000040
import A000010
from modules import factor


class A107656(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, caching=False)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 1000, n=n)
            if A000040(k) == A000005(k) * A000010(k) + 1:
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A107656()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A107656().enumerate():
        print(f"{n} {val}")
