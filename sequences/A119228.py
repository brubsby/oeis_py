import itertools
import logging
import sys

from modules import factor, base, prime, semiprime, tridigital
from sequence import Sequence


class A119228(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[55, 595, 5995, 555985, 85989999559555, 5558888585898885, 898989555999995895, 559585958899855598985, 988889885885555858595, 85889898559958558998859955, 5595888555988988898588558558585], start_index=1)

    def generator(self, start):
        yield from tridigital.triangular_tridigit_generator([5, 8, 9], start=start)


sys.modules[__name__] = A119228()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A119228()
    print(seq.generate_data_section())
    # seq.generate_b_file(term_cpu_time=30)
    # for n, val in seq.enumerate(alert_time=60, quit_on_alert=False):
    #     print(f"{n} {val}")
