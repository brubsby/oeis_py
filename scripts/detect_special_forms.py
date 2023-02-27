import itertools
import logging
import time
import timeit

import gmpy2
import random

from modules import oeis_factor_db, factor

sqrt_5 = gmpy2.sqrt(5)
golden_ratio = (1 + sqrt_5)/2
half = gmpy2.mpz(1)/gmpy2.mpz(2)


def inverse_fibonacci(f):
    return gmpy2.mpz(gmpy2.floor(gmpy2.log(f*sqrt_5-half)/gmpy2.log(golden_ratio)))


def inverse_lucas(l):
    if l < 1:
        return 0
    return gmpy2.mpz(gmpy2.floor(gmpy2.log(l-1/2)/gmpy2.log(golden_ratio)))


# make sure the input composite isn't divisible by 5 before lol
def find_lucas_sum_form(input_composite):
    # sum form
    for i, composite in enumerate([input_composite, input_composite * 5]):
        # sum
        lucas1n = inverse_lucas(composite)
        lucas1 = gmpy2.lucas(lucas1n)
        while lucas1 < composite:
            lucas1n += 1
            lucas1 = gmpy2.lucas(lucas1n)
        lucas2_target = composite - lucas1
        lucas2n = inverse_lucas(lucas2_target)
        lucas2 = gmpy2.lucas(lucas2n)
        while lucas2 < lucas2_target:
            lucas2n -= 1
            lucas2 = gmpy2.lucas(lucas2n)
        lucas_sum = lucas1 + lucas2
        while lucas1n >= lucas2n:
            if lucas_sum == composite:
                lucas_diff = lucas1n - lucas2n
                if gmpy2.is_even(lucas_diff):
                    k = lucas_diff // 2
                    m = lucas2n
                    if gmpy2.is_even(k):
                        factors = [gmpy2.lucas(k), gmpy2.lucas(k + m)]
                        if factors[0] != 1:
                            logging.info(f"lucas sum found: L{lucas1n}+L{lucas2n}=C{gmpy2.num_digits(composite)}")
                            logging.info(f"lucas sum is of even distance")
                            logging.info(f"lucas sum diff k is even, factors are L{k}*L{k+m}")
                            return factors
                    else:
                        factors = [gmpy2.fib(k), gmpy2.fib(k + m)]
                        if factors[0] != 1:
                            logging.info(f"lucas sum found: L{lucas1n}+L{lucas2n}=C{gmpy2.num_digits(composite)}")
                            logging.info(f"lucas sum is of even distance")
                            logging.info(f"lucas sum diff k is odd, factors are F{k}*F{k+m}")
                            return factors
            if lucas_sum > composite:
                lucas1n -= 1
                lucas1 = gmpy2.lucas(lucas1n)
            else:
                lucas2n += 1
                lucas2 = gmpy2.lucas(lucas2n)
            lucas_sum = lucas1 + lucas2

        # difference
        lucas1n = inverse_lucas(composite)
        lucas1 = gmpy2.lucas(lucas1n)
        while lucas1 < composite:
            lucas1n += 1
            lucas1 = gmpy2.lucas(lucas1n)
        lucas2_target = lucas1 - composite  # positive number
        lucas2n = inverse_lucas(lucas2_target)
        lucas2 = gmpy2.lucas(lucas2n)
        while lucas2 < lucas2_target:
            lucas2n += 1
            lucas2 = gmpy2.lucas(lucas2n)
        lucas_diff = lucas1 - lucas2
        while lucas_diff != 0:
            if lucas_diff == composite:
                k2 = lucas1n - lucas2n
                if gmpy2.is_even(k2):
                    k = k2 // 2
                    m = lucas2n
                    if gmpy2.is_even(k):
                        factors = [gmpy2.fib(k), gmpy2.fib(k + m)]
                        if factors[0] != 1:
                            logging.info(f"lucas diff found: L{lucas1n}-L{lucas2n}=C{gmpy2.num_digits(composite)}")
                            logging.info(f"lucas diff is of even distance")
                            logging.info(f"lucas diff k is even, factors are F{k}*F{k + m}")
                            return factors
                    else:
                        factors = [gmpy2.lucas(k), gmpy2.lucas(k + m)]
                        if factors[0] != 1:
                            logging.info(f"lucas diff found: L{lucas1n}-L{lucas2n}=C{gmpy2.num_digits(composite)}")
                            logging.info(f"lucas diff is of even distance")
                            logging.info(f"lucas diff k is odd, factors are L{k}*L{k + m}")
                            return factors
            if lucas_diff < composite:
                lucas1n += 1
                lucas1 = gmpy2.lucas(lucas1n)
            else:
                lucas2n += 1
                lucas2 = gmpy2.lucas(lucas2n)
            lucas_diff = lucas1 - lucas2


def test_random_fib_or_lucas_product():
    rand_k = random.randrange(10000)
    rand_m = random.randrange(10000)
    is_fib = bool(random.getrandbits(1))
    is_fib_char = 'F' if is_fib else 'L'
    composite = gmpy2.fib(rand_k)*gmpy2.fib(rand_k+rand_m) if is_fib else gmpy2.lucas(rand_k)*gmpy2.lucas(rand_k+rand_m)
    print(f"k = {rand_k}")
    print(f"m = {rand_m}")
    print(f"searching for algebraic factorization of {is_fib_char}{rand_k}*{is_fib_char}{rand_k+rand_m} = {composite})")
    print(f"lucas sum should be L{rand_m+2*rand_k}+-L{rand_m}")
    print(find_lucas_sum_form(composite))


def test_db_composites_for_lucas_addition_special_forms():
    db = oeis_factor_db.OEISFactorDB()
    composites = db.get_all_composites()
    for composite in composites:
        value = composite['value']
        if value:
            result = find_lucas_sum_form(value)
            if result:
                print(f"Composite: {value}")
                print(f"Factors: {result}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # print(timeit.timeit("detect_special_forms.test_random_fib_or_lucas_product()", setup="import detect_special_forms", number=1))
    test_db_composites_for_lucas_addition_special_forms()
    print(gmpy2.square(1431))