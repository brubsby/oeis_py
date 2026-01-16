import itertools
import sys
import logging

from oeispy.core import Sequence


class A000461(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        return str(n) * n


sys.modules[__name__] = A000461()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A000461().enumerate():
        if n > 100:
            break
        print(f"{n} {val}")
