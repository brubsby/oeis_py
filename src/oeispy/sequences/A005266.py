import logging
import math
import sys

import gmpy2

from oeispy.utils import factor
from oeispy.core import Sequence


class A005266(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[3, 2, 5, 29, 79, 68729, 3739, 6221191, 157170297801581, 70724343608203457341903, 46316297682014731387158877659877, 78592684042614093322289223662773, 181891012640244955605725966274974474087, 547275580337664165337990140111772164867508038795347198579326533639132704344301831464707648235639448747816483406685904347568344407941], start_index=1, iterative_lookup=True)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(3)
        return factor.biggest_prime_factor(math.prod(self(k) for k in range(1, n)) - 1)


sys.modules[__name__] = A005266()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A005266()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
