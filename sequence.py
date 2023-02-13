import itertools
import logging
import os
import sys
import time
import notifypy

from func_timeout import func_timeout, FunctionTimedOut
import modules.checkpoint as checkpoint


class Sequence:

    def __init__(self, start_index=1, lookup_list=None, iterative_lookup=False, b_file_lookup=False, caching=True):
        self._lookup = {}
        if lookup_list:
            for n, item in enumerate(lookup_list, start=start_index):
                if item is not None:
                    self._lookup[n] = item
        self.start_index = start_index
        self._caching = caching
        self._iterative_lookup = iterative_lookup
        if b_file_lookup:
            self.cache_b_file_values()

    def lookup(self, n):
        return self._lookup.get(n)

    def cache_value(self, n, value):
        if n not in self._lookup:
            self._lookup[n] = value
        else:
            assert value == self._lookup.get(n), f"value mismatch when attempting to cache {n}, (new value) {value} != {self._lookup.get(n)} (existing value)"

    def first_unknown(self):
        for n in itertools.count(start=self.start_index):
            if n not in self._lookup:
                return n

    def __call__(self, n, no_lookup=False):
        if not no_lookup:
            if self._lookup.get(n) is not None:
                return self._lookup.get(n)
            # sequence refers to it past 1 term mostly
            # go ahead and calc them all up to n-1 iteratively to avoid terrible python recursion
            if self._iterative_lookup:
                biggest_lookup_n = sorted(self._lookup.keys())[-1] if len(self._lookup) > 0 else self.start_index
                for m in range(biggest_lookup_n + 1, n):
                    self.calculate(m)
        calculated_value = self.calculate(n)
        # cache calculated values
        if self._caching:
            self._lookup[n] = calculated_value
        return calculated_value

    def calculate(self, n):
        raise NotImplementedError

    def list(self, n, no_lookup=False):
        return [self(i, no_lookup) for i in range(self.start_index, n + 1)]

    def generate(self, no_lookup=False, alert_time=None, quit_on_alert=False):
        last = time.time() - 0.01
        for n in itertools.count(start=self.start_index):
            value = self(n, no_lookup)
            yield value
            checkpoint.timing_reset()
            if alert_time:
                now = time.time()
                if now - last > alert_time:
                    noti = notifypy.Notify()
                    noti.title = f"New term found in {self.__class__.__name__}!"
                    noti.message = f"{self.__class__.__name__}(n) = {value}"
                    noti.send()
                    if quit_on_alert:
                        print(f"Exiting as value was found after calculating for {int(now - last)} seconds!")
                        sys.exit(0)
                last = now

    def enumerate(self, no_lookup=False, alert_time=None, quit_on_alert=False):
        for n, value in enumerate(self.generate(no_lookup=no_lookup, alert_time=alert_time, quit_on_alert=quit_on_alert),
                                  start=self.start_index):
            yield n, value

    def enumerate_with_timeout(self, start=None, timeout=5, no_lookup=False):
        for n, value in enumerate(self.generate_with_timeout(start=start, no_lookup=no_lookup),
                                  start=self.start_index):
            yield n, value

    def generate_with_timeout(self, start=None, timeout=5, no_lookup=False):
        if start is None:
            start = self.start_index
        term_getter = self.calculate if no_lookup else self.__call__
        for n in itertools.count(start=start):
            try:
                yield func_timeout(timeout, term_getter, [n])
            except FunctionTimedOut:
                yield -1

    def get_b_filename(self, letter_file="b"):
        return os.path.join("..", "data", "b-files", self.__class__.__name__.replace("A", letter_file) + ".txt")

    def generate_b_file(self, no_lookup=False, max_n=10000, comment=None, term_digit_length_limit=1000, term_cpu_time=None):
        with open(self.get_b_filename(), "w") as bfile:
            bfile_comment_header = f"# {self.__class__.__name__}\n"
            if comment:
                if type(comment) is str:
                    comment = "\n".join([f"#{split_comment}" for split_comment in comment.split("\n")])
                else:
                    comment = f"#{str(comment)}"
                bfile_comment_header += f"#" \
                                        f"{comment}" \
                                        f"#" \
                                        f""
            bfile.write(bfile_comment_header)
            enumerator = self.enumerate(no_lookup=no_lookup) if term_cpu_time is None else self.enumerate_with_timeout(timeout=term_cpu_time)
            for n, val in enumerator:
                strval = str(val)
                strval_len = len(strval)
                if strval_len > term_digit_length_limit:
                    bfile.write(f"# a({n}) is {strval_len} digits (larger than the {term_digit_length_limit} digit soft limit)\n")
                    break
                if val == -1 and term_cpu_time:
                    break
                bfile.write(f"{n} {strval}\n")
                if n+1 > max_n:
                    break

    def cache_b_file_values(self):
        if not os.path.exists(self.get_b_filename()):
            logging.warning(f"{self.get_b_filename()} not found, even though b_file caching was requested for {self.__class__.__name__}, continuing...")
            return
        with open(self.get_b_filename(), "r") as bfile:
            for line in bfile.readlines():
                if line.startswith("#"):
                    continue
                line = line.split("#")[0].strip()
                if line:
                    parts = line.split(" ")
                    assert len(parts) == 2, "Too many terms in a single b file line"
                    n = int(parts[0])
                    value = int(parts[1])
                    self.cache_value(n, value)

    def get_dat_filename(self, n=None):
        return self.__class__.__name__ + f"{'' if not n else f'_{n}'}.dat"

    def checkpoint(self, vals, counter=None, iterations=1, n=None, total=True, log=True, cooldown=5):
        if not counter:
            counter = 1  # print and save timing info every call to checkpoint if no counter
        if log:
            checkpoint.timing(vals, counter, iterations=iterations, total=total, filename=self.get_dat_filename(n), cooldown=cooldown)
        else:
            checkpoint.save(vals, filename=self.get_dat_filename(n))

    def load_checkpoint(self, default=None, n=None):
        if n < 0:
            return default
        return checkpoint.load(filename=self.get_dat_filename(n), default=default)

    def delete_checkpoint(self, n=None):
        checkpoint.delete(filename=self.get_dat_filename(n))


