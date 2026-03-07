import itertools
import sys
import logging

import gmpy2
import requests
from lxml import html

from oeispy.core import Sequence
import A006577
import A006878
import A006877


class A033491(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0, b_file_lookup=True)

    def calculate(self, n):
        start_val = 0
        # smartly choose starting point off what we know about the records
        for i in itertools.count(start=1):
            if A006878.lookup(i) is not None and A006877.lookup(i) is not None:
                start_val = A006877.lookup(i)
            else:
                break
            if A006878.lookup(i+1) is not None and A006878.lookup(i+1) > n:
                break
        for k in itertools.count(start=start_val):
            val = A006577.calculate_with_stopping(k, stop_after_count=n)
            if val == -1:
                continue
            if k % 1000000 == 0:
                logging.debug(f"A006577({k})={val}")
            if val == n:
                return k

    def generate_b_file_from_webscraping(self):
        records = html.fromstring(requests.get("http://www.ericr.nl/wondrous/classrec.html").content).xpath(
            ".//td")
        values = [1]
        for record in records:
            stripped = record.text_content().replace(",", "").strip()
            if not stripped:
                break
            values.append(int(stripped))
        for n, value in enumerate(values):
            self.cache_value(n, value)
        self.generate_b_file(max_n=len(values), term_cpu_time=5)


sys.modules[__name__] = A033491()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # A033491().generate_b_file_from_webscraping()
    for n, val in A033491().enumerate(alert_time=10, quit_on_alert=True):
        print(f"{n} {val}")
