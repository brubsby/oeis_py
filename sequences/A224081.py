import itertools
import logging
import sys

import A112141
from modules import prime
from sequence import Sequence


class A224081(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[1, 4, 5, 6, 11, 12, 18, 39, 51, 98, 124, 170, 179, 208, 248, 838, 919, 939, 1233, 1352, 2177, 3070, 10714], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, n=n)
            val = A112141(k) + 1
            if prime.is_prime(val) in [1, 2]:
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A224081()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A224081().enumerate(alert_time=30, quit_on_alert=True):
        print(f"{n} {val}")
