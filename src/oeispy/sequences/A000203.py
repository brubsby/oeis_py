import itertools
import sys
import logging

from oeispy.core import Sequence

from oeispy.utils import factor


class A000203(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        return factor.sigma(n)


sys.modules[__name__] = A000203()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A000203().enumerate():
        print(f"{n} {val}")
