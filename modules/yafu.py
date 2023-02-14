import itertools
import logging
import os
import shutil
import subprocess
import time
import uuid
import tempfile

import gmpy2


def factor(expr, stop_after_one=False, threads=1, work=None):
    logging.debug(f"Running yafu for: {expr}")
    str_expr = f"factor({str(expr)})"
    start_time = time.time()
    this_uuid = uuid.uuid4()
    yafu_dir = "C:/Users/Tyler/Downloads/yafu-2.9/"
    dirpath = os.path.join("..", "data", "temp", str(this_uuid))
    filename = f"temp-{this_uuid}.dat"
    temp_filepath = os.path.join(dirpath, filename)
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
            popen_arglist.append(threads)
        if work:
            popen_arglist.append("-work")
            popen_arglist.append(work)

        proc = subprocess.Popen(popen_arglist,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE,
                                universal_newlines=True, cwd=dirpath)
        print(str_expr, file=proc.stdin, flush=True)
        proc.stdin.close()
        for i, line in enumerate(proc.stdout):
            logging.debug(line[:-1])
        proc.wait()
        with open(os.path.join(dirpath, factors_filename), "r") as factors_file:
            lines = factors_file.readlines()
            assert len(lines) == 1, "Should only be one line in factor output file per yafu invocation"
            factors = lines[0].split("/")  # [2, 3^5, ...]
            factors = [term.split("^") for term in factors]  # [[2], [3, 5], ...]
            factors = [term if len(term) == 1 else [term[0]] * int(term[1]) for term in factors]  # [[2], [3, 3, 3, 3, 3], ...]
            factors = list(itertools.chain.from_iterable(factors))
            elapsed = time.time() - start_time
            logging.debug(f"yafu factored {expr} in {elapsed:.02f} seconds")
            return [gmpy2.mpz(factor) for factor in factors[1:]]
    finally:
        # cleanup temp dir
        shutil.rmtree(dirpath, ignore_errors=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print(factor("fib(1000)"))
