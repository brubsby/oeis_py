import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime, expression
from oeispy.core import Sequence


class A258357(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[0, 1, 2, 3, 13, 470, 2957], start_index=0)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 0 else 0, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 1, n=n)
            if prime.is_prime(expression.evaluate(f"Phi(7,{k}!)"), check_factor_db=False):
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A258357()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A258357()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
