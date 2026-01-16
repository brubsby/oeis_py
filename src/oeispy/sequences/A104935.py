import itertools
import logging
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence
from sequences import A000040


class A104935(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def generator(self, start):
        for n, p in enumerate(prime.generator(start=start, start_nth=True), start=start):
            j = p + n
            root, perfect = gmpy2.iroot(j, 2)
            if perfect:
                if prime.is_prime(root):
                    yield j


sys.modules[__name__] = A104935()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A104935()
    seq.generate_b_file()
    # for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
    #     print(f"{n} {val}")
