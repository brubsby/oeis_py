import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A069678(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)
        self.internal_digit = "3"

    def calculate(self, n):
        strval = str(self(n-1)) if n > 1 else "1"
        while True:
            val, strval = self.internal_repdigit_increment(strval, self.internal_digit)
            if prime.is_prime(val):
                return val

    @staticmethod
    def internal_repdigit_increment(strval, internal_digit):
        if len(strval) == 1 or len(strval) == 2:
            val = int(strval)
            val += 1
            strval = str(val)
            if val == 100:
                strval = "1" + internal_digit + "1"
        else:
            leftstr = strval[0]
            rightstr = ""
            if strval[-1] == "1":
                rightstr = "3"
            elif strval[-1] == "3":
                rightstr = "7"
            elif strval[-1] == "7":
                rightstr = "9"
            elif strval[-1] == "9":
                rightstr = "1"
                leftnum = int(strval[0])
                leftnum += 1
                leftstr = str(leftnum)
                if leftstr == "10":
                    leftstr = "1" + internal_digit
            strval = leftstr + strval[1:-1] + rightstr
            val = int(strval)
        return val, strval




sys.modules[__name__] = A069678()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A069678()
    seq.generate_b_file()
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
