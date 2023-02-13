import itertools
import sys
import logging

from sequence import Sequence


class A007908(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, iterative_lookup=True)

    def calculate(self, n):
        if n < 2:
            return "1"
        return self(n-1) + str(n)


sys.modules[__name__] = A007908()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A007908().enumerate():
        print(f"{n} {val}")
