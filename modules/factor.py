import copy
import functools
import logging
import math
import time

import gmpy2
import primesieve
from modules import prime
from modules.factordb import FactorDB
from modules import yafu

__trialdivisors = primesieve.primes(2, int(1e6))


# returns the proper divisors, but invokes yafu and may take unbounded time
def factorize(n, divisors=__trialdivisors, check_factor_db=True, threads=1, work=None):
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    if n < 2:
        return []
    if gmpy2.num_digits(n) < 20:
        factors = trial_div_until(n, until=None, divisors=divisors)
        fully_factored = prime.is_prime(factors[-1], trial_div_limit=None)
        if fully_factored:
            return factors
    if check_factor_db:
        factor_db_factors = factordb_factor(n, num_retries=0, sleep_time=0)
        if factor_db_factors != -1:
            return factor_db_factors
    return yafu.factor(n, threads=threads, work=work)


def distinct_factors(n, factors=None, divisors=__trialdivisors, check_factor_db=True, num_retries=10, sleep_time=2):
    if factors is None:
        factors = factorize(n, divisors=divisors, check_factor_db=check_factor_db)
    return list(set(factors))


def factors_as_dict(n, factors=None, divisors=__trialdivisors, check_factor_db=True, threads=1, work=None):
    if factors is None:
        factors = factorize(n, divisors=divisors, check_factor_db=check_factor_db, threads=threads, work=work)
    if factors == -1:
        return -1
    multiplicity = {}
    for factor in factors:
        multiplicity[factor] = multiplicity.get(factor, 0) + 1
    return multiplicity


def phi(n, factors=None, divisors=__trialdivisors, check_factor_db=True, threads=1, work=None):
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    if n < 2:
        return gmpy2.mpz(1)
    factor_dict = factors_as_dict(n, factors=factors, divisors=divisors, check_factor_db=check_factor_db, threads=threads, work=work)
    if factor_dict == -1:
        return -1
    return math.prod([p-1 for p, k in factor_dict.items()]) * math.prod([pow(p, k - 1) for p, k in factor_dict.items()])


def number_of_divisors(n, factors=None, divisors=__trialdivisors, check_factor_db=True, threads=1, work=None):
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    if n == 1:
        return 1
    signature = prime_signature(n, factors=factors, divisors=divisors, check_factor_db=check_factor_db, threads=threads, work=work)
    if signature == -1:
        return -1
    return math.prod([exponent + 1 for exponent in signature])


def sigma(n, factors=None, x=1, divisors=__trialdivisors, check_factor_db=True, threads=1, work=None):
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    if n == 1:
        return gmpy2.mpz(1)
    factor_dict = factors_as_dict(n, factors=factors, divisors=divisors, check_factor_db=check_factor_db, threads=threads, work=work)
    if factor_dict == -1:
        return -1
    return math.prod([sum([pow(prime, j * x) for j in range(exponent + 1)]) for prime, exponent in factor_dict.items()])


def prime_signature(n, factors=None, divisors=__trialdivisors, check_factor_db=True, threads=1, work=None):
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    if n == 1:
        return [1]
    factor_dict = factors_as_dict(n, factors=factors, divisors=divisors, check_factor_db=check_factor_db, threads=threads, work=work)
    if factor_dict == -1:
        return -1
    return list(factor_dict.values())


def smallest_prime_factor(n, divisors=__trialdivisors, check_factor_db=True, digit_limit=10):
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    if n < 2:
        return n
    factors = trial_div_until(n, 2, divisors)
    if len(factors) > 1:
        return factors[0]
    if prime.is_prime(factors[0], check_factor_db=check_factor_db):
        return factors[0]
    else:
        factordb_smallest_factor = factordb_get_smallest_factor(n, num_retries=0, sleep_time=0, digit_limit=digit_limit)
        if factordb_smallest_factor != -1:
            return factordb_smallest_factor
        # weren't able to easily fully factor or find the full factorization for this one, so now we commence
        # infinite trial division, which will either keep going until it finds a factor, reaches 2^64 (I think)
        # or the surrounding cpu timer code kills it
        return infinite_trial_div(n, until=2)[0]


def biggest_prime_factor(n, divisors=__trialdivisors, check_factor_db=True, threads=1, work=None):
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    if n < 2:
        return n
    factors = trial_div_until(n, until=None, divisors=divisors)
    if prime.is_prime(factors[-1], check_factor_db=check_factor_db):
        return factors[-1]
    else:
        factordb_biggest_factor = factordb_get_biggest_factor(n, num_retries=0, sleep_time=0)
        if factordb_biggest_factor != -1:
            return factordb_biggest_factor
        return yafu.factor(n, threads=threads, work=work)[-1]


# digit limit is the number of digits below which we are fairly certain we have the smallest prime factor
def factordb_get_smallest_factor(n, num_retries=10, sleep_time=2, digit_limit=10):
    logging.debug(f"Checking factordb for smallest factor of: {n}")
    f = FactorDB(n)
    f.connect()
    status = f.get_status()
    if status in ["P", "PRP", "Prp"]:
        return n
    if status in ["FF"]:
        return f.get_factor_list()[0]
    factors = f.get_factor_list()
    if not factors:
        return -1
    if len(factors) == 1 or gmpy2.num_digits(factors[0]) > digit_limit:
        if num_retries >= 0:
            if sleep_time > 0:
                logging.info(
                    f"Sleeping for {sleep_time} seconds after inconclusive status ({status}) on FactorDB for value: {n}")
                time.sleep(sleep_time)
            recurse_val = factordb_get_smallest_factor(n, num_retries - 1, sleep_time=sleep_time * 2, digit_limit=digit_limit)
            if recurse_val != -1:
                return recurse_val
        logging.debug(f"Unable to find smallest factor for {n}")
        return -1
    else:
        return factors[0]


