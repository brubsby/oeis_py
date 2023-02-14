import itertools
import logging
import time

import gmpy2
import primesieve
import modules.primetest as primetest
from modules import yafu
from modules.factor import trial_div_until
from modules.factordb import FactorDB


__trialdivisors = primesieve.primes(2, int(1e6))
__primes_set = frozenset(primesieve.primes(2, int(1e7)))

DEFINITE_SEMIPRIME = 2
PROBABLE_SEMIPRIME = 1
DEFINITE_NOT_SEMIPRIME = 0
UNKNOWN_IF_SEMIPRIME = -1
PROBABLE_NOT_SEMIPRIME = -2


def is_trial_div_semi(n, divisors=__trialdivisors):
    if n < 2:
        return DEFINITE_NOT_SEMIPRIME
    factors = trial_div_until(n, 3, divisors)
    if len(factors) > 2:
        return DEFINITE_NOT_SEMIPRIME
    return UNKNOWN_IF_SEMIPRIME


# trial div, prime test, and primesieve test
def is_semi(n, divisors=__trialdivisors, check_factor_db=True, threads=1, work=None):
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    if n < 2:
        return DEFINITE_NOT_SEMIPRIME
    factors = trial_div_until(n, 3, divisors)
    if len(factors) > 2:
        return DEFINITE_NOT_SEMIPRIME
    if len(factors) == 2:
        return primetest.is_prime(factors[-1], check_factor_db=check_factor_db)
    else:
        prime_result = primetest.is_prime(factors[-1], check_factor_db=check_factor_db)
        if prime_result == 0:
            if check_factor_db:
                factordb_is_semi_result = factordb_is_semi(n, num_retries=0)
                if factordb_is_semi_result != UNKNOWN_IF_SEMIPRIME:
                    return factordb_is_semi_result
            return yafu_is_semi(n, threads=threads, work=work)
            # todo add yafu (and report to factordb) when this result inconclusive
        if prime_result == 1:
            return PROBABLE_NOT_SEMIPRIME  # probable prime, therefore probable not semiprime
        elif prime_result == 2:
            return DEFINITE_NOT_SEMIPRIME  # certain prime, therefore certain not semiprime


def yafu_is_semi(n, threads=1, work=None):
    factors = yafu.factor(n, stop_after_one=True, threads=threads, work=work)
    assert len(factors) > 0, "yafu should give factors"
    if len(factors) == 1:
        primetest_result = primetest.is_prime(factors[0], check_factor_db=True)
        if primetest_result == 0:
            raise Exception(f"yafu failed to factor {n}? shouldn't happen")
        if primetest_result == 1:
            return PROBABLE_NOT_SEMIPRIME
        if primetest_result == 2:
            return DEFINITE_NOT_SEMIPRIME
        raise Exception(f"Prime test gave weird value: {primetest_result} for {factors[0]}")
    if len(factors) > 2:
        return DEFINITE_NOT_SEMIPRIME
    primetest_result = primetest.is_prime(factors[-1], check_factor_db=True)
    if primetest_result == 0:
        return DEFINITE_NOT_SEMIPRIME
    if primetest_result == 1:
        return PROBABLE_SEMIPRIME
    if primetest_result == 2:
        return DEFINITE_SEMIPRIME
    raise Exception(f"Prime test gave weird value: {primetest_result} for {factors[0]}")


def factordb_is_semi(n, num_retries=10, sleep_time=5):
    f = FactorDB(n)
    f.connect()
    status = f.get_status()
    if status in ['Unit', 'Zero']:
        return DEFINITE_NOT_SEMIPRIME
    factors = f.get_factor_list()
    num_factors = len(factors)
    if status in ["FF"]:
        if num_factors == 2:
            # we know both factors are prime or prp at this point, but we want to be specific if possible
            # we'll use our very optimized prime checking rather than immediately querying factordb again
            one_prime_result = primetest.is_prime(factors[0], check_factor_db=True)
            two_prime_result = primetest.is_prime(factors[1], check_factor_db=True)
            assert one_prime_result != 0
            assert two_prime_result != 0
            if one_prime_result == 1 or two_prime_result == 1:
                return PROBABLE_SEMIPRIME
            return DEFINITE_SEMIPRIME
        return DEFINITE_NOT_SEMIPRIME
    elif status in ["C", "U"]:
        if num_retries <= 0:
            return UNKNOWN_IF_SEMIPRIME
        logging.info(
            f"Sleeping for {sleep_time} seconds after inconclusive status ({status}) on FactorDB for value: {n}")
        time.sleep(sleep_time)
        return factordb_is_semi(n, num_retries=num_retries-1, sleep_time=sleep_time*2)
    elif status in ["CF"]:
        if num_factors > 2:
            return DEFINITE_NOT_SEMIPRIME
        one_prime_result = primetest.is_prime(factors[0], check_factor_db=True)
        two_prime_result = primetest.is_prime(factors[1], check_factor_db=True)
        # not semiprime if one is composite
        if one_prime_result == 0 or two_prime_result == 0:
            return DEFINITE_NOT_SEMIPRIME
        if one_prime_result == 1 or two_prime_result == 1:
            return PROBABLE_SEMIPRIME
        return DEFINITE_SEMIPRIME
    elif status in ["P", "Unit"]:
        return DEFINITE_NOT_SEMIPRIME
    elif status in ["Prp", "PRP"]:
        return PROBABLE_NOT_SEMIPRIME
    else:
        raise Exception(f"Unknown status: {status} returned when querying FactorDB for value: {n}")


def generator(start=2):
    for k in itertools.count(start=start):
        if is_semi(k):
            yield k


