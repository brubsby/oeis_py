import itertools
import logging
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A363572(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, iterative_lookup=True)

    def generator(self, start):
        if start == 1:
            yield gmpy2.mpz(1)
        prev = 1
        used = {1}
        for n in itertools.count(start=2):
            prev_r = str(prev)[-1]
            for i in itertools.count(start=1):
                if i % 10 == 0 or i in used:
                    continue
                first = str(i)[0]

                if prime.is_prime(int(prev_r + first)):
                    if n >= start:
                        yield i
                    used.add(i)
                    prev = i
                    break


sys.modules[__name__] = A363572()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A363572()
    print(seq.generate_data_section())
    seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
