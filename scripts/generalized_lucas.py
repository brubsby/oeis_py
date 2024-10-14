import argparse
import itertools
import math
import pathlib
import re
import sys
import time
import traceback

import gmpy2

from modules import factor
from modules import factordb
from modules import prime
from modules import batch_factordb

__version__ = "0.0.1"


def u(p, q, n):
    if p * p == 4 * q:
        s = p//2
        return n * pow(s, n-1)
    return gmpy2.lucasu(p, q, n)


def v(p, q, n):
    if p * p == 4 * q:
        s = p//2
        return 2 * pow(s, n)
    return gmpy2.lucasv(p, q, n)


def factordb_get_factorizaton_string(val, lookup_primes=None, factordb_result=None):
    if lookup_primes is None:
        lookup_primes = set()
    negative_str = ""
    if val in [-1, 0, 1]:
        return str(val)
    if val < 0:
        val = abs(val)
        negative_str = "-1."
    if not factordb_result:
        factordb_result = factordb.FactorDB(val)
        factordb_result.connect()
    else:
        assert factordb_result.get_val() == val, f"batch results probably out of order {val} != {factordb_result.get_val()}"
    status = factordb_result.get_status()
    print(f"{str(status): <3}", end='\r', file=sys.stderr)
    backoff = 2
    while status in ["U"] and backoff <= 2:
        # if number never seen by factordb, it will return C first time
        # before finding trialdiv, other factors, and primality
        # give it a second and try again, then return that
        time.sleep(backoff)
        backoff *= 2
        response = factordb_result.requery()
        status = factordb_result.get_status()
        print(f"{str(status): <3}", end='\r', file=sys.stderr)
        if not response.ok:
            assert False, f"Response bad after seeing C or U, not sure what happened"
        # if status in ["C"]:
        #     return f"{negative_str}({n})"
    if status in ["C"]:
        return f"{negative_str}({val})"
    if status is None:
        assert False, f"{val} had {status} status (but response was okay), we didn't expect this to happen"
    if status in ["P", "PRP", "Prp", "Unit", "Zero"]:
        return f"{negative_str}{val}"
    if status in ["FF"]:
        factors = factordb_result.get_factor_from_api()
        if factors is None:
            return None
        return negative_str + ".".join(f"{base}{'^'+ str(exponent) if exponent > 1 else ''}" for base, exponent in factors)
    if status in ["CF"]:
        factors = factordb_result.get_factor_from_api()
        if factors is None:
            return None
        terms = []
        for base, exponent in factors:
            term = ""
            if base in lookup_primes or prime.is_prime(base, care_probable=False, check_factor_db=True) > 0:
                term += str(base)
            else:
                term += f"({base})"
            if exponent > 1:
                term += f"^{exponent}"
            terms.append(term)
        return negative_str + ".".join(terms)
    assert False, f"Unknown factordb status: {status} for {val}"


def factor_string_to_factor_list(factor_string):
    terms = factor_string.strip().split(".")
    factor_list = []
    for term in terms:
        if "^" in term:
            base, exponent = term.split("^")
        else:
            base = term
            exponent = 1
        base = int(base.replace("(","").replace(")",""))
        exponent = int(exponent)
        for factor in [base] * exponent:
            factor_list.append(factor)
    return factor_list


def load_backup_factors(sequence_letter, p, q):
    filename = f"sean_lucas/{sequence_letter.lower()}{p}.{q}.dat"
    backup_factors = {}
    for line in pathlib.Path(filename).read_text().strip().split("\n"):
        n, factorstring = line.split(" ")
        backup_factors[int(n)] = factor_string_to_factor_list(factorstring)
    return backup_factors


def check_missing_factors(sequence_func, p, q, n, factordb_result, backup_factors):
    try:
        if factordb_result.get_status() in ["FF", "PRP", "P", "One", "Zero"]:
            return
        val = sequence_func(p, q, n)
        factordb_factors = list(map(int, factordb_result.get_factor_list()))
        missing = list(filter(lambda x: x not in factordb_factors, backup_factors))
        if missing:
            smallest_missing = min(map(gmpy2.num_digits, missing))
            biggest_present = max(map(gmpy2.num_digits, factordb_factors))
            if smallest_missing < biggest_present:
                print(f"Reporting {val}={missing}", file=sys.stderr)
                factordb.report({val: missing})
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)


