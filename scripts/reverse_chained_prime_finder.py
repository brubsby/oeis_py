import cProfile
import copy
import itertools
import logging
import random

import gmpy2
from modules import prime

_prime_cache = {}


def is_valid_n_exception_reverse_chained_prime(n_str, exceptions, prefix="", prefailures=0):
    if type(n_str) != str:
        n_str = str(n_str)
    prime_string = prefix + n_str
    failures = prefailures
    for i in range(1, len(prime_string)+1):
        if is_prime(prime_string[-i:]) == 0:
            failures += 1
        if failures > exceptions:
            return 0
    if failures == exceptions:
        return 2
    if failures < exceptions:
        return 1


prime_last_digits = ["1", "3", "7", "9"]
digits = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
fail_digits = list(filter(lambda digit: digit not in prime_last_digits, digits))
random.shuffle(prime_last_digits)
random.shuffle(fail_digits)
digits = prime_last_digits + fail_digits

# yield stochastic solutions based off the starting parameters
def random_n_exception_chained_reverse_prime_generator(start_n="", exceptions=5, start_exceptions=0):
    if type(start_n) != str:
        start_n = str(start_n)
    if not start_n:
        for digit in digits:
            if is_prime(digit):
                yield from random_n_exception_chained_reverse_prime_generator(digit, exceptions=exceptions,
                                                                              start_exceptions=start_exceptions)
            elif exceptions > start_exceptions:
                yield from random_n_exception_chained_reverse_prime_generator(digit, exceptions=exceptions,
                                                                              start_exceptions=start_exceptions + 1)
            else:
                yield digit
        return
    valid_n = start_n
    current_exceptions = start_exceptions
    prime_digits = ""
    for next_digit in digits:
        candidate_str = next_digit + valid_n
        candidate_val = gmpy2.mpz(candidate_str)
        if is_prime(candidate_val):
            # prime formed is valid, continue yielding
            prime_digits += next_digit
            yield from random_n_exception_chained_reverse_prime_generator(candidate_str, exceptions=exceptions, start_exceptions=current_exceptions)
    # out of exceptions, yield self (the only time anything is actually yielded)
    if current_exceptions >= exceptions:
        yield valid_n
        return
    non_prime_digits = filter(lambda digit: digit not in prime_digits, digits)
    for next_digit in non_prime_digits:
        # we still have failures we can do, yield all the fail trees below
        yield from random_n_exception_chained_reverse_prime_generator(next_digit + valid_n, exceptions=exceptions, start_exceptions=current_exceptions + 1)
    # yielded all possibilities at this level


def is_prime(p):
    if type(p) != gmpy2.mpz:
        p = gmpy2.mpz(p)
    if p in _prime_cache:
        return _prime_cache[p]
    result = prime.is_prime(p)
    _prime_cache[p] = result
    return result


def get_failure_composites(n):
    if not n:
        return []
    if type(n) != str:
        n = str(n)
    return list(map(str, filter(lambda s: is_prime(s) == 0, (gmpy2.mpz(n[-i:]) for i in range(0, len(n))))))


def roundrobin(*iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # Recipe credited to George Sakkis
    num_active = len(iterables)
    nexts = itertools.cycle(iter(it).__next__ for it in iterables)
    while num_active:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            # Remove the iterator we just exhausted from the cycle.
            num_active -= 1
            nexts = itertools.cycle(itertools.islice(nexts, num_active))
            logging.info("exhausted a generator")


# create a round-robin generator that generates points from
def get_generator_panel_for_best(best, exceptions=5):
    failure_composites = get_failure_composites(best)
    logging.info(f"failures: {', '.join(failure_composites)}")
    generators = [random_n_exception_chained_reverse_prime_generator("", exceptions=exceptions, start_exceptions=0)]
    for i, composite in enumerate(failure_composites):
        branch = composite[1:]
        if not branch:
            continue
        generators.append(random_n_exception_chained_reverse_prime_generator(branch, exceptions=exceptions, start_exceptions=i))
    return roundrobin(*generators)


def main(record, exceptions=5, panel=True):
    best = str(record)
    print(f"starting candidate: {best}")
    print(f"len: {len(best)}")
    while True:
        again = False
        if panel:
            generator = get_generator_panel_for_best(best, exceptions=exceptions)
        else:
            generator = random_n_exception_chained_reverse_prime_generator("", exceptions=exceptions, start_exceptions=0)
        for candidate in generator:
            if not best or len(candidate) >= len(best) and gmpy2.mpz(best) < gmpy2.mpz(candidate):
                if not is_valid_n_exception_reverse_chained_prime(candidate, exceptions=exceptions):
                    continue
                best = candidate
                print(best)
                print(f"len: {len(best)}")
                again = True
                break
        if not again:
            exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    profile = False
    best = "963129963136248319687995918918997653319693967"
    exceptions = 5
    panel = True


    print(is_valid_n_exception_reverse_chained_prime(best, exceptions=exceptions))
    if profile:
        cProfile.run(f"main({best}, exceptions={exceptions}, panel={panel})")
    else:
        main(best, exceptions=exceptions, panel=panel)


