import itertools
import sys
import logging

import gmpy2

from sequence import Sequence


class A100083(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[
            1, 2, 4, 8, 31, 62, 124, 248, 373, 746, 1492, 2984, 11563, 23126, 46252, 92504
        ], start_index=1, iterative_lookup=True)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        val = sum(gmpy2.fac(m + 1) for m in range(1, k + 1))
        for k in itertools.count(start=k):
            self.checkpoint(k, k, n=n)
            if val.is_divisible(k):
                self.delete_checkpoint(n=n)
                return k
            val += gmpy2.fac(k+2)


sys.modules[__name__] = A100083()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A100083().enumerate():
        print(f"{n} {val}")
