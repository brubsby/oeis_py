import itertools
import logging
import math
import os
import subprocess
import shutil
import time
import timeit

import gmpy2
import primesieve
import uuid

from modules.factordb import FactorDB

__trialdivisors = primesieve.primes(2, int(1e6))
__primes_set = frozenset(primesieve.primes(2, int(1e7)))
# https://github.com/aleaxit/gmpy/issues/354#issuecomment-1404620217
__gmp_BPSW_LIMIT = (21 * pow(gmpy2.mpz(10), gmpy2.mpz(15)))//10
__pfgw_factordb_digit_limit = 20000
# don't even trial_div if it's more than 5000 digits, as we'll probably be slow
__in_house_trialdiv_digit_limit = 100
# gmpy2.is_prime is pretty fast up to


# public api, 0 composite, 1 probable prime, 2 definite prime
def is_prime(n, check_factor_db=False, care_probable=True, factordb_pfgw_limit=__pfgw_factordb_digit_limit, trial_div_limit=__in_house_trialdiv_digit_limit):
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    # below this limit we know gmpy2 does not get fooled by prps and is pretty fast
    if n < __gmp_BPSW_LIMIT:
        return gmpy2_is_prime(n)
    # trial div under a certain size
    if trial_div_limit and n < trial_div_limit:
        trial_div_prime_test_result = trial_div_prime_test(n)
        if trial_div_prime_test_result == 0 or trial_div_prime_test_result == 2:
            return trial_div_prime_test_result
    # look it up on factordb first if it's above a certain size
    # if below this size, it's maybe faster to just test, and maybe a bit more polite
    if gmpy2.num_digits(n) > factordb_pfgw_limit:
        if check_factor_db:
            factordb_result = check_factordb_prime(n, retries=0, sleep_time=0)
            if factordb_result != -1:
                return factordb_result
        return prp_test_pfgw(n)  # not checking factordb, just test
    else:
        pfgw_result = prp_test_pfgw(n)  # smaller number, start with pfgw, it might do more trial div than we did
        if check_factor_db and care_probable:  # we have the pfgw result, but want to check with factordb if we got probable prime
            if pfgw_result != 1:
                return pfgw_result
            # we were told to check factordb, at least see if factordb knows for sure
            # if we haven't been able to figure it out
            factordb_result = check_factordb_prime(n, retries=0, sleep_time=0)
            if factordb_result in [0, 1, 2]:
                return factordb_result
            return pfgw_result  # return the pfgw result (1) if factordb messed up
        return pfgw_result


def gmpy2_is_prime(n):
    is_prime = gmpy2.is_prime(n)
    if n < __gmp_BPSW_LIMIT:
        return 2 if is_prime else 0
    else:
        return 1 if is_prime else 0


def trial_div_prime_test(n, divisors=__trialdivisors):
    if n in __primes_set:
        return 2
    for d in divisors:
        if gmpy2.is_divisible(n, d):
            return 0
    return -1


def check_factordb_prime(expr, retries=3, sleep_time=5):
    str_expression = str(expr)
    text = f"{len(str_expression)} char expression: {str_expression[:10] + '...' + str_expression[-10:]}" if len(
        str_expression) > 100 else expr
    logging.info(f"Checking factordb for prime status of: {text}")
    f = FactorDB(expr)
    f.connect()
    status = f.get_status()
    if status in ["P"]:
        return 2
    elif status in ["PRP", "Prp"]:
        return 1
    elif status == "U":
        if retries > 0:
            if sleep_time > 0:
                time.sleep(sleep_time)
            recurse_val = check_factordb_prime(expr, retries - 1, sleep_time=sleep_time * 2)
            if recurse_val in [0, 1, 2]:
                return recurse_val
        return -1
    else:
        return 0


def prp_test_pfgw(expr):
    start_time = time.time()
    str_expression = str(expr)
    this_uuid = uuid.uuid4()
    dirpath = os.path.join("..", "data", "temp", str(this_uuid))
    filename = f"temp-{this_uuid}.dat"
    temp_filepath = os.path.join(dirpath, filename)
    try:
        os.makedirs(dirpath, exist_ok=True)
        with open(temp_filepath, "w") as temp:
            temp.write(str_expression)
            temp.write("\n")
        is_prp = False
        is_trivially_prime = False
        proc = subprocess.Popen([
            "C:/Users/Tyler/Downloads/pfgw_win_4.0.4/distribution/pfgw64.exe",
            "-k", filename,  # "-f0",
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,
            cwd=dirpath)
        info_logged = False
        for i, line in enumerate(proc.stdout):
            if not info_logged and time.time() - start_time > 1:
                text = f"{len(str_expression)} char expression: {str_expression[:10] + '...' + str_expression[-10:]}" if len(
                    str_expression) > 100 else expr
                logging.info(f"PFGW testing {text}")
                info_logged = True
            logging.debug(line[:-1])
            if "trivially prime!" in line:
                is_trivially_prime = True
            if "3-PRP" in line:
                is_prp = True
            if "Evaluator failed" in line:
                raise Exception("PFGW had trouble evaluating the expression")
            elif "Error opening file" in line:
                raise Exception(f"PFGW couldn't open temp file {temp_filepath}")
        proc.wait()
        os.remove(temp_filepath)
    finally:
        # cleanup temp dir
        shutil.rmtree(dirpath, ignore_errors=True)
    assert not (is_prp and is_trivially_prime)
    if is_trivially_prime:
        return 2
    if is_prp:
        return 1
    return 0


def generator(start=0, start_nth=False):
    iterator = primesieve.Iterator()
    if start_nth:
        assert start > 0
        for i in range(start-1):
            iterator.next_prime()
    else:
        iterator.skipto(max(start-1, 0))
    while True:
        yield iterator.next_prime()


# tested this to be the fastest way to do it out of a lot
def nth_primorial(n):
    return math.prod(primesieve.n_primes(n), start=gmpy2.mpz(1))


if __name__ == "__main__":

    print(next(generator))

    code = """
import random
import primetest
import gmpy2
random.seed(42)
magnitude = {}
low = pow(gmpy2.mpz(10), gmpy2.mpz(magnitude))
high = low * 10
for i in range({}):
    num = gmpy2.mpz(random.randrange(low, high))
    {}
"""
    functions = [
        "primetest.is_prime(num)",
        "primetest.trial_div_prime_test(num)",
        "primetest.prp_test_pfgw(num)",
    ]
    for magnitude_counter in itertools.count(start=124):
        magnitude = 1000 * magnitude_counter
        tests = 1
        for i, function in enumerate(functions):
            # if i == 2 and magnitude < 100000:
            #     break
            print(f"{timeit.timeit(code.format(magnitude, tests, function), number=1):.010f}, ", end="")
        print(f"magnitude: {magnitude}")