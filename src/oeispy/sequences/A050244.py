import itertools
import logging
import sys

import gmpy2
import primesieve

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A050244(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[3, 6, 7, 8, 10, 11, 12, 14, 16, 22, 32, 34, 38, 82, 83, 106, 128, 149, 218, 223, 334, 412, 436, 599, 647, 916, 1373, 4414, 7246, 8423, 10118, 10942, 15898, 42422, 65986], start_index=1)

    # searches all k
    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else gmpy2.mpz(1), n=n)
        pow2 = pow(gmpy2.mpz(2), k-1)
        pow3 = pow(gmpy2.mpz(3), k-1)
        for k in itertools.count(start=k):
            pow2 *= 2
            pow3 *= 3
            val = pow2 + pow3
            # yafu hangs on composites this big
            if semiprime.is_semi(val, run_yafu=False, check_factor_db_prime=False, threads=8) in [1, 2]:
                self.delete_checkpoint(n=n)
                return k
            self.checkpoint(k, k, n=n, cooldown=None)

    # searches k such that k is a product of a power of 2 and a prime in blocks
    def generator(self, start):
        block_size = 1000
        if self.lookup(start-1):
            lower = self(start-1)+1
        else:
            lower = gmpy2.mpz(1)
        it = primesieve.Iterator()
        while True:
            upper = gmpy2.mpz(gmpy2.ceil(lower/block_size)*block_size)  # gmpy2.mpz(pow(2, gmpy2.ceil(gmpy2.log2(lower))))
            logging.info(f"Starting {lower}-{upper} block... from numdigits: {gmpy2.num_digits(pow(2, lower) + pow(3, lower))}-{gmpy2.num_digits(pow(2, upper) + pow(3, upper))}")
            it.skipto(0)
            prime = 0
            evaluated = set()
            terms = set()
            while prime <= upper:
                prime = it.next_prime()
                term = prime
                while term < lower:
                    term *= 2
                while term <= upper:
                    if term not in evaluated:
                        val = pow(2, term) + pow(3, term)
                        if semiprime.is_semi(val, run_yafu=False, check_factor_db_prime=False) in [1, 2]:
                            terms.add(term)
                            logging.info(f"Found one! {term}, waiting to yield until block completed.")
                        evaluated.add(term)
                    term *= 2
            yield from sorted(terms)
            lower = upper + 1


sys.modules[__name__] = A050244()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A050244()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=10, quit_on_alert=True, start=seq.first_unknown()):
        print(f"{n} {val}")
