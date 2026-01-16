import itertools
import sys
import logging

import gmpy2

from oeispy.core import Sequence
from oeispy.utils import factor


class A110079(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[5, 38, 284, 1370, 2168, 26828, 133088, 1515608, 19414448, 23521328, 25812848, 49353008, 82988756, 103575728, 537394688, 558504608, 921747488, 2651596448, 17517611968, 18249863488, 77792665408, 556915822208], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1) + 1 if n > 1 else 1, n=n)
        for k in itertools.count(start=k):
            k = gmpy2.mpz(k)
            self.checkpoint(k, k, 10000, n=n)
            factors = factor.factorize(k)
            if factor.sigma(k, factors) == 2 * k - pow(gmpy2.mpz(2), factor.number_of_divisors(k, factors)):
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A110079()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A110079().enumerate(alert_time=10, quit_on_alert=True):
        print(f"{n} {val}")
