import itertools
import logging
import sys

import gmpy2

from modules import factor, base, prime, semiprime
from sequence import Sequence


#Let f denote the map that replaces k with the concatenation of its proper divisors, written in decreasing order,
# each divisor being written in base 10 in the normal way.
class T000002(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        if n == 1 or prime.is_prime(n):
            return gmpy2.mpz(n)
        return gmpy2.mpz("".join([gmpy2.digits(divisor) for divisor in reversed(sorted(factor.get_all_proper_divisors(n)))]))


sys.modules[__name__] = T000002()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = T000002()
    [print(val, end=", ") for val in itertools.islice(T000002().generator(start=1), 20)]
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
