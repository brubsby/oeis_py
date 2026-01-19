import functools
import itertools
import logging
import os
import shutil
import subprocess
import sys
import time
import uuid
import requests
import random
import urllib
from func_timeout import func_timeout, FunctionTimedOut
from oeispy.utils import config

import gmpy2

from oeispy.utils import factor

__COOKIE__ = config.get_factordb_cookie()

def local_factor(composites, threads=1, work=None, pretest=None, one=None, timeout=None):
    if not timeout:
        return factor_implementation(composites, threads=threads, work=work, pretest=pretest, one=one)
    return func_timeout(timeout, factor_implementation, [composites],
                        kwargs={"threads": threads, "work": work, "one": one, "pretest": pretest})


def factor_implementation(composites, threads=1, work=None, pretest=None, one=None):
    expr = "".join([f"factor({composite})\n" for composite in composites])
    logging.info(f"Running yafu for {len(composites)} composites")
    # [logging.info(f"{len(composite) if type(composite) == str else gmpy2.num_digits(composite)}-digit composite: {composite}") for composite in composites]
    start_time = time.time()
    this_uuid = uuid.uuid4()
    yafu_dir = "C:/Software/yafu-master/"
    dirpath = os.path.join("temp", str(this_uuid))
    filename = f"temp-{this_uuid}.dat"
    temp_filepath = os.path.join(dirpath, filename)
    proc = None
    try:
        os.makedirs(dirpath, exist_ok=True)
        # copy the yafu.ini so we can use it from the throwaway temp dir without polluting the yafu directory with
        # logs and restart points
        shutil.copy(os.path.join(yafu_dir, "yafu.ini"), os.path.join(dirpath, "yafu.ini"))
        with open(temp_filepath, "w") as temp:
            temp.write(f"{expr}\n")
        factors_filename = "factors.out"
        popen_arglist = [
            os.path.join(yafu_dir, "yafu-x64-gc.exe"), "-of", factors_filename, "-no_expr",
        ]
        if threads != 1:
            popen_arglist.append("-threads")
            popen_arglist.append(str(threads))
        if work:
            popen_arglist.append("-work")
            popen_arglist.append(str(work))
        if pretest:
            popen_arglist.append("-pretest")
            popen_arglist.append(str(pretest))
        if one:
            popen_arglist.append("-one")

        proc = subprocess.Popen(popen_arglist,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE,
                                universal_newlines=True, cwd=dirpath, bufsize=1)
        print(expr, file=proc.stdin, flush=True)
        proc.stdin.close()
        for i, line in enumerate(proc.stdout):
            logging.debug(line[:-1])
        proc.wait()
    finally:
        if proc:
            proc.kill()
        # send factors even if killed early
        to_report = []
        factors = []
        with open(os.path.join(dirpath, factors_filename), "r") as factors_file:
            for line in factors_file.readlines():
                factors = line.split("/")  # [2, 3^5, ...]
                factors = [term.split("^") for term in factors]  # [[2], [3, 5], ...]
                factors = [[gmpy2.mpz(term[0])] if len(term) == 1 else [gmpy2.mpz(term[0])] * int(term[1]) for term in factors]  # [[2], [3, 3, 3, 3, 3], ...]
                factors = list(itertools.chain.from_iterable(factors))
                to_report.append((factors[0], factors[1:]))
            elapsed = time.time() - start_time
            report(to_report)
            logging.debug(f"yafu ran {expr} in {elapsed:.02f} seconds")
        # cleanup temp dir
        shutil.rmtree(dirpath, ignore_errors=True)


def report(composite_factors_tuples, sleep=1):
    payload = "\n".join(["{}={}".format(composite, str([int(factor) for factor in factors])) for composite, factors in composite_factors_tuples])
    logging.info(f"submitting factors:\n{payload}")
    payload = 'report=' + urllib.parse.quote(payload, safe='') + '&format=0'
    temp2 = requests.get('http://factordb.com/report.php?'+payload, cookies={"fdbuser": __COOKIE__})
    try:
        temp2.raise_for_status()
    except Exception as e:
        logging.exception(e)
        time.sleep(sleep)
        report(composite_factors_tuples, sleep=sleep*2)


def get_composites_from_factordb(minimum_digits=1, num_composites=100, start_number=0, sleep=1):
    request = requests.get(f"http://factordb.com/listtype.php?t=3&mindig={minimum_digits}&perpage={num_composites}&start={start_number}&download=1", cookies={"fdbuser": __COOKIE__})
    try:
        request.raise_for_status()
        return request.text.strip().split('\n')
    except Exception as e:
        time.sleep(sleep)
        return get_composites_from_factordb(minimum_digits=minimum_digits, num_composites=num_composites, start_number=start_number, sleep=sleep*2)


def get_composites_from_stdin():
    return list(map(int, sys.stdin.readlines())) if not sys.stdin.isatty() else []


def get_hardcoded_composites():
    return [

    ]


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    # clear temp files when starting
    shutil.rmtree(os.path.join("temp"), ignore_errors=True)

    composites = []#get_composites_from_stdin()
    if not composites:
        composites = get_hardcoded_composites()
    get_from_factordb = not composites
    get_num = 1

    while True:
        if get_from_factordb and not composites:
            composites = get_composites_from_factordb(0, get_num, random.randint(0, 200))
            # batch more if the number is smaller
            get_num = max((80 - gmpy2.num_digits(int(composites[-1]))) * 2, 1)
        try:
            start = time.time()
            local_factor(composites, threads=12, work=0, one=True)
        except (FileNotFoundError, UnicodeDecodeError, FunctionTimedOut, urllib.error.HTTPError, requests.exceptions.ConnectionError) as e:
            logging.error(e)
        composites = []

