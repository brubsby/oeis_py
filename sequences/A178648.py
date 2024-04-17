import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence

from sequences import A096177, A096547


class A178648(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def generator(self, n):
        index1 = index2 = 1
        while True:
            val1 = A096177(index1)
            val2 = A096547(index2)
            if val1 == val2:
                yield A096177(index1)
                index1 += 1
                index2 += 1
            elif val1 > val2:
                index2 += 1
            else:
                index1 += 1



sys.modules[__name__] = A178648()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A178648()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
