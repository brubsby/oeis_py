import timeit

import gmpy2


def digsum(n):
    if type(n) is not str:
        n = gmpy2.digits(n)
    return sum(gmpy2.mpz(character) for character in n)


def digrev(n):
    if type(n) == str:
        return n[::-1]
    if type(n) == gmpy2.mpz:
        return gmpy2.mpz(gmpy2.digits(n)[::-1])
    return int(str(n)[::-1])


def concat(nlist, inbase=10, outbase=10):
    return gmpy2.mpz(''.join(gmpy2.mpz(n).digits(inbase) for n in nlist), base=outbase)


if __name__ == "__main__":
    print(concat([123, gmpy2.mpz(123), "123"]))
    print(concat([1, 10], 2, 10))
    print(timeit.timeit("num.digits()[::-1]", "import gmpy2; num = gmpy2.mpz(12345678901234567890123456789012345678901234567890)"))
    print(timeit.timeit("str(num)[::-1]", "import gmpy2; num = gmpy2.mpz(12345678901234567890123456789012345678901234567890)"))