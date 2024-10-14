import itertools
import sys
import logging
from modules import prime

from sequence import Sequence
import A112141


class A224082(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[1, 2, 6, 7, 11, 17, 20, 21, 36, 69, 84, 168, 207, 248, 401, 431, 435, 1468, 4421, 8949], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, n=n)
            val = A112141(k) - 1
            if prime.is_prime(val) in [1, 2]:
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A224082()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A224082().enumerate(alert_time=30, quit_on_alert=True):
        print(f"{n} {val}")
