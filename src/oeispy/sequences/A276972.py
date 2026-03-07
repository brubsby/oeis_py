import sys

import gmpy2

from oeispy.core import Sequence


class A276972(Sequence):

    def __init__(self):
        super().__init__(start_index=0, lookup_list=[])

    def calculate(self, n):
        n = gmpy2.mpz(n)
        return pow(n, 2 * (2 * pow(n, 4) + 1))


sys.modules[__name__] = A276972()

if __name__ == "__main__":
    A276972().generate_b_file()