def check_for_orphan_algebraic_factors(sequence_func, p, q, n, factordb_result):
    try:
        n_factors = factor.factorize(n)
        val = sequence_func(p, q, n)
        cofactors = set()
        for n_factor in n_factors:
            cofactor = abs(sequence_func(p, q, n_factor))
            for dbfactor in factordb_result.get_factor_list():
                if gmpy2.is_divisible(dbfactor, cofactor) and dbfactor // cofactor > 1:
                    cofactors.add(cofactor)
                if gmpy2.is_divisible(cofactor, dbfactor):
                    cofactor = cofactor // dbfactor
                if cofactor == 1:
                    break
        if cofactors:
            print(f"Reporting {val}={list(cofactors)}", file=sys.stderr)
            factordb.report({val: cofactors})
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=f"")
    parser.add_argument("p", type=int)
    parser.add_argument("q", type=int)
    parser.add_argument("action", type=str)
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    valid_p = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    valid_q = [-2, -1, 1, 2]
    valid_actions = ["factor-table", "factor-table-u", "factor-table-v"]
    p = args.p
    q = args.q
    # if p not in valid_p:
    #     parser.exit(1, f"value of p must be in {valid_p}\n")
    # if q not in valid_q:
    #     parser.exit(1, f"value of q must be in {valid_q}\n")



    if args.action not in valid_actions:
        try:
            n = int(args.action)
        except ValueError as e:
            parser.exit(1, f"action must be a positive integer, or one of {valid_actions}\n")
        print(f"U({p},{q},{n}) = {factordb_get_factorizaton_string(u(p, q, n))}")
        print(f"V({p},{q},{n}) = {factordb_get_factorizaton_string(v(p, q, n))}")
    else:
        if args.action in ["factor-table", "factor-table-u"]:
            sequence_func = u
            sequence_letter = "U"
        else:
            sequence_func = v
            sequence_letter = "V"

        #delete me
        backup_factors = load_backup_factors(sequence_letter, p, q)
        # factor_input[n][0] is primes, factor_input[n][1] is composites, factor_input[n][2] is the line
        factor_table_input = {}
        primes_lookup = set()
        lines = []
        # read stdin for the old file for factorization hints, to not repeat work
        n = 0
        try:
            if not sys.stdin.isatty():
                # read all lines in, in case we need to panic print them out on sigterm
                lines = sys.stdin.readlines()
                for line in lines:
                    try:
                        if not line.strip():
                            continue
                        n, right = line.strip().split(' ')
                        n = int(n)
                        primes = []
                        composites = []
                        for match in re.findall(r"(?:(-?\d+)|\((-?\d+)\))(?:\^(\d+))?", right):
                            exponent = int(match[2] or 1)
                            if match[0]:
                                base = int(match[0])
                                primes_lookup.add(base)
                                primes.append([base, exponent])
                            elif match[1]:
                                composites.append([int(match[1]), exponent])
                            else:
                                assert False, "Shouldn't happen, regex must be malformed"
                        val = math.prod(map(lambda divisor: pow(divisor[0], divisor[1]), itertools.chain(primes, composites)))
                        expected_val = sequence_func(p, q, n)
                        if val != expected_val:
                            print(f"The following line did not add up to {sequence_letter}({p},{q},{n}):", file=sys.stderr)
                            print(f"Line: {line}", file=sys.stderr)
                            print(f"Line product: {val}", file=sys.stderr)
                            print(f"Exp product:  {expected_val}", file=sys.stderr)
                            print(f"Skipping line", file=sys.stderr)
                        else:
                            factor_table_input[n] = [primes, composites, line]
                    except Exception as e:
                        print(f"Incorrect formatting for line: {line}", e, file=sys.stderr)
            print(f"Read {len(factor_table_input)} input lines successfully, now batch querying", end='\n', file=sys.stderr)
            # only query n where we don't have data or there is a composite
            n_to_query = list(filter(lambda n: n not in factor_table_input or (n in factor_table_input and len(factor_table_input[n][1]) > 0), range(1, 1001)))
            print(f"{len(n_to_query)} n needing queries", end='\n', file=sys.stderr)
            n_to_val = dict((n, abs(sequence_func(p, q, n))) for n in n_to_query)
            batch_factordb_result_gen = batch_factordb.batch_factordb(list(n_to_val.values()))
            try:
                for n in range(1, 1001):
                    value = sequence_func(p, q, n)
                    # didn't get any hints in the input
                    if n not in factor_table_input:
                        # haven't seen this number, look it up
                        print(f"\x1B[3C{sequence_letter}({p},{q},{n})", end="\r", file=sys.stderr)
                        print(n, factordb_get_factorizaton_string(value,
                                                                  lookup_primes=primes_lookup,
                                                                  factordb_result=next(batch_factordb_result_gen)))
                    else:
                        # no composites, just print it back
                        if len(factor_table_input[n][1]) == 0:
                            print(factor_table_input[n][2].strip())
                        else:
                            print(f"\x1B[3C{sequence_letter}({p},{q},{n})", end="\r", file=sys.stderr)
                            factordb_result = next(batch_factordb_result_gen)

                            # temporarily hijacking this script to report algebraic factors and check backup
                            # delet me
                            # check_missing_factors(sequence_func, p, q, n, factordb_result, backup_factors[n])
                            # check_for_orphan_algebraic_factors(sequence_func, p, q, n, factordb_result)

                            # if number of factors is the same as before
                            # and no composites under 60 digits (these will be auto factored by factordb)
                            # and new query not fully factored
                            # just print old
                            if factordb_result.get_status() not in ["FF"] and \
                                not any(map(lambda composite: gmpy2.num_digits(int(composite[0])) < 60, factor_table_input[n][1])) and \
                                    len(factordb_result.get_factor_list()) \
                                    == len(factor_table_input[n][0]) + len(factor_table_input[n][1]) \
                                    + (1 if factor_table_input[n][2].startswith('-') else 0):
                                print(factor_table_input[n][2].strip())
                            else:
                                print(n, factordb_get_factorizaton_string(
                                    value,
                                    lookup_primes=primes_lookup,
                                    factordb_result=factordb_result))
            except GeneratorExit:
                batch_factordb_result_gen.close()
        except BrokenPipeError:
            # no pipe, just exit
            pass
        except (KeyboardInterrupt, Exception):
            print(traceback.format_exc(), file=sys.stderr)
            # do our best to print out what we know and exit
            if n == 0:
                # hadn't started the main loop, just print stdin back out
                print("\n".join(lines))
            else:
                # interrupted at n, start from there and print what came from stdin.
                for n in range(n, 1001):
                    if n in factor_table_input:
                        print(factor_table_input[n][2].strip())
