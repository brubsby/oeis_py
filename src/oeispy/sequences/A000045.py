import logging
import sys

import gmpy2

from oeispy.core import Sequence


class A000045(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0)

    def calculate(self, n):
        return gmpy2.fib(n)


sys.modules[__name__] = A000045()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A000045()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
