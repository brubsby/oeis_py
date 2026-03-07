import sys

import gmpy2
import primesieve

import A045918
from oeispy.core import Sequence


class A247148(Sequence):

    def calculate(self, n):
        p = self.load_checkpoint(default=self(n-1) if n > 1 else 1, n=n)
        prime_it = primesieve.Iterator()
        prime_it.skipto(p)
        p = prime_it.next_prime()
        counter = 0
        A045918.set_caching(False)
        while True:
            ls_val = A045918(p)
            if gmpy2.is_divisible(ls_val, p):
                self.delete_checkpoint(n)
                return p
            self.checkpoint(p, counter, 10000000, n=n)
            p = prime_it.next_prime()
            counter += 1


sys.modules[__name__] = A247148()


if __name__ == "__main__":
    seq = A247148()
    for i, val in enumerate(seq.generate()):
        print(f"{i} {val}")
