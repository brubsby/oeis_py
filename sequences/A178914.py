import sys
import logging
import gmpy2

from sequence import Sequence


class A178914(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0)

    @staticmethod
    def num_digits(n):
        if n == 0:
            return gmpy2.mpz(1)
        return gmpy2.floor(gmpy2.log10(n))+1

    def calculate(self, n):
        return gmpy2.mpz(pow(gmpy2.mpz(10), A178914.num_digits(n)) - n)


sys.modules[__name__] = A178914()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A178914().enumerate():
        if n > 100:
            break
        print(f"{n} {val}")
