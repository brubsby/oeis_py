from modules import factor
import math
import itertools
import logging
import primesieve

logging.basicConfig(level=logging.DEBUG)

# for k in itertools.count(1):
if True:
    k = 7
    seq = list(primesieve.n_primes(k))
    prevsets = set()
    for n in itertools.count(0):
        prevlist = tuple(seq[-k:])
        logging.info(n)
        if prevlist in prevsets:
            print(f"{k}-truncated Euclid Mullin loops after {n} steps, {seq}")
            break
        prevsets.add(prevlist)
        val = math.prod(prevlist) + 1
        smallest_factor = factor.smallest_prime_factor(val, check_factor_db=True, threads=16)
        seq.append(int(smallest_factor))

