import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence
from sequences import A001008


class A153357(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def generator(self, start):
        assert(start == 1)
        for k in itertools.count(start):
            semi_result = semiprime.is_semi(A001008(k))
            if semi_result in [1, 2]:
                yield k
            if semi_result == -1:
                break


sys.modules[__name__] = A153357()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A153357()
    print(seq.generate_data_section())
    seq.generate_b_file(term_cpu_time=30)
    # for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
    #     print(f"{n} {val}")
