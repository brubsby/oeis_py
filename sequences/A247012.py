import itertools
import logging
import sys

from modules import factor, base
from sequence import Sequence


class A247012(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[6, 133, 172, 841, 1005, 1603, 4258, 5299, 192901, 498906, 1633303, 5307589, 16333303, 20671542, 41673714, 42999958, 73687923], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 10000, n=n)
            revk = base.digrev(k)
            divisors = factor.proper_divisors(k)
            value = 0
            old_value = None
            while value < revk:
                value = sum(divisors)
                if revk == value:
                    self.delete_checkpoint(n=n)
                    return k
                if value == old_value:
                    break
                divisors = divisors[1:] + [value]
                old_value = value


sys.modules[__name__] = A247012()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A247012().enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
