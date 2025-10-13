import itertools
import logging
import sys
import num2words

from modules import factor, base, prime, semiprime
from sequence import Sequence


class A005224(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=1, iterative_lookup=True)
        self.sentence = "tisthe"
        self.index = 1


    def calculate(self, n):
        i = self.sentence.index("t")
        val = i + self.index
        self.sentence = self.sentence[i+1:] + num2words.num2words(val, ordinal=True).replace(" and","").replace(" ", "").replace("-", "").replace(",","")
        # print(f"{self.index}: {self.sentence}")
        self.index += i+1
        return val



sys.modules[__name__] = A005224()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seq = A005224()
    # seq.generate_b_file(term_cpu_time=30)
    # for n, val in seq.enumerate(alert_time=60, quit_on_alert=True):
    #     print(f"{n} {val}")
    #     if n > 100:
    #         break
    print(seq(10000))