import itertools
import sys
import logging

from oeispy.core import Sequence


class A007942(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, iterative_lookup=True)

    def calculate(self, n):
        if n < 2:
            return "1"
        return str(n) + self(n-1) + str(n)


sys.modules[__name__] = A007942()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A007942().enumerate():
        if n > 100:
            break
        print(f"{n} {val}")
