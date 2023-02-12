import itertools
import sys
import logging

from sequence import Sequence
import A178914


class A110396(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, iterative_lookup=True)

    def calculate(self, n):
        if n == 0:
            return 1
        return A178914(n)*self(n-1)


sys.modules[__name__] = A110396()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A110396().enumerate():
        print(f"{n} {val}")
