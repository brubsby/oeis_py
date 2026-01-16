import itertools
import sys
import logging

from oeispy.core import Sequence

from sequences import A080670


class A195265(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, iterative_lookup=True, b_file_lookup=True)

    def calculate(self, n):
        if n == 1:
            return 20
        return A080670(self(n-1))


sys.modules[__name__] = A195265()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A195265()
    seq.generate_b_file(term_cpu_time=10)

    for n, val in seq.enumerate():
        print(f"{n} {val}")
