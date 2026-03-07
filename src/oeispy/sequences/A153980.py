import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A153980(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[259146, 2185871, 2191530, 20317438, 22608949, 30512946, 33685085, 46400839, 81780856, 202677438, 302561193, 694999138, 711286401, 788309388, 1006626821, 1105599276], start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 1, n=n)
        for k in itertools.count(start=k):
            fail, s, ds, ss = False, str(k), set(), 0
            for d in range(1, len(s)):
                for c in itertools.combinations(s, d):
                    t = int("".join(c))
                    if t not in ds:
                        ds.add(t)
                        ss += t
                        if ss > k:
                            fail = True
                            break
                if fail:
                    break
            if ss == k:
                return k
            self.checkpoint(k, k, 100, n=n)


sys.modules[__name__] = A153980()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A153980()
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
