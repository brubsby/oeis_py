import itertools
import logging

import gmpy2

__tridigital_lookup = []
__tridigital_lookup_len = 0
__lookup_depth = 15


def generator(digits, lower_length=1, upper_length=None):
    assert lower_length > 0, "lower_length must be at least 1"
    digits = list(map(gmpy2.mpz, digits))
    digit_iterables = [digits]
    x10_lambda = lambda x: x * 10
    while len(digit_iterables) < lower_length:
        last_digits = digit_iterables[0]
        digit_iterables.insert(0, list(map(x10_lambda, last_digits)))
    for digit_length in range(lower_length, upper_length + 1):
        yield from _tridigital_generator_helper(*digit_iterables)
        last_digits = digit_iterables[0]
        digit_iterables.insert(0, list(map(x10_lambda, last_digits)))


def _tridigital_generator_helper(*args):
    # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
    # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
    pools = [tuple(pool) for pool in args]
    if len(pools) == __tridigital_lookup_len:
        yield from iter(__tridigital_lookup)
    elif __lookup_depth > len(pools) > __tridigital_lookup_len:
        _tridigital_lookup = list(_tridigital_generator_helper_2(0, *pools))
        _tridigital_lookup_len = len(pools)
        yield from iter(_tridigital_lookup)
    else:
        yield from _tridigital_generator_helper_2(0, *pools)


def _tridigital_generator_helper_2(number, *args):
    pools = [tuple(pool) for pool in args]
    if len(pools) == __tridigital_lookup_len:
        for value in __tridigital_lookup:
            yield number + value
        return
    if len(pools) == 0:
        yield number
        return
    if len(pools) == 1:
        for value in pools[0]:
            yield number + value
        return
    for value in pools[0]:
        yield from _tridigital_generator_helper_2(number + value, *pools[1:])


def triangular_tridigit_generator(digits, start=1):
    assert len(digits) == 3
    assert all(map(lambda digit: type(digit) == int, digits))
    start_digits = len(str(start))
    digit_set = set(map(str, digits))
    digits = list(map(gmpy2.mpz, digits))
    digit_iterables = [digits]
    x10_lambda = lambda x: x * 10
    l = start_digits
    n = gmpy2.mpz(gmpy2.ceil((l + 1) / 2))
    while len(digit_iterables) < n:
        last_digits = digit_iterables[0]
        digit_iterables.insert(0, list(map(x10_lambda, last_digits)))
    for l in itertools.count(start=l):
        if gmpy2.mpz(gmpy2.ceil((l + 1) / 2)) > n:
            n = gmpy2.mpz(gmpy2.ceil((l + 1) / 2))
            last_digits = digit_iterables[0]
            digit_iterables.insert(0, list(map(x10_lambda, last_digits)))
        ln = l - n
        tentoln = pow(10, ln)
        for m in _tridigital_generator_helper(*digit_iterables):
            t = gmpy2.isqrt(8 * m * tentoln) + 1
            if gmpy2.is_even(t):
                t += 1
            q = (pow(t, 2) - 1) // 8
            if q // tentoln != m:
                continue
            if set(gmpy2.digits(q)) <= digit_set and start <= q:
                yield q
        logging.info(f"finished searching {l} digits")


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()

    # accept list of arguments
    # like -d 1 2 3
    p.add_argument('-d', nargs="+", type=int)
    args = p.parse_args()

    # check if input is valid
    d = args.d

    # check if "a" is in proper range.
    if not (min(d) >= 0 and max(d) <= 9 and len(d) == 3 and len(set(d)) == 3):
        raise Exception(f"invalid arguments for digits {d}")

    logging.basicConfig(level=logging.INFO)
    digits = d
    maxchars = 260
    terms = set()
    char_len = 0
    retval = ""
    for i, term in enumerate(triangular_tridigit_generator(digits), start=1):
        if term in terms:
            continue
        terms.add(term)
        term_str = str(term)
        term_len = len(term)
        if i == 1:
            retval += term_str
            print(term_str)
            char_len += term_len
            if (char_len * 2) + 2 > maxchars:
                break
            continue
        candidate = ", " + term_str
        candidate_len = len(candidate)
        if char_len + candidate_len > maxchars:
            print(f"term {term} pushes data section over the {maxchars} char limit, stopping")
            break
        retval += candidate
        print(retval)
        char_len += candidate_len

    print()
    print(retval)
    print()
    print(f"a()-a({len(terms) - 1}) from")
