import logging
import sys

from sequences import A000422
from sequences import A007908
from sequence import Sequence


class A173426(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, iterative_lookup=True)

    def calculate(self, n):
        if n == 1:
            return "1"
        return A007908(n) + A000422(n-1)


sys.modules[__name__] = A173426()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A173426().enumerate():
        if n > 100:
            break
        print(f"{n} {val}")
