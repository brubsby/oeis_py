import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence
from sequences import A005282


class A051788(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def generator(self, start):
        yield from A005282.mian_chowla_generator(1, 3)


sys.modules[__name__] = A051788()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A051788()
    print(seq.generate_data_section())
    seq.generate_b_file()
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
