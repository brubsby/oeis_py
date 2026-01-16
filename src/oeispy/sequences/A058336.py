import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence
from sequences import A005282


class A058336(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def generator(self, start):
        yield from A005282.mian_chowla_generator(1, 5)


sys.modules[__name__] = A058336()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A058336()
    print(seq.generate_data_section())
    seq.generate_b_file()
    # for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
    #     print(f"{n} {val}")
