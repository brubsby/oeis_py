import itertools
import sys
import logging

from modules import semiprime
from sequence import Sequence
import A110396


class A109758(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = self(n-1)+1 if n > 1 else 1  # self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, n=n)
            val = A110396(k) - 1
            is_semi = semiprime.is_semi(val, sleep_time=2, num_retries=2)
            if is_semi in [1, 2]:
                self.delete_checkpoint(n=n)
                return k
            elif is_semi in [-1]:
                logging.info(f"yafu time, k={k}: http://factordb.com/index.php?query={val}")
                # self.delete_checkpoint(n=n)
                # return k



sys.modules[__name__] = A109758()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A109758().enumerate():
        print(f"{n} {val}")
