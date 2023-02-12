
import sys
import logging

import gmpy2

from sequence import Sequence
import A001358


class A112141(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, iterative_lookup=True)

    def calculate(self, n):
        return self(n-1) * A001358(n) if n > 1 else A001358(1)


sys.modules[__name__] = A112141()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(gmpy2.mpz(A112141()(8949)))
    # for n, val in A112141().enumerate():
    #     print(f"{n} {val}")
