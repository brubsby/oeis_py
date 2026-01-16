import primesieve
import math
import gmpy2


def nth_primorial(n):
    return math.prod(primesieve.n_primes(n), start=gmpy2.mpz(1))


def primorial(p):
    return math.prod(primesieve.primes(2, p) if p > 0 else [], start=gmpy2.mpz(1))