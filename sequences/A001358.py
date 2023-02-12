import itertools
import sys
import logging

from modules import semiprime
from sequence import Sequence


class A001358(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, iterative_lookup=True)

    def calculate(self, n):
        k = self(n-1)+1 if n > 1 else 1
        for k in itertools.count(start=k):
            is_semi = semiprime.is_semi(k)
            if is_semi > 0:
                return k
            elif is_semi == -1:
                print(f"yafu time: {k}")
                exit(1)


sys.modules[__name__] = A001358()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A001358().enumerate():
        print(f"{n} {val}")
