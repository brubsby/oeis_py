import logging
import sys

from oeispy.utils import factor

from oeispy.core import Sequence


class A000010(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, caching=False)

    def calculate(self, n):
        return factor.phi(n)


sys.modules[__name__] = A000010()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A000010().enumerate():
        if n > 100:
            break
        print(f"{n} {val}")
