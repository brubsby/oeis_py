import itertools
import sys
import logging

from oeispy.core import Sequence
import A060383


class A139044(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True)

    def calculate(self, n):
        return A060383(n+2)


sys.modules[__name__] = A139044()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A139044()
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate():
        print(f"{n} {val}")
