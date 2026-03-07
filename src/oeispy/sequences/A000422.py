import itertools
import sys
import logging

from oeispy.core import Sequence


class A000422(Sequence):

    def __init__(self):
        super().__init__(lookup_list=["1"], start_index=1, iterative_lookup=True)

    def calculate(self, n):
        return str(n) + self(n-1)

sys.modules[__name__] = A000422()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A000422().enumerate():
        print(f"{n} {val}")
