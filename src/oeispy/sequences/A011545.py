import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence
import sympy
import gmpy2


class A011545(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0, iterative_lookup=True)

    def calculate(self, n):
        if n == 0:
            return gmpy2.mpz(3)
        return self(n-1) * 10 + gmpy2.mpz(str((sympy.N(sympy.pi, n+100).evalf(n+100)))[-100:-99])


sys.modules[__name__] = A011545()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A011545()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
        if n > 100:
            break
