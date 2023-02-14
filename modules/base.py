import gmpy2


def digsum(n, base=10):
    if type(n) is not str:
        n = gmpy2.digits(n)
    return sum(gmpy2.mpz(character) for character in n)
