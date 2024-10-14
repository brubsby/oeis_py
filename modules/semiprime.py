import itertools
import logging
import time

import gmpy2
import primesieve
from modules import prime
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


def is_semi(n, divisors=__trialdivisors, run_yafu=True, check_factor_db=True, check_factor_db_prime=False, threads=1, work=None):
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    if n < 2:
        return DEFINITE_NOT_SEMIPRIME
    factors = trial_div_until(n, 3, divisors)
    if len(factors) > 2:
        return DEFINITE_NOT_SEMIPRIME
    if len(factors) == 2:
        # no trial div, we already did
        return prime.is_prime(factors[-1], check_factor_db=check_factor_db_prime, trial_div_limit=None)
    else:  # trial div revealed no factors
        # no trial div, we already did
        prime_result = prime.is_prime(factors[-1], check_factor_db=check_factor_db_prime, trial_div_limit=None)
        if prime_result == 0:  # candidate is a single composite number that trial div did not crack
            if check_factor_db:  # check factor db if caller allows it
                factordb_is_semi_result = factordb_is_semi(n, num_retries=0)  # call only once to see if info is cached
                if factordb_is_semi_result != UNKNOWN_IF_SEMIPRIME:
                    return factordb_is_semi_result  # return a definitive value if we get it
            if run_yafu:  # didn't get anything definitive from factordb, use yafu from here on out if caller allows it
                return yafu_is_semi(n, threads=threads, work=work, report_to_factordb=check_factor_db)
            if check_factor_db:  # otherwise wait forever for factordb to have an answer (again) if user allows it
                return factordb_is_semi(n, num_retries=999999999, sleep_time=2)
            return UNKNOWN_IF_SEMIPRIME  # otherwise we have no way of knowing
        if prime_result == 1:
            return PROBABLE_NOT_SEMIPRIME  # candidate is probable prime, therefore probable not semiprime
        elif prime_result == 2:
            return DEFINITE_NOT_SEMIPRIME  # candidate is prime, therefore not semiprime


def yafu_is_semi(n, threads=1, work=None, report_to_factordb=False):
    factors = yafu.factor(n, stop_after_one=True, threads=threads, work=work, report_to_factordb=report_to_factordb)
    assert len(factors) > 0, "yafu should give factors"
    if len(factors) == 1:
        # yafu did trial div
        prime_result = prime.is_prime(factors[0], check_factor_db=True, trial_div_limit=None)
        if prime_result == 0:
            raise Exception(f"yafu failed to factor {n}? shouldn't happen")
        if prime_result == 1:
            return PROBABLE_NOT_SEMIPRIME
        if prime_result == 2:
            return DEFINITE_NOT_SEMIPRIME
        raise Exception(f"Prime test gave weird value: {prime_result} for {factors[0]}")
    if len(factors) > 2:
        return DEFINITE_NOT_SEMIPRIME
    # yafu did trial div, test if second factor is prime
    prime_result = prime.is_prime(factors[-1], check_factor_db=True, trial_div_limit=None)
    if prime_result == 0:
        return DEFINITE_NOT_SEMIPRIME
    if prime_result == 1:
        return PROBABLE_SEMIPRIME
    if prime_result == 2:
        return DEFINITE_SEMIPRIME
    raise Exception(f"Prime test gave weird value: {prime_result} for {factors[0]}")


def factordb_is_semi(n, num_retries=10, sleep_time=5, trial_div_limit=None):
    f = FactorDB(n)
    f.connect()
    status = f.get_status()
    if status in ['Unit', 'Zero']:
        return DEFINITE_NOT_SEMIPRIME
    factors = f.get_factor_list()
    if factors is None:
        logging.info(
            f"Sleeping for {sleep_time} seconds after no factors were found for value: {n}")
        time.sleep(sleep_time)
        return factordb_is_semi(n, num_retries=num_retries-1, sleep_time=sleep_time*2)
    num_factors = len(factors)
    if status in ["FF"]:
        if num_factors == 2:
            # we know both factors are prime or prp at this point, but we want to be specific if possible
            # we'll use our prime checking rather than immediately querying factordb again
            # this only happens when we found one, not a huge deal
            one_prime_result = prime.is_prime(factors[0], check_factor_db=True, trial_div_limit=trial_div_limit)
            two_prime_result = prime.is_prime(factors[1], check_factor_db=True, trial_div_limit=trial_div_limit)
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
        # factordb doesn't yet know the full factorization, and it could still be semiprime, the first val is definitely
        # prime or prp though, so we check the second first
        two_prime_result = prime.is_prime(factors[1], check_factor_db=True, trial_div_limit=trial_div_limit)
        # not semiprime if one is composite
        if two_prime_result == 0:
            return DEFINITE_NOT_SEMIPRIME
        # more likely that second factor is composite, so we postpone prime checking one until after we ruled that out
        one_prime_result = prime.is_prime(factors[0], check_factor_db=True, trial_div_limit=trial_div_limit)
        if one_prime_result == 0:
            # less likely to happen, but can
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


