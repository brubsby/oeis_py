import itertools
import logging
import math
import sys

import gmpy2

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A124984(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[3, 11, 1091, 1296216011, 2177870960662059587828905091, 76870667, 19, 257680660619, 73677606898727076965233531, 23842300525435506904690028531941969449780447746432390747, 35164737203, 680236515395832721385207993551089268653587669049005603771158431322421439886788657692771702217312064676141442733002799920551333408363991227971028435973627828868442456287665035319981598483172695609287167647379336272618247325274559541163968869546790959684845355600979883789395127470721634720000867602979, 420731, 163, 427307], start_index=1)

    def calculate(self, n):
        if n == 1:
            return gmpy2.mpz(3)
        q = math.prod(self(k) for k in range(1, n))
        val = pow(q, 2) + 2
        for prime_factor in factor.generate_factors_by_size(val):
            if gmpy2.is_congruent(prime_factor, 3, 8):
                return prime_factor


sys.modules[__name__] = A124984()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A124984()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
