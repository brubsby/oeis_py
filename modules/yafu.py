import functools
import itertools
import logging
import os
import shutil
import subprocess
import time
import uuid
import tempfile
from modules import factordb

import gmpy2

logger = logging.getLogger("yafu")


def factor(expr, stop_after_one=False, report_to_factordb=True, threads=1, work=None, pretest=None):
    str_expression = str(expr)
    text = f"{len(str_expression)} char expression: {str_expression[:48] + '...' + str_expression[-48:]}" if len(
        str_expression) > 100 else expr
    header_log_message_parts = ["Running yafu"]
    if work:
        header_log_message_parts.append(f"from t{work}")
    if pretest:
        header_log_message_parts.append(f"to t{pretest}")
    if stop_after_one:
        header_log_message_parts.append("and stopping after one factor")
    header_log_message_parts.append(f"for {text}")
    logger.info(" ".join(header_log_message_parts))
    str_expr = f"factor({str(expr)})"
    start_time = time.time()
    this_uuid = uuid.uuid4()
    yafu_dir = "C:/Users/Tyler/Downloads/yafu-2.9/"
    dirpath = os.path.join("..", "data", "temp", str(this_uuid))
    filename = f"temp-{this_uuid}.dat"
    temp_filepath = os.path.join(dirpath, filename)
    proc = None
    try:
        os.makedirs(dirpath, exist_ok=True)
        # symlink the yafu.ini so we can use it from the throwaway temp dir without polluting the yafu directory with
        # logs and restart points
        shutil.copy(os.path.join(yafu_dir, "yafu.ini"), os.path.join(dirpath, "yafu.ini"))
        with open(temp_filepath, "w") as temp:
            temp.write(f"{str_expr}\n")
        factors_filename = "factors.out"
        popen_arglist = [
            os.path.join(yafu_dir, "yafu-x64.exe"), "-of", factors_filename,
        ]
        if stop_after_one:
            popen_arglist.append("-one")
        if threads != 1:
            popen_arglist.append("-threads")
            popen_arglist.append(str(threads))
        if work:
            popen_arglist.append("-work")
            popen_arglist.append(str(work))
        if pretest:
            popen_arglist.append("-pretest")
            popen_arglist.append(str(pretest))
        proc = subprocess.Popen(popen_arglist,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE,
                                universal_newlines=True, cwd=dirpath, bufsize=1)
        print(str_expr, file=proc.stdin, flush=True)
        proc.stdin.close()
        for i, line in enumerate(proc.stdout):
            logger.debug(line[:-1])
        proc.wait()
        try:
            with open(os.path.join(dirpath, factors_filename), "r") as factors_file:
                lines = factors_file.readlines()
                assert len(lines) == 1, "Should only be one line in factor output file per yafu invocation"
                factors = lines[0].split("/")  # [2, 3^5, ...]
                factors = [term.split("^") for term in factors]  # [[2], [3, 5], ...]
                factors = [[gmpy2.mpz(term[0])] if len(term) == 1 else [gmpy2.mpz(term[0])] * int(term[1]) for term in factors[1:]]  # [[2], [3, 3, 3, 3, 3], ...]
                factors = list(itertools.chain.from_iterable(factors))

                # inputs for which yafu might not completely factor a number
                if stop_after_one or pretest:
                    # yafu doesn't give the remaining cofactor so we have to calculate it
                    # (worry about evaluating math expressions later)
                    assert type(expr) in [int, gmpy2.mpz]
                    factors.append(functools.reduce(lambda comp, div: comp // div, factors, expr))
                elapsed = time.time() - start_time
                # if elapsed > 10:  # report factors to factordb if it took more than 10 seconds in yafu
                # always report factors if yafu was called and found a factor
                if report_to_factordb and len(factors) > 1:
                    logger.info(f"yafu found factors: {factors}")
                    factordb.report(expr, factors)
                    logger.info(f"yafu reported factors for expression: {expr}")
                logger.info(f"yafu ran on {expr} for {elapsed:.02f} seconds")
                return [gmpy2.mpz(factor) for factor in factors]
        except FileNotFoundError as e:
            time_elapsed = time.time() - start_time
            if pretest:
                # likely no factors found due to pretesting not finding any
                # if it took less than 3 seconds it was probably a real error we should not continue from
                # perhaps from msieve
                if pretest > 30 and time_elapsed < 3:
                    raise e
                logger.info(f"yafu found no factors during pretest on: {expr}")
                return [expr]
    except Exception as e:
        logger.error(e)
        raise e
    finally:
        if proc:
            proc.kill()
        # cleanup temp dir
        shutil.rmtree(dirpath, ignore_errors=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print(factor("fib(1000)"))
