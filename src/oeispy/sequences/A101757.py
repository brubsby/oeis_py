import itertools
import logging
import sys

from oeispy.utils import semiprime
from oeispy.core import Sequence
import A000073


class A101757(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 0, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, n=n)
            is_semi = semiprime.is_semi(A000073(k), num_retries=1, sleep_time=2)
            if is_semi in [1, 2]:
                self.delete_checkpoint(n=n)
                return k
            elif is_semi in [-1]:
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A101757()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A101757().enumerate():
        print(f"{n} {val} # http://factordb.com/index.php?query={A000073(val)}")
