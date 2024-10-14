import itertools
import logging
import sys
import modules.prime as prime

from sequence import Sequence


# Champernowne primes
class A176942(Sequence):

    def __init__(self):
        super().__init__(start_index=1, lookup_list=[10, 14, 24, 235, 2804, 4347, 37735])

    # k is decimal digit length of candidate (A071620)
    def calculate(self, n):
        k = self.load_checkpoint(default=1 if n <= 1 else self(n-1)+1, n=n)
        concat_str, i = self.get_champernowne_string_of_length(k)
        for k in itertools.count(start=k):
            if len(concat_str) >= k:
                concat_str += str(i)
                i += 1
            if prime.is_prime(concat_str[:k]):
                self.delete_checkpoint(n=n)
                return k
            self.checkpoint(k, k, n=n, total=False)

    # rather than generating the string based off last full number added
    # generate the first full string that is greater than given length k
    # return string and next i to add to champernowne string
    # tested by timeit to be a lot faster than concatenating strings as you go
    @staticmethod
    def get_champernowne_string_of_length(k):
        concat_list = []
        length = 0
        for i in itertools.count(start=1):
            next = str(i)
            concat_list.append(next)
            length += len(next)
            if length >= k:
                return "".join(concat_list), i + 1


sys.modules[__name__] = A176942()

if __name__ == "__main__":
    # len_996, i = A176942.get_champernowne_string_of_length(997)
    # print(len_996)
    # print(len_996[:996])
    logging.basicConfig(level=logging.INFO)
    for n, val in A176942().enumerate(alert_time=10, quit_on_alert=True):
        print(f"{n} {val}")
