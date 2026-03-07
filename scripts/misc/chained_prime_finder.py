import cProfile
import itertools
import logging
import random

import gmpy2
from oeispy.utils import prime


_prime_cache = {}

def is_valid_n_exception_chained_prime(n_str, exceptions, prefix="", prefailures=0):
    if type(n_str) != str:
        n_str = str(n_str)
    prime_string = prefix + n_str
    failures = prefailures
    for i in range(1, len(prime_string)+1):
        if is_prime(prime_string[0:i]) == 0:
            failures += 1
        if failures > exceptions:
            return 0
    if failures == exceptions:
        return 2
    if failures < exceptions:
        return 1


prime_last_digits = ["1", "3", "7", "9"]
digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
fail_digits = list(filter(lambda digit: digit not in prime_last_digits, digits))
random.shuffle(prime_last_digits)
random.shuffle(fail_digits)
digits = prime_last_digits + fail_digits


# yield stochastic solutions based off the starting parameters
def random_n_exception_chained_prime_generator(start_n="", exceptions=5, start_exceptions=0):
    if type(start_n) != str:
        start_n = str(start_n)
    if not start_n:
        for digit in digits:
            if is_prime(gmpy2.mpz(digit)):
                yield from random_n_exception_chained_prime_generator(digit, exceptions=exceptions,
                                                                      start_exceptions=start_exceptions)
            elif exceptions > start_exceptions:
                yield from random_n_exception_chained_prime_generator(digit, exceptions=exceptions,
                                                                      start_exceptions=start_exceptions + 1)
            else:
                yield digit
        return
    while True:
        valid_n = start_n
        current_exceptions = start_exceptions
        while True:
            for next_digit in prime_last_digits:
                if next_digit in prime_last_digits and is_prime(gmpy2.mpz(valid_n + next_digit)):
                    # prime formed is valid, continue yielding
                    yield from random_n_exception_chained_prime_generator(valid_n+next_digit, exceptions=exceptions, start_exceptions=current_exceptions)
            for next_digit in fail_digits:
                    # out of exceptions, yield self (the only time anything is actually yielded)
                    if current_exceptions >= exceptions:
                        yield valid_n
                        return
                    # we still have failures we can do, yield all the fail trees below
                    yield from random_n_exception_chained_prime_generator(valid_n+next_digit, exceptions=exceptions, start_exceptions=current_exceptions+1)
            # yielded all possibilities at this level, break out
            return


def get_failure_composites(n):
    if not n:
        return []
    if type(n) != str:
        n = str(n)
    return list(map(str, filter(lambda s: is_prime(s) == 0, (gmpy2.mpz(n[0:i]) for i in range(1, len(n)+1)))))

def is_prime(p):
    if type(p) != gmpy2.mpz:
        p = gmpy2.mpz(p)
    if p in _prime_cache:
        return _prime_cache[p]
    result = prime.is_prime(p)
    _prime_cache[p] = result
    return result


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
    generators = [random_n_exception_chained_prime_generator("", exceptions=exceptions, start_exceptions=0)]
    for i, composite in enumerate(failure_composites):
        branch = composite[:-1]
        if not branch:
            continue
        generators.append(random_n_exception_chained_prime_generator(branch, exceptions=exceptions, start_exceptions=i))
    return roundrobin(*generators)


def main(record, exceptions=5):
    best = str(record)
    print(f"starting candidate: {best}")
    print(f"len: {len(best)}")
    while True:
        again = False
        for candidate in get_generator_panel_for_best(best, exceptions=exceptions):
            if not best or len(candidate) >= len(best) and gmpy2.mpz(best) < gmpy2.mpz(candidate):
                best = candidate
                print(best)
                print(f"len: {len(best)}")
                again = True
                break
        if not again:
            exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(is_valid_n_exception_chained_prime("73327337879693992314139313", exceptions=5))
    profile = False
    if profile:
        cProfile.run("main(5)")
    else:
        main("73327337879693992314139313", exceptions=5)

