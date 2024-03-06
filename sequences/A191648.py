import itertools
import logging
import sys

from modules import factor, base, prime, semiprime
from sequence import Sequence

from sequences import A130846


class A191648(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def calculate(self, n):
        if n == 1 or n == 2:
            return 1
        k = n
        while True:
            antidivisors_concat = A130846(k)
            prime_status = prime.is_prime(antidivisors_concat, care_probable=True)
            if prime_status == 2:
                return antidivisors_concat
            elif prime_status == 1:
                exit("prp antidivisors_concat")
            else:
                k = antidivisors_concat





sys.modules[__name__] = A191648()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    seq = A191648()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True, start=8):
        print(f"{n} {val}")
