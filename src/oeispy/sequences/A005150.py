import sys

import gmpy2

from oeispy.sequences import A045918
from oeispy.core import Sequence


class A005150(Sequence):

    def calculate(self, n):
        if n == 1:
            return "1"
        return A045918.string_ls(self(n-1))


sys.modules[__name__] = A005150()


if __name__ == "__main__":
    seq = A005150()
    print(seq(18))