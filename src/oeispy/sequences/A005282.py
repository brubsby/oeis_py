import itertools
import logging
import sys

from oeispy.utils import factor, base, prime, semiprime
from oeispy.core import Sequence


class A005282(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1)

    def generator(self, start):
        yield from self.mian_chowla_generator(1, 2)

    @staticmethod
    def mian_chowla_generator(a1, a2):
            values = [a1]
            increases = set()
            differences = set()
            k = a2
            yield values[0]
            for k in itertools.count(k):
                fail = False
                increase = k - values[-1]
                if increase in increases:
                    continue
                next_differences = set()
                for val in values:
                    difference = k - val
                    if difference in differences:
                        fail = True
                        break
                    next_differences.add(difference)
                if fail:
                    continue
                increases.add(increase)
                differences.update(next_differences)
                values.append(k)
                yield k


sys.modules[__name__] = A005282()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A005282()
    print(seq.generate_data_section())
    # seq.generate_b_file(term_cpu_time=30)
    for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
        print(f"{n} {val}")
