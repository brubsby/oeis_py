import itertools
import logging
import sys

import gmpy2
import primesieve

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A160054(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[7, 11, 23, 109, 211, 307, 1021, 4583, 42967, 297779, 1022443, 1459811, 10781809, 125211211, 11673806759, 3019843939831, 40047392632801, 88212019638251209, 444190204424015227, 57852556614292865039, 9801250757169593701501, 64747502900142088755541, 619216322498658374863033], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1) if n > 1 else 1, n=n)
        prime_it = primesieve.Iterator()
        prime_it.skipto(k)
        two = gmpy2.mpz(2)
        lp = prime_it.next_prime()
        lp2 = pow(lp, two)
        while True:
            p = prime_it.next_prime()
            p2 = pow(p, two)
            val = p2 + lp2 - 1
            if gmpy2.is_square(val):
                self.delete_checkpoint(n=n)
                return lp
            lp = p
            lp2 = p2


sys.modules[__name__] = A160054()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A160054()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
