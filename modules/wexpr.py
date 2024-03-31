import re


def convert(wexpr, n=10):
    # (k_m * b^(m * n + o_m) + ... + k_1 * b^(1 * n + o_1) + c) / d
    wexpr = wexpr.strip()
    m = wexpr.count("w")
    if m == 0:
        raise ValueError(f"No w found in wexpr {wexpr}")
    if re.match(r"([^w\d]|ww)", wexpr):
        raise ValueError(f"Invalid wexpr {wexpr}, only (\d+w?)+ matches allowed")
    len_n_1 = len(wexpr.replace("w", ""))
    k = [1] * m
    b = 10
    o = [1] * m
    c = 0
    d = 9
    last_rep = 0
    parts = re.findall(r"(\d+w?)", wexpr)
    for part in parts:
        m -= 1
        num_str = part.replace("w", "")
        num = int(num_str)
        if "w" in part:
            rep = int(part[-2])
            o[m] = len_n_1 - len(num_str) - m
            len_n_1 -= len(num_str)
            section = sum(last_rep * pow(b, i) for i in range(len(part)-1))
            diff_num = num - section
            diff_sign = 1 if diff_num >= 0 else -1
            diff_num = abs(diff_num)
            diff_rep = diff_num % b
            k_abs = diff_num - diff_num // b
            if k_abs % b == 0:
                k_abs -= 1
                c -= 18
            k[m] = diff_sign * k_abs
            c += -1 * diff_sign * ((k_abs % 9) + (9 if diff_rep == 9 else 0))
            last_rep = rep
        else:
            section = sum(last_rep * pow(b, i) for i in range(len(part)))
            c += (num - section) * d
    return *simplify(k, o, b, c, d), \
        (sum(k_m * pow(b, (i+1) * n + o_m) for i, (k_m, o_m) in enumerate(zip(k, o))) + c) // d


