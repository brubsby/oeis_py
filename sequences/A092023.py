import itertools
import sys
import logging

from sequence import Sequence


class A092023(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 100000, n=n)
            if k == 0:
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A092023()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A092023().enumerate():
        print(f"{n} {val}")