def factordb_get_biggest_factor(n, num_retries=10, sleep_time=2):
    logging.debug(f"Checking factordb for biggest factor of: {n}")
    f = FactorDB(n)
    f.connect()
    status = f.get_status()
    if status in ["P", "PRP", "Prp"]:
        return n
    if status in ["FF"]:
        return f.get_factor_list()[-1]
    if num_retries >= 0:
        if sleep_time > 0:
            logging.info(
                f"Sleeping for {sleep_time} seconds after inconclusive status ({status}) on FactorDB for value: {n}")
            time.sleep(sleep_time)
        recurse_val = factordb_get_biggest_factor(n, num_retries - 1, sleep_time=sleep_time * 2)
        if recurse_val != -1:
            return recurse_val
    logging.debug(f"Unable to find biggest factor for {n}")
    return -1


def factordb_factor(n, num_retries=10, sleep_time=2):
    logging.debug(f"Checking factordb for prime factors of: {n}")
    f = FactorDB(n)
    f.connect()
    status = f.get_status()
    if status in ["P", "PRP", "Prp", "Unit"]:
        return [n]
    if status in ["FF"]:
        return f.get_factor_list()
    if num_retries >= 0:
        if sleep_time > 0:
            logging.info(
                f"Sleeping for {sleep_time} seconds after inconclusive status ({status}) on FactorDB for value: {n}")
            time.sleep(sleep_time)
        recurse_val = factordb_factor(n, num_retries - 1, sleep_time=sleep_time * 2)
        if recurse_val != -1:
            return recurse_val
    logging.debug(f"Unable to find full factors for {n}")
    return -1


def factordb_prime_signature(n, num_retries=10, sleep_time=2):
    logging.debug(f"Checking factordb for prime signature of: {n}")
    f = FactorDB(n)
    f.connect()
    status = f.get_status()
    if status in ["P", "PRP", "Prp", "Unit"]:
        return [1]
    if status in ["FF"]:
        return [factor_tuple[1] for factor_tuple in f.get_factor_from_api()]
    if num_retries >= 0:
        if sleep_time > 0:
            logging.info(
                f"Sleeping for {sleep_time} seconds after inconclusive status ({status}) on FactorDB for value: {n}")
        time.sleep(sleep_time)
        recurse_val = factordb_prime_signature(n, num_retries - 1, sleep_time=sleep_time * 2)
        if recurse_val != -1:
            return recurse_val
    logging.debug(f"Unable to find prime signature for {n}")
    return -1


def factordb_get_remaining_composites(n):
    logging.debug(f"Checking factordb for remaining composite factors of: {n}")
    f = FactorDB(n)
    f.connect()
    status = f.get_status()
    if f.result is None:  # probably number too big
        return [n]
    if status in ["P", "PRP", "Prp", "Unit", "FF"]:
        return []
    if status in ["C", "U"]:
        return [n]
    if status in ["CF"]:
        return list(filter(lambda x: not prime.is_prime(x, check_factor_db=True, care_probable=True), f.get_factor_list()))
    assert False, f"Unknown factordb status: {status} for {n}"



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


def trial_div_until_distinct(n, until=None, divisors=__trialdivisors):
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    factors = [n]
    distincts = set(factors)
    if n == 1:
        return factors
    remainder = n
    for d in divisors:
        if until is not None and len(distincts) >= until:
            return factors
        if d >= remainder:
            break
        while d < remainder and gmpy2.is_divisible(remainder, d):
            remainder = remainder//d
            factors = factors[:-1] + [d, remainder]
            distincts.add(d)
            if until is not None and len(distincts) >= until:
                return factors
    return factors


# useful for guaranteeing we have the smallest factor when the number isn't fully factored
def infinite_trial_div(n, until=None):
    return trial_div_until(n, until=until, divisors=prime.generator())


def get_all_proper_divisors(n, threads=1, work=None):
    if n < 2:
        return []
    factor_dict = factors_as_dict(n, threads=threads, work=work)
    factor_powers_lists = [[pow(factor, e) for e in range(exponent+1)] for factor, exponent in factor_dict.items()]
    factor_powers_generator_list = [(factor_power for factor_power in factor_power_list) for factor_power_list in factor_powers_lists]
    this_factor_power_list = [next(factor_powers_generator) for factor_powers_generator in factor_powers_generator_list]
    divisors = []
    while True:
        divisor = math.prod(this_factor_power_list)
        if divisor == n:
            return divisors
        divisors.append(divisor)
        for i, generator in enumerate(factor_powers_generator_list):
            next_factor_power = next(generator, None)
            if next_factor_power:
                this_factor_power_list[i] = next_factor_power
                break
            factor_powers_generator_list[i] = (factor_powers for factor_powers in factor_powers_lists[i])
            this_factor_power_list[i] = next(factor_powers_generator_list[i])


def aliquot_sum(n, threads=1, work=None):
    return sum(get_all_proper_divisors(n, threads=threads, work=None))