def simplify(k1, o1, b1, c1, d1, d_fac=3):
    k = k1[:]
    o = o1[:]
    b = b1
    c = c1
    d = d1
    while d > 1 and all(k_m % d_fac == 0 for k_m in k) and c % d_fac == 0:
        k = [k_m//d_fac for k_m in k]
        c //= d_fac
        d //= d_fac
    while all(k_m % b1 == 0 for k_m in k):
        k = [k_m//b for k_m in k]
    o_w = min(o_m//(i+1) for i, o_m in enumerate(o))
    o = [o_m - o_w * (i+1) for i, o_m in enumerate(o)]
    ns = [f"n{o_m:+d}" if o_m != 0 else f"n" for i, o_m in enumerate(reversed(o))]
    ns = [f"{str(len(o)-i) + '*' if len(o)-i > 1 else ''}{n}" for i, n in enumerate(ns)]
    ns = [f"({n})" if n != "n" else "n" for n in ns]
    terms = [f"{k_m:+d}*{b}^{n}" if abs(k_m) != 1 else f"{'+' if k_m >= 0 else '-'}{b}^{n}" for k_m, n in zip(reversed(k), ns)]
    retstring = "".join(terms)
    if retstring[0] == "+":
        retstring = retstring[1:]
    if c != 0:
        retstring = f"{retstring}{c:+d}"
    if d != 1:
        retstring = f"({retstring})/{d}"
    return retstring, f"n=w{o_w:+d}"


if __name__ == "__main__":
    def test(wexpr, expected):
        converted = convert(wexpr)
        if converted[0] == expected:
            print(f"{wexpr : >20} passed: was {converted[0] : <60}")
        else:
            print(f"{wexpr : >20} failed: was {converted[0] : <60} but expected {expected : <55} : {converted[1]}, {converted[2]}")
    test("9w",               "10^n-1")
    test("9w8",              "10^n-2")
    test("19w",              "2*10^n-1")
    test("1w",               "(10^n-1)/9")
    test("31349w",           "3135*10^n-1")
    test("1239w234",         "124*10^n-766")
    test("13w",              "(4*10^n-1)/3")
    test("23w",              "(7*10^n-1)/3")
    test("51w",              "(46*10^n-1)/9")
    test("52w",              "(47*10^n-2)/9")
    test("53w",              "(16*10^n-1)/3")
    test("54w",              "(49*10^n-4)/9")
    test("56w",              "(17*10^n-2)/3")
    test("58w",              "(53*10^n-8)/9")
    test("68w",              "(62*10^n-8)/9")
    test("87w",              "(79*10^n-7)/9")
    test("101w",             "(91*10^n-1)/9")
    test("98w",              "(89*10^n-8)/9")
    test("13w7",             "(4*10^n+11)/3")
    test("9w0w",             "10^(2*n)-10^n")
    test("31345w",           "(28211*10^n-5)/9")
    test("1234w1234",        "(1111*10^n-28894)/9")
    test("9w8w",             "(9*10^(2*n)-10^n-8)/9")
    test("9w1w",             "(9*10^(2*n)-8*10^n-1)/9")
    test("1w2w3",            "(10^(2*n+1)+10^(n+1)+7)/9")
    test("9w87w",            "(9*10^(2*n+1)-11*10^n-7)/9")
    test("9w8w9",            "(9*10^(2*n+1)-10^(n+1)+1)/9")
    test("3w2334w",          "(3*10^(2*n+3)-899*10^n-4)/9")
    test("4w34445w",         "(4*10^(2*n+4)-8999*10^n-5)/9")
    test("123w234w",         "(111*10^(2*n+2)-89*10^n-4)/9")
    test("9w8378w9",         "(9*10^(2*n+2)-1459*10^n+1)/9")
    test("9w8378w",          "(9*10^(2*n+3)-1459*10^n-8)/9")
    test("123w4w56",         "(111*10^(2*n)+10^(n+1)+104)/9")
    test("9w8w9w",           "(9*10^(3*n)-10^(2*n)+10^n-9)/9")
    test("9w1212121w",       "(9*10^(2*n+6)-7909091*10^n-1)/9")
    test("9w1w2w",           "(9*10^(3*n)-8*10^(2*n)+10^n-2)/9")
    test("9w1w9w",           "(9*10^(3*n)-8*10^(2*n)+8*10^n-9)/9")
    test("9w837w8w",         "(9*10^(3*n+2)-146*10^(2*n)+10^n-8)/9")
    test("1w2w3w4",          "(10^(3*n+1)+10^(2*n+1)+10^(n+1)+6)/9")
    test("123w45w6w",        "(111*10^(3*n+1)+11*10^(2*n)+10^n-6)/9")
    test("9w8378w9w",        "(9*10^(3*n+3)-1459*10^(2*n)+10^n-9)/9")
    test("9w8378w7w",        "(9*10^(3*n+3)-1459*10^(2*n)-10^n-7)/9")
    test("7w837w9w",         "(7*10^(3*n+2)+54*10^(2*n)+2*10^n-9)/9")
    test("1w23w456w",        "(10^(3*n+3)+11*10^(2*n+2)+111*10^n-6)/9")
    test("978w789w987w",     "(881*10^(3*n+4)-89*10^(2*n+2)-11*10^n-7)/9")
    test("123w234w345w456",  "(111*10^(3*n+1)-89*10^(2*n+1)-89*10^(n+1)-896)/9")
    test("9w8w7w8w9w",       "(9*10^(5*n)-10^(4*n)-10^(3*n)+10^(2*n)+10^n-9)/9")
    test("789w789w789w789w", "79*10^(4*n+6)-21*10^(3*n+4)-21*10^(2*n+2)-21*10^n-1")
    test("7w837w9w8w9w",     "(7*10^(5*n+2)+54*10^(4*n)+2*10^(3*n)-10^(2*n)+10^n-9)/9")
    test("987w987w987w987w", "(889*10^(4*n+6)+189*10^(3*n+4)+189*10^(2*n+2)+189*10^n-7)/9")