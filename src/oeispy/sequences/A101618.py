import itertools
import logging
import sys
import oeispy.utils.semiprime as semiprime

from oeispy.core import Sequence
import A001003


class A101618(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[],
                         start_index=1)

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1 if n > 1 else 0, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, n=n, cooldown=5)
            semi_test_result = semiprime.is_semi(A001003(k), num_retries=2, sleep_time=2)
            if semi_test_result == -1:
                # print(f"yafu time: http://factordb.com/index.php?query={A001003(k)}")
                # exit(1)
                # print probables
                self.delete_checkpoint(n=n)
                return k
            if semi_test_result in [1, 2]:
                self.delete_checkpoint(n=n)
                return k


sys.modules[__name__] = A101618()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A101618().enumerate():
        print(f'{n} {val} # {f"http://factordb.com/index.php?query={A001003(val)}"}')
