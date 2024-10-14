import itertools
import sys
import modules.prime as prime
import logging

import primesieve

from sequence import Sequence


class A359406(Sequence):

    def __init__(self, log_level=logging.INFO):
        super().__init__(start_index=1, lookup_list=[1, 2, 3, 23, 43, 141, 3472])

    def calculate(self, n):
        if n == 1:
            return 1
        it = primesieve.Iterator()
        lastk = self.load_checkpoint(default=self(n-1), n=n)
        it.skipto(30)
        concat_str = ""
        for k in itertools.count(start=1):
            p = it.next_prime()
            concat_str += str(p)
            if k <= lastk:
                continue
            if prime.is_prime(concat_str):
                return k
            self.checkpoint(k, k, n=n, total=False)


sys.modules[__name__] = A359406()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A359406().enumerate(alert_time=10, quit_on_alert=True):
        print(f"{n} {val}")


