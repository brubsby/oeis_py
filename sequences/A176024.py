import itertools
import sys
import logging

from modules import prime
from sequence import Sequence
import A000422


class A176024(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[82, 37765], start_index=1)

    # has been searched up to 46530
    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, n=n, cooldown=1)
            if prime.is_prime(A000422(k)):
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A176024()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A176024().enumerate(alert_time=10, quit_on_alert=True):
        print(f"{n} {val}")
