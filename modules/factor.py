import copy
import functools
import heapq
import itertools
import logging
import math
import random
import time

import gmpy2
import primesieve
from modules import prime
from modules.factordb import FactorDB
from modules import yafu
import sequences.A000945 as A000945
import sequences.A051328 as A051328
import sequences.A051309 as A051309
import sequences.A051334 as A051334
import sequences.A051335 as A051335
import sequences.A051308 as A051308

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


def timed_factorize(n, timeout=1, divisors=__trialdivisors, threads=1):
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    if n < 2:
        return []
    if gmpy2.num_digits(n) < 20:
        factors = trial_div_until(n, until=None, divisors=divisors)
        fully_factored = prime.is_prime(factors[-1], trial_div_limit=None)
        if fully_factored:
            return factors
    return yafu.factor(n, threads=threads)


def distinct_factors(n, factors=None, threads=1, divisors=__trialdivisors, check_factor_db=True, work=None):
    if factors is None:
        factors = factorize(n, threads=threads, divisors=divisors, check_factor_db=check_factor_db, work=work)
    return list(set(factors))


def factors_as_dict(n, factors=None, divisors=__trialdivisors, check_factor_db=True, threads=1, work=None):
    if factors is None:
        factors = factorize(n, divisors=divisors, check_factor_db=check_factor_db, threads=threads, work=work)
    multiplicity = {}
    for factor in factors:
        multiplicity[factor] = multiplicity.get(factor, 0) + 1
    return multiplicity


def is_squarefree(n, factors=None, divisors=__trialdivisors, check_factor_db=True, threads=1, work=None):
    trial_div_factors = trial_div_until(n, until=None, divisors=divisors)
    if len(trial_div_factors) > len(set(trial_div_factors)):
        return False
    factor_dict = factors_as_dict(n, factors=factors, divisors=divisors, check_factor_db=check_factor_db, threads=threads, work=work)
    return not any(map(lambda f: f > 1, factor_dict.values()))



def factor_dict_to_value(factor_dict):
    return math.prod(pow(prime_factor, multiplicity) for prime_factor, multiplicity in factor_dict.items())


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


# number of distinct factors
def little_omega(n, factors=None, divisors=__trialdivisors, check_factor_db=True, threads=1, work=None):
    return len(distinct_factors(n, factors=factors, threads=threads, divisors=divisors, check_factor_db=check_factor_db, work=work))


# number of prime factors (with duplicity)
def big_omega(n, factors=None, divisors=__trialdivisors, check_factor_db=True, threads=1, work=None):
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    if n == 1:
        return gmpy2.mpz(0)
    if type(factors) == dict:
        factor_dict = factors
    else:
        factor_dict = factors_as_dict(n, factors=factors, divisors=divisors, check_factor_db=check_factor_db, threads=threads, work=work)
    if factor_dict == -1:
        return -1
    return sum(factor_dict.values())


def sigma(n, factors=None, x=1, divisors=__trialdivisors, check_factor_db=True, threads=1, work=None):
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    if n == 1:
        return gmpy2.mpz(1)
    if type(factors) == dict:
        factor_dict = factors
    else:
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


def smallest_prime_factor(n, divisors=__trialdivisors, check_factor_db=True, digit_limit=10, threads=1):
    checked_factordb = False
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    if n < 2:
        return n
    factors = trial_div_until(n, 2, divisors)
    if len(factors) > 1:
        return factors[0]
    if prime.is_prime(factors[0], check_factor_db=check_factor_db, trial_div_limit=None):
        return factors[0]
    else:
        num_digits = gmpy2.num_digits(n)
        if check_factor_db and num_digits >= 50:
            factordb_smallest_factor = factordb_get_smallest_factor(n, num_retries=0, sleep_time=0, digit_limit=digit_limit)
            checked_factordb = True
            if factordb_smallest_factor != -1:
                return factordb_smallest_factor
        # trying to factor the whole number is a bit silly if it's large, so just do trialdiv and hope we're kinda lucky
        # if gmpy2.num_digits(n) > 140:
        #     # weren't able to easily fully factor or find the full factorization for this one, so now we commence
        #     # infinite trial division, which will either keep going until it finds a factor, reaches 2^64 (I think)
        #     # or the surrounding cpu timer code kills it
        #     return infinite_trial_div(n, until=2)[0]
        # else:
            # should be easy enough, just factor
        return factorize(n, check_factor_db=check_factor_db and not checked_factordb, threads=threads)[0]


