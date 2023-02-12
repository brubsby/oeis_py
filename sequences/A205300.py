import itertools
import logging
import sys
import time

import gmpy2
import primesieve

import A045918
import modules.checkpoint as checkpoint
import modules.semiprime as semiprime
from modules.factordb import FactorDB
from sequence import Sequence


class A205300(Sequence):

    def __init__(self):
        super().__init__(start_index=1, lookup_list=[6, 14, 4, 119, 993, 21161, 588821])

    def calculate(self, n):
        divisor_sets = [primesieve.primes(2, m) for m in [10000000]]
        start_k = self.load_checkpoint(default=1, n=n)
        for k in itertools.count(start=start_k):
            self.checkpoint(k, k, 1000, n=n)
            k_semi = semiprime.is_semi(k)
            assert k_semi != 1
            if k_semi == 0:
                continue
            seq = []
            is_semis = []
            skip = False
            first_divisor_set = True
            val = k
            for divisor_set in divisor_sets:
                for i in range(1, n+1):
                    if first_divisor_set:
                        val = A045918.ls(val)
                        seq.append(val)
                    else:
                        val = seq[i-1]
                    is_semi = semiprime.is_semi(val, divisor_set)
                    is_semis.append(is_semi)
                    if i == n:
                        if is_semi == 2:
                            skip = True
                            break
                    else:
                        if is_semi == 0:
                            skip = True
                            break
                if skip:
                    break
                first_divisor_set = False
            if skip:
                continue
            for i, val in enumerate(seq):
                good_vals = [0, -2] if i == len(seq)-1 else [2, 1]  # last value needs to not be a semiprime
                bad_vals = [2, 1] if i == len(seq)-1 else [0, -2]
                val_semi = is_semis[i]
                if val_semi in good_vals:
                    continue
                elif val_semi in bad_vals:
                    skip = True
                    break
                result = semiprime.factordb_is_semi(val)
                if result in bad_vals:
                    logging.info(f"Factor db ruled out k={k}, val={val}")
                    logging.info(f"http://factordb.com/index.php?query={val}")
                    skip = True
                    break
                elif result in good_vals:
                    continue
                logging.error(
                    f"Factor db does not have complete factors for next candidate: C{gmpy2.num_digits(val)} k={k}, val={val}")
                logging.error(f"http://factordb.com/index.php?query={val}")
                input()
            if skip:
                continue
            logging.info(f"Found the next term! {k}")
            self.delete_checkpoint(n=n)
            return k


sys.modules[__name__] = A205300()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # find next term
    seq = A205300()
    for n, val in seq.enumerate(no_lookup=False, alert_time=10, quit_on_alert=True):
        print(f"{n+seq.start_index} {val}")

