import itertools
import sys
import logging

import gmpy2
import numpy as np

from oeispy.core import Sequence


class A006577(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)
        self.cache_limit = 2**32
        self._lookup_table = np.zeros(self.cache_limit, np.uint16)

    def calculate(self, n):
        return self.calculate_with_stopping(n)

    def calculate_with_stopping(self, n, stop_after_count=None):
        if n <= 1:
            return 0
        if n < self._lookup_table.size and self._lookup_table[n]:
            return self._lookup_table[n]
        val = n
        count = 0
        to_cache = []
        while val != 1:
            if gmpy2.is_even(val):
                next_val = val // 2
            else:
                next_val = 3 * val + 1
            if next_val < self._lookup_table.size:
                lookup_val = self._lookup_table[next_val]
                if lookup_val or next_val == 1:
                    for n_count, n_cache in enumerate(reversed(to_cache)):
                        if n_cache < self._lookup_table.size:
                            self._lookup_table[n_cache] = n_count + lookup_val + 1
                    return lookup_val + count + 1
            count += 1
            to_cache.append(next_val)
            val = next_val
            if count > stop_after_count:
                return -1
        for n_count, n_cache in enumerate(reversed(to_cache)):
            if n_cache < self._lookup_table.size:
                self._lookup_table[n_cache] = n_count + lookup_val + 1
        return count


sys.modules[__name__] = A006577()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A006577().enumerate():
        print(f"{n} {val}")