def smallest_prime_factor_generator(n, divisors=__trialdivisors, check_factor_db=True, digit_limit=10):
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    if n < 2:
        yield n
        return
    remaining_composite = n
    factors = trial_div_until(remaining_composite, 2, divisors)
    while len(factors) > 1:
        yield factors[0]
        if prime.is_prime(factors[1], check_factor_db=check_factor_db):
            yield factors[1]
            return
        remaining_composite = factors[1]
        factors = trial_div_until(remaining_composite, 2, divisors)

    factordb_smallest_factor = 1
    while factordb_smallest_factor != -1:
        factordb_smallest_factor = factordb_get_smallest_factor(remaining_composite, num_retries=0, sleep_time=0, digit_limit=digit_limit)
        if factordb_smallest_factor != -1:
            yield factordb_smallest_factor
            remaining_composite = remaining_composite // factordb_smallest_factor
            if prime.is_prime(remaining_composite, check_factor_db=check_factor_db):
                yield remaining_composite
                return

    not_prime = True
    while not_prime:
        factors = infinite_trial_div(remaining_composite, until=2)
        yield factors[0]
        remaining_composite = factors[1]
        not_prime = prime.is_prime(remaining_composite)
    yield remaining_composite


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
    if len(factors) == 1 or (digit_limit and gmpy2.num_digits(factors[0]) > digit_limit):
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
    if status is None:  # probably number too big
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
    logging.info(f"Running infinite trial div for {n}")
    return trial_div_until(n, until=until, divisors=prime.generator())


def antidivisors(n, threads=1):
    retval = []
    for d in divisors(n, threads=threads):
        y = 2*d
        if n > y and n % y:
            retval.append(y)
    for d in divisors(2*n-1, threads=threads):
        if n > d >= 2 and n % d:
            retval.append(d)
    for d in divisors(2*n+1, threads=threads):
        if n > d >= 2 and n % d:
            retval.append(d)
    return list(sorted(retval))


def divisors(n, threads=1, work=None, proper=False):
    ret = proper_divisors(n, threads=threads, work=work)
    if proper:
        return ret
    elif n < 2:
        return []
    else:
        return [gmpy2.mpz(1)] + ret + [n]


def proper_divisors(n, threads=1, work=None):
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
            return list(sorted(divisors))
        if divisor > 1:
            divisors.append(divisor)
        for i, generator in enumerate(factor_powers_generator_list):
            next_factor_power = next(generator, None)
            if next_factor_power:
                this_factor_power_list[i] = next_factor_power
                break
            factor_powers_generator_list[i] = (factor_powers for factor_powers in factor_powers_lists[i])
            this_factor_power_list[i] = next(factor_powers_generator_list[i])


def aliquot_sum(n, threads=1, work=None):
    return 1 + sum(proper_divisors(n, threads=threads, work=work))


def euclid_mullin(start, index):
    # reference the sequence objects where they exist for fast lookups
    assert index > 0
    if index == 1:
        return gmpy2.mpz(start)
    if start == 2:
        return A000945(index)
    if start == 5:
        return A051308(index)
    if start == 11:
        return A051309(index)
    if start == 89:
        return A051328(index)
    if start == 8191:
        return A051334(index)
    if start == 127:
        return A051335(index)
    return smallest_prime_factor(euclid_mullin_product(start, index-1) + 1)


