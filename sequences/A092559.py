import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A092559(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[3, 5, 6, 7, 11, 12, 13, 17, 19, 20, 23, 28, 31, 32, 40, 43, 61, 64, 79, 92, 101, 104, 127, 128, 148, 167, 191, 199, 256, 313, 347, 356, 596, 692, 701, 1004, 1228, 1268, 1709, 2617, 3539, 3824, 5807, 10501, 10691, 11279, 12391, 14479, 42737, 83339, 95369, 117239], start_index=1, iterative_lookup=True)

    def calculate(self, n):
        for k in itertools.count(self(n-1)+1 if n > 1 else 1):
            val = pow(2, k) + 1
            logging.info(f"k = {k}")
            semiprime_result = semiprime.is_semi(val, threads=2, check_factor_db_prime=True)
            if semiprime_result in [1, 2]:
                return k
            elif semiprime_result == -1:
                raise Exception(f"Unknown if 2^{k}+1 is semiprime")




sys.modules[__name__] = A092559()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A092559()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
