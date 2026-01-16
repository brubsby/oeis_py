import itertools
import logging
import sys

from oeispy.utils import semiprime
from oeispy.core import Sequence


class A215231(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[2, 3, 4, 6, 7, 11, 14, 19, 20, 24, 25, 28, 30, 32, 38, 47, 54, 55, 70, 74, 76, 82, 85, 87, 88, 95, 98, 107, 110, 112, 120, 123, 126, 146, 163, 166, 171], start_index=1)

    def calculate(self, n):
        if n == 1:
            return 2
        k = self.load_checkpoint(default=1, n=n)
        last_max_gap = self(n-1) if n > 1 else 2
        last = k
        for k in semiprime.generator(start=k):
            gap = k - last
            if gap > last_max_gap:
                self.delete_checkpoint(n=n)
                return gap
            last = k
            self.checkpoint(k-1, k-1, 1000, n=n)


sys.modules[__name__] = A215231()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A215231().enumerate():
        print(f"{n} {val}")
