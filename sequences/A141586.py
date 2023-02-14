import itertools
import sys
import logging

from sequence import Sequence


class A141586(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True)


sys.modules[__name__] = A141586()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A141586().enumerate():
        print(f"{n} {val}")
