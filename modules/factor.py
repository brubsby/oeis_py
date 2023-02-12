import logging
import math
import time

import gmpy2
import primesieve
from modules import primetest
from modules.factordb import FactorDB

__trialdivisors = primesieve.primes(2, int(1e6))


def number_of_divisors(n, divisors=__trialdivisors, check_factor_db=True, num_retries=10, sleep_time=2):
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    if n == 1:
        return 1
    signature = prime_signature(n, divisors=divisors, check_factor_db=check_factor_db, num_retries=num_retries, sleep_time=sleep_time)
    if signature == -1:
        return -1
    return math.prod([exponent + 1 for exponent in signature])


def prime_signature(n, divisors=__trialdivisors, check_factor_db=True, num_retries=10, sleep_time=2):
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    if n == 1:
        return 1
    factors = trial_div_until(n, None, divisors)
    fully_factored = primetest.is_prime(factors[-1])
    if fully_factored:
        multiplicity = {}
        for factor in factors:
            multiplicity[factor] = multiplicity.get(factor, 0) + 1
        # python keeps dicts in insertion order so this should be fine
        return list(multiplicity.values())
    if check_factor_db:
        return factordb_prime_signature(n, num_retries=num_retries, sleep_time=sleep_time)
    return -1


def smallest_prime_factor(n, divisors=__trialdivisors, check_factor_db=True, num_retries=10, sleep_time=2):
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    if n < 2:
        return n
    factors = trial_div_until(n, 2, divisors)
    if len(factors) > 1:
        return factors[0]
    if primetest.is_prime(factors[0], check_factor_db=check_factor_db):
        return factors[0]
    else:
        return factordb_get_smallest_factor(n, num_retries=num_retries, sleep_time=sleep_time)


def biggest_prime_factor(n, divisors=__trialdivisors, check_factor_db=True, num_retries=10, sleep_time=2):
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    if n < 2:
        return n
    factors = trial_div_until(n, until=None, divisors=divisors)
    if primetest.is_prime(factors[-1], check_factor_db=check_factor_db):
        return factors[-1]
    else:
        return factordb_get_biggest_factor(n, num_retries=num_retries, sleep_time=sleep_time)


def factordb_get_smallest_factor(n, num_retries=10, sleep_time=2):
    logging.debug(f"Checking factordb for smallest factor of: {n}")
    f = FactorDB(n)
    f.connect()
    status = f.get_status()
    if status in ["P", "PRP", "Prp"]:
        return n
    factors = f.get_factor_list()
    if len(factors) == 1:
        if num_retries > 0:
            logging.info(
                f"Sleeping for {sleep_time} seconds after inconclusive status ({status}) on FactorDB for value: {n}")
            time.sleep(sleep_time)
            recurse_val = factordb_get_smallest_factor(n, num_retries - 1, sleep_time=sleep_time * 2)
            if recurse_val != -1:
                return recurse_val
        logging.debug(f"Unable to find smallest factor for {n}")
        return -1
    else:
        return factors[0]


def factordb_get_biggest_factor(n, num_retries=10, sleep_time=2):
    logging.debug(f"Checking factordb for smallest factor of: {n}")
    f = FactorDB(n)
    f.connect()
    status = f.get_status()
    if status in ["P", "PRP", "Prp"]:
        return n
    if status in ["FF"]:
        return f.get_factor_list()[-1]
    if num_retries > 0:
        logging.info(
            f"Sleeping for {sleep_time} seconds after inconclusive status ({status}) on FactorDB for value: {n}")
        time.sleep(sleep_time)
        recurse_val = factordb_get_biggest_factor(n, num_retries - 1, sleep_time=sleep_time * 2)
        if recurse_val != -1:
            return recurse_val
    logging.debug(f"Unable to find smallest factor for {n}")
    return -1


def factordb_prime_signature(n, num_retries=10, sleep_time=2):
    logging.debug(f"Checking factordb for prime signature of: {n}")
    f = FactorDB(n)
    f.connect()
    status = f.get_status()
    if status in ["P", "PRP", "Prp"]:
        return [1]
    if status in ["FF"]:
        return [factor_tuple[1] for factor_tuple in f.get_factor_from_api()]
    if num_retries > 0:
        logging.info(
            f"Sleeping for {sleep_time} seconds after inconclusive status ({status}) on FactorDB for value: {n}")
        time.sleep(sleep_time)
        recurse_val = factordb_get_biggest_factor(n, num_retries - 1, sleep_time=sleep_time * 2)
        if recurse_val != -1:
            return recurse_val
    logging.debug(f"Unable to find prime signature for {n}")
    return -1


def trial_div_until(n, until=None, divisors=__trialdivisors):
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    factors = [n]
    if n == 1:
        return factors
    remainder = n
    for d in divisors:
        if until is not None and len(factors) >= until:
            return factors
        if d >= remainder:
            break
        while d < remainder and gmpy2.is_divisible(remainder, d):
            remainder = remainder//d
            factors = factors[:-1] + [d, remainder]
            if until is not None and len(factors) >= until:
                return factors
    return factors
