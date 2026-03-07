import itertools
import logging
import sys
from sympy import factorial

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A181185(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[1, 2, 3, 6, 17, 25, 40, 45, 143, 289, 510, 524, 526, 716, 756, 1008, 1271, 1370, 3677, 7963, 9053], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        term1 = pow(2,k)
        term2 = factorial(k)
        for k in itertools.count(start=k):
            val = (term1 - 1) * term2 + 1
            if prime.is_prime(val):
                self.delete_checkpoint(n=n)
                return k
            self.checkpoint(k, k, 1, n=n)
            term1 *= 2
            term2 *= k+1


sys.modules[__name__] = A181185()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A181185()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
