import itertools
import sys

import gmpy2

def u(p, q, n):
    if p * p == 4 * q:
        s = p//2
        return n * pow(s, n-1)
    return gmpy2.lucasu(p, q, n)


def v(p, q, n):
    if p * p == 4 * q:
        s = p//2
        return 2 * pow(s, n)
    return gmpy2.lucasv(p, q, n)


def tohex(n):
    return hex(n)[2:]


if __name__ == "__main__":

    sys.set_int_max_str_digits(10000)
    inputs = sorted(list(map(lambda x: int(x), sys.stdin.read().strip().split("\n"))))
    inputs_set = set(inputs)
    low_digits = 50 #int(gmpy2.num_digits(inputs[0]))
    high_digits = 200  # int(gmpy2.num_digits(inputs[0]))
    max_a = 5  # min 1
    max_b = 2  # min 0
    max_n = 10000
    add_terms = True
    include_b_zero = True

    print(f"generating generalized lucas numbers for gcd...", file=sys.stderr)
    print(f"pruning terms outside of {low_digits}-{high_digits} digits...", file=sys.stderr)
    print(f"extra terms a*N+b for a=[1,{max_a}] b=[-{max_b}-{max_b}]", file=sys.stderr)

    for line in inputs:
        print(tohex(line))
    if add_terms:
        for p in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
            for q in [-2, -1, 1, 2]:
                if (p, q) in [(2, 1), ]:
                    continue
                for a in range(1, max_a+1):
                    for b in range(-max_b, max_b+1):
                        for n in itertools.count(1):
                            if a != 1 and b == 0:
                                break
                            if b == 0 and not include_b_zero:
                                break
                            miss = 0
                            for func in [u, v]:
                                val = a * abs(func(p, q, n)) + b
                                num_digits = gmpy2.num_digits(val)
                                if low_digits < num_digits:
                                    if num_digits < high_digits:
                                        # if val in inputs:
                                        #     continue
                                        print(tohex(val))
                                    else:
                                        miss += 1
                            if miss >= 2 or n > max_n:
                                break

