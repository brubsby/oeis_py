import functools
import itertools
import logging
import sys

import gmpy2

import A045918

from sequence import Sequence


class A121994(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[], start_index=0)


    #method to reverse ls sequence
    def calculate(self, n):
        k = self.load_checkpoint(default=1, n=n)
        for k in itertools.count(start=k):
            A121994.ls_inverse_generator(k)


    # mpz only method: 336774/s
    # string only method: 304824/s
    def calculate2(self, n):
        k = self.load_checkpoint(default=1, n=n)
        for k in itertools.count(start=k):
            self.checkpoint(k, k, 10000, n=n)
            last = k
            last_str = gmpy2.digits(k)
            last_num_digits = gmpy2.num_digits(k)  # may be one too big
            fail = False
            for next_val_str in itertools.islice(self.ls_generator(last_str), n):
                if last_num_digits - 1 > len(next_val_str):
                    last_str = next_val_str
                    last = None
                    last_num_digits = len(next_val_str)
                    continue
                next_val = gmpy2.mpz(next_val_str)
                if not last:
                    last = gmpy2.mpz(last_str)
                if next_val >= last:
                    fail = True
                    break
                last = next_val
                last_str = next_val_str
                last_num_digits = len(next_val_str)
            if not fail:
                self.delete_checkpoint(n=n)
                return k

    @staticmethod
    def ls_generator(n):
        val = n
        while True:
            val = A045918.string_ls(val)
            yield val

    @staticmethod
    def ls_inverse_generator(n, to_append="", digit_limit=sys.maxsize):
        n_str = str(n)
        if len(n_str) < 2:
            return
        if len(to_append) + len(n_str) > digit_limit:
            return
        right = n_str[-1]
        if right == "0":
            return
        left_end_index_excl = len(n_str)-1
        for left_start_index in reversed(range(left_end_index_excl)):
            left_str = n_str[left_start_index:left_end_index_excl]
            left_as_int = gmpy2.mpz(left_str)
            if left_as_int + len(to_append) > digit_limit:
                break
            if left_start_index == 0:
                return_string = (left_as_int * right) + to_append
                if len(return_string) <= digit_limit:
                    yield return_string
            else:
                if right != n_str[left_start_index - 1]:
                    yield from A121994.ls_inverse_generator(
                        n_str[:left_start_index],
                        (left_as_int * right) + to_append, digit_limit=digit_limit)

    @staticmethod
    def possible_solutions_of_depth_generator(previous_values, depth, digit_limit=sys.maxsize):
        if type(previous_values) is not list:
            previous_values = [str(previous_values)]
        if depth == 0:
            yield previous_values
            return
        for next in A121994.ls_inverse_generator(previous_values[-1], digit_limit=digit_limit):
            if len(next) <= digit_limit:
                if len(next) > len(previous_values[-1]) or gmpy2.mpz(next) > gmpy2.mpz(previous_values[-1]):
                    yield from A121994.possible_solutions_of_depth_generator(previous_values + [next], depth - 1, digit_limit=digit_limit)


sys.modules[__name__] = A121994()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A121994().enumerate():
        print(f"{n} {val} # {', '.join([str(val) for val in itertools.islice(A121994.ls_generator(str(val)), n+1)])}")
