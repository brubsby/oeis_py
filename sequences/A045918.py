import sys

import gmpy2

from sequence import Sequence
import logging


class A045918(Sequence):

    def __init__(self):
        super().__init__(start_index=0)

    def calculate(self, n):
        return self.ls(n)

    def ls(self, n):
        digits = gmpy2.digits(n)
        cur_dig = None
        ret_strs = []
        dig_count = 0
        for digit in digits:
            if cur_dig and cur_dig != digit:
                ret_strs.append(str(dig_count) + cur_dig)
                dig_count = 0
            cur_dig = digit
            dig_count += 1
        ret_strs.append(str(dig_count) + cur_dig)
        return gmpy2.mpz("".join(ret_strs))

    def string_ls(self, nstr):
        digits = nstr
        cur_dig = None
        ret_strs = []
        dig_count = 0
        for digit in digits:
            if cur_dig and cur_dig != digit:
                ret_strs.append(str(dig_count) + cur_dig)
                dig_count = 0
            cur_dig = digit
            dig_count += 1
        ret_strs.append(str(dig_count) + cur_dig)
        return "".join(ret_strs)


sys.modules[__name__] = A045918()