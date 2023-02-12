import itertools
import sys
import logging

from sequence import Sequence


class A104350(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, b_file_lookup=True)


sys.modules[__name__] = A104350()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A104350().enumerate():
        print(f"{n} {val}")