def euclid_mullin_product(start, index):
    start_to_sequence_map = {
        2: A000945,
        5: A051308,
        11: A051309,
        89: A051328,
        8191: A051334,
        127: A051335,

    }
    assert index > 0
    if index == 1:
        return gmpy2.mpz(start)
    # barring some more advanced caching system, hardcode the ones that aren't covered by sequences
    if start == 8581 and index == 30:
        return gmpy2.mpz(141208584732202933985043597872957492707358144318898872118657282339712271572179267100961675026279141122923937150499405940373529391974355377191956123135236318070713628724204458523041098923271739111961931134010370314342166029850673324166944214136572106328571511680331336580294798956198380164563517386197075765008807910833827575527000953962444164505805867723402565423188465258799151305597345590623940408489172824801857943743118709126)
    if start == 32687 and index == 50:
        return gmpy2.mpz(19033201879619270402836051492132922474567096416370720465158118270967813749526574849563756720180026369762174906193978202911884183636178999932103022728084118049163378067635655471312637319818549960822047884032827877827239197034786099291510484521370151175866321866950899079569130034048984181882415094900713147633987083653290880784834771937594801407458270830558180971138040640917443115114371556093261510)
    sequence = None
    if start in start_to_sequence_map:
        sequence = start_to_sequence_map[start]
    if sequence:
        return math.prod(sequence(k) for k in range(1, index+1))
    partial_product = euclid_mullin_product(start, index-1)
    return partial_product * smallest_prime_factor(partial_product + 1, digit_limit=None)


def numbers_with_n_distinct_factors_generator(n):
    size_limit = gmpy2.mpz(gmpy2.floor(gmpy2.exp(4*n-6)))
    exponent_sum_size_limit = n + 3  # 2 * gmpy2.mpz(gmpy2.floor(gmpy2.log2(n))) + 4
    prime_it = primesieve.Iterator()
    prime_generator = prime.generator()
    primes = list(itertools.islice(prime_generator, n))
    factors = copy.copy(primes)
    factors = dict([(prime_factor, 1) for prime_factor in factors])
    value = gmpy2.mpz(factor_dict_to_value(factors))
    heap = [(value, factors)]
    seen_set = set()
    # old_value = 0
    for _ in itertools.count(start=1):
        value, factors = heapq.heappop(heap)
        # logging.debug(f"heap size: {len(heap)}")
        # while value == old_value:
        #     value, factors = heapq.heappop(heap)
        for prime_factor, multiplicity in factors.items():
            if prime_factor == 2:
                new_factors = copy.copy(factors)
                new_factors[prime_factor] += 1
                new_value = value * prime_factor
                if new_value < size_limit and new_value not in seen_set:
                    heapq.heappush(heap, (new_value, new_factors))
                    seen_set.add(new_value)
            prime_it.skipto(prime_factor)
            next_prime = prime_it.next_prime()
            if next_prime not in factors and multiplicity == 1:
                new_factors = copy.copy(factors)
                del new_factors[prime_factor]
                new_factors[next_prime] = 1
                new_value = (value // prime_factor) * next_prime
                if new_value < size_limit and new_value not in seen_set:
                    heapq.heappush(heap, (new_value, new_factors))
                    seen_set.add(new_value)
            elif next_prime in factors and multiplicity > 1:
                new_factors = copy.copy(factors)
                new_factors[prime_factor] -= 1
                new_factors[next_prime] += 1
                new_value = (value // prime_factor) * next_prime
                if new_value < size_limit and new_value not in seen_set:
                    heapq.heappush(heap, (new_value, new_factors))
                    seen_set.add(new_value)
        yield value, factors

        # old_value = value


def generate_factors_by_size(n, divisors=__trialdivisors, check_factor_db=True, digit_limit=10):
    composite = n
    while True:
        smallest = smallest_prime_factor(composite, divisors=divisors, check_factor_db=check_factor_db, digit_limit=digit_limit)
        yield smallest
        composite = composite // smallest
        if composite == 1:
            return


def totient(n, factors=None, threads=1, divisors=__trialdivisors, check_factor_db=True):
    factor_dict = factors_as_dict(n, factors=factors, threads=threads, divisors=__trialdivisors, check_factor_db=True)
    totient = gmpy2.mpz(1)
    for prime, count in factor_dict.items():
        totient *= (prime - 1) * (prime ** (count - 1))
    return totient
