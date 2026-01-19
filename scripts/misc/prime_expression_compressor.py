import itertools
import logging
import math
from functools import cache

import gmpy2

from oeispy.utils import expression


@cache
def log2base(base):
    return gmpy2.log2(base)


@cache
def expcalc(complog2, base):
    return int(round(complog2/log2base(base)))

@cache
def biggest_number_in_length(length):
    if length == 0:
        return 0
    if length == 1:
        return 9
    if length == 2:
        return 99
    return pow(gmpy2.mpz(9), int("9" * (length - 2))) if length < 7 else math.inf

@cache
def powplusminusc(composite, record_len=None, depth=1):
    record = str(gmpy2.digits(composite))
    # if record_len is not None and record_len < 5:
    #     return record
    if composite > biggest_number_in_length(record_len):
        return record
    logging.debug(f"inside {composite}, record_len={record_len}, depth={depth}")
    complog2 = gmpy2.log2(composite)
    if record_len is None:
        record_len = len(record)
    for base in itertools.count(2):
        # logging.debug(f"inside {composite}, record_len={record_len}, depth={depth}, base={base}")
        exponent = expcalc(complog2, base)
        if exponent < 2:
            break
        power = pow(base, exponent)
        pow_len = len(str(base)) + len(str(exponent)) + 1
        diff = composite - power
        diff_len = gmpy2.num_digits(diff)
        if pow_len + 2 > record_len:
            continue
        diffstr = diff # powplusminusc(abs(diff), record_len - pow_len, depth=depth+1)
        candidate = f"{base}^{exponent}{'+' if diff > 0 else '-'}{diffstr}"
        # candidate = f"{base}^{exponent}{diff:+d}"
        if len(candidate) < record_len:
            record = candidate
            record_len = len(record)
            logging.debug(f"New record: {record}")
    return record


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    composite_str = "(1361^3+6)^3+80"
    composite = expression.evaluate(composite_str)
    print(powplusminusc(composite, len(composite_str)+1))
