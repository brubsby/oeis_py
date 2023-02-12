import itertools
import sys
import gmpy2

from sequence import Sequence
import modules.primetest as primetest

class A254002(Sequence):

    def __init__(self):
        super().__init__(start_index=1,
                         lookup_list=[1, 3, 4, 6, 9, 45, 57, 130, 142, 198, 273, 331, 2494, 8437, 10210, 17377, 19972])

    def calculate(self, n):
        k = self.load_checkpoint(default=self(n-1)+1, n=n)
        term = pow(gmpy2.mpz(100), k)
        for k in itertools.count(start=k):
            val = 46*(term-1)//99+1
            self.checkpoint(k, n=n)
            trial_div_result = primetest.trial_div_prime_test(val)
            if trial_div_result == 2:
                self.delete_checkpoint(n)
                return n
            elif trial_div_result == -1:
                if primetest.prp_test_pfgw(f"46*(100^{k}-1)/99+1"):
                    self.delete_checkpoint(n)
                    return n
            term *= 100


sys.modules[__name__] = A254002()

if __name__ == "__main__":
    for n, val in enumerate(A254002().generate()):
        print(f"{n} {val}")


