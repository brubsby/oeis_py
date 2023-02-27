import importlib
import re

import gmpy2
import sympy
import primesieve

# fourFn.py
#
# Demonstration of the pyparsing module, implementing a simple 4-function expression parser,
# with support for scientific notation, and symbols for e and pi.
# Extended to add exponentiation and simple built-in functions.
# Extended test cases, simplified pushFirst method.
# Removed unnecessary expr.suppress() call (thanks Nathaniel Peterson!), and added Group
# Changed fnumber to use a Regex, which is now the preferred method
# Reformatted to latest pypyparsing features, support multiple and variable args to functions
#
# Copyright 2003-2019 by Paul McGuire
#
from pyparsing import (
    Literal,
    Word,
    Group,
    Forward,
    alphas,
    alphanums,
    Regex,
    ParseException,
    CaselessKeyword,
    Suppress,
    delimitedList,
    Combine,
    Optional
)
import math
import operator

from sequences import A000058
from sequences import A000073
from sequences import A110396
from sequences import A007908

_exprStack = []


def _push_first(toks):
    _exprStack.append(toks[0])


def _push_unary(toks):
    for t in toks:
        if t == "-":
            _exprStack.append("unary -")
        else:
            break


_bnf = None


def _BNF():
    """
    expop   :: '^'
    multop  :: '*' | '/'
    addop   :: '+' | '-'
    integer :: ['+' | '-'] '0'..'9'+
    atom    :: PI | E | real | fn '(' expr ')' | '(' expr ')'
    factor  :: atom [ expop factor ]*
    term    :: factor [ multop factor ]*
    expr    :: term [ addop term ]*
    """
    global _bnf
    if not _bnf:
        # use CaselessKeyword for e and pi, to avoid accidentally matching
        # functions that start with 'e' or 'pi' (such as 'exp'); Keyword
        # and CaselessKeyword only match whole words
        e = CaselessKeyword("E")
        pi = CaselessKeyword("PI")
        # fnumber = Combine(Word("+-"+nums, nums) +
        #                    Optional("." + Optional(Word(nums))) +
        #                    Optional(e + Word("+-"+nums, nums)))
        # or use provided pyparsing_common.number, but convert back to str:
        # fnumber = ppc.number().addParseAction(lambda t: str(t[0]))
        fnumber = Regex(r"[+-]?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?")
        ident = Word(alphas, alphanums + "_$")

        plus, minus, mult, div = map(Literal, "+-*/")
        lpar, rpar = map(Suppress, "()")
        lbrace, rbrace = map(Suppress, "{}")
        lbrack, rbrack = map(Suppress, "[]")
        addop = plus | minus
        multop = mult | div
        expop = Literal("^")
        fac, prim = map(Literal, "!#")
        unop = fac | prim

        expr = Forward()
        expr_list = delimitedList(Group(expr))
        # add parse action that replaces the function identifier with a (name, number of args) tuple
        def insert_fn_argcount_tuple(t):
            fn = t.pop(0)
            num_args = len(t[0])
            t.insert(0, (fn, num_args))

        fn_call = (ident + lpar - Group(expr_list) + rpar).setParseAction(
            insert_fn_argcount_tuple
        )
        atom = (
            addop[...]
            + (
                (fn_call | pi | e | fnumber | ident).setParseAction(_push_first)
                | Group(lpar + expr + rpar)
            ) + unop.setParseAction(_push_first)[...]
        ).setParseAction(_push_unary)

        # by defining exponentiation as "atom [ ^ factor ]..." instead of "atom [ ^ atom ]...", we get right-to-left
        # exponents, instead of left-to-right that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = Forward()
        factor <<= atom + (expop + factor).setParseAction(_push_first)[...]
        term = factor + (multop + factor).setParseAction(_push_first)[...]
        expr <<= term + (addop + term).setParseAction(_push_first)[...]
        _bnf = expr
    return _bnf


# map operator symbols to corresponding arithmetic operations
_epsilon = 1e-12
_opn = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.floordiv,
    "^": operator.pow,
}

_fn = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "exp": math.exp,
    "abs": abs,
    "trunc": int,
    "round": round,
    "sgn": lambda a: -1 if a < -_epsilon else 1 if a > _epsilon else 0,
    # functionsl with multiple arguments
    "multiply": lambda a, b: a * b,
    "hypot": math.hypot,
    # functions with a variable number of arguments
    "all": lambda *a: all(a),
    "Fibonacci": gmpy2.fib,
    "fibonacci": gmpy2.fib,
    "F": gmpy2.fib,
    "Fib": gmpy2.fib,
    "fib": gmpy2.fib,
    "Lucas": gmpy2.lucas,
    "Euler": sympy.euler,
    "Pell": lambda n: gmpy2.lucasu(2, -1, n),
    "Phi_": lambda n, x: sympy.polys.specialpolys.cyclotomic_poly(n, x),
    "tens_complement_factorial": A110396,
    "Tribonacci": A000073,
    "Sylvester": A000058,
    "Sm": lambda n: gmpy2.mpz(A007908(n)),
}


def _evaluate_stack(s):
    op, num_args = s.pop(), 0
    if isinstance(op, tuple):
        op, num_args = op
    if op == "unary -":
        return -_evaluate_stack(s)
    if op == "!":
        return gmpy2.fac(_evaluate_stack(s))
    if op == "#":
        return sympy.primorial(primesieve.count_primes(0, _evaluate_stack(s)))
    if op in "+-*/^":
        # note: operands are pushed onto the stack in reverse order
        op2 = _evaluate_stack(s)
        op1 = _evaluate_stack(s)
        return _opn[op](op1, op2)
    elif op == "PI":
        return math.pi  # 3.1415926535
    elif op == "E":
        return math.e  # 2.718281828
    elif op in _fn:
        # note: args are pushed onto the stack in reverse order
        args = reversed([_evaluate_stack(s) for _ in range(num_args)])
        return _fn[op](*args)
    elif re.match(r"A\d{6}", op):
        # note: args are pushed onto the stack in reverse order
        args = reversed([_evaluate_stack(s) for _ in range(num_args)])
        return gmpy2.mpz(importlib.import_module(f"sequences.{op}")(*args))
    elif op[0].isalpha():
        raise Exception("invalid identifier '%s'" % op)
    else:
        # try to evaluate as int first, then as float if int fails
        try:
            return gmpy2.mpz(op)
        except ValueError:
            return float(op)


def evaluate(s):
    if not s:
        return None
    _exprStack[:] = []
    results = _BNF().parseString(s, parseAll=True)
    val = _evaluate_stack(_exprStack[:])
    return val


if __name__ == "__main__":

    def test(s, expected):
        _exprStack[:] = []
        try:
            results = _BNF().parseString(s, parseAll=True)
            val = _evaluate_stack(_exprStack[:])
        except ParseException as pe:
            print(s, "failed parse:", str(pe))
        except Exception as e:
            print(s, "failed eval:", str(e), _exprStack)
        else:
            if val == expected:
                print(s, "=", val, results, "=>", _exprStack)
            else:
                print(s + "!!!", val, "!=", expected, results, "=>", _exprStack)

    test("523#+1", 8709668761379269784034173446876636639594408083936553641753483991897255703964943107588335040121154680170867105541177741204814011615930342030904704147856733048115934632145172739949220591246493529224396454328521288726491)
    test("tens_complement_factorial(112)-1", A110396(112)-1)
    test("Phi_{17}(5461881130856756498343881353355730200091930726446628652260883480575183173)", sympy.polys.specialpolys.cyclotomic_poly(17,5461881130856756498343881353355730200091930726446628652260883480575183173))
    test("A007942(3)", gmpy2.mpz(32123))
    test("7^384-384", pow(gmpy2.mpz(7), 384) - 384)
    test("110!+7", gmpy2.fac(110) + 7)
    test("Fibonacci(1423)", gmpy2.fib(1423))
    test("2^1497-1", pow(gmpy2.mpz(2), 1497)-1)
    test("9", 9)
    test("-9", -9)
    test("--9", 9)
    test("-E", -math.e)
    test("9 + 3 + 6", 9 + 3 + 6)
    test("9 + 3 / 11", 9 + 3.0 // 11)
    test("(9 + 3)", (9 + 3))
    test("(9+3) / 11", (9 + 3.0) // 11)
    test("9 - 12 - 6", 9 - 12 - 6)
    test("9 - (12 - 6)", 9 - (12 - 6))
    test("2*3.14159", 2 * 3.14159)
    test("3.1415926535*3.1415926535 / 10", 3.1415926535 * 3.1415926535 // 10)
    test("PI * PI / 10", math.pi * math.pi // 10)
    test("PI*PI/10", math.pi * math.pi // 10)
    test("PI^2", math.pi ** 2)
    test("round(PI^2)", round(math.pi ** 2))
    test("6.02E23 * 8.048", 6.02e23 * 8.048)
    test("e / 3", math.e // 3)
    test("sin(PI/2)", math.sin(math.pi // 2))
    test("10+sin(PI/4)^2", 10 + math.sin(math.pi // 4) ** 2)
    test("trunc(E)", int(math.e))
    test("trunc(-E)", int(-math.e))
    test("round(E)", round(math.e))
    test("round(-E)", round(-math.e))
    test("E^PI", math.e ** math.pi)
    test("exp(0)", 1)
    test("exp(1)", math.e)
    test("2^3^2", 2 ** 3 ** 2)
    test("(2^3)^2", (2 ** 3) ** 2)
    test("2^3+2", 2 ** 3 + 2)
    test("2^3+5", 2 ** 3 + 5)
    test("2^9", 2 ** 9)
    test("sgn(-2)", -1)
    test("sgn(0)", 0)
    test("sgn(0.1)", 1)
    test("foo(0.1)", None)
    test("round(E, 3)", round(math.e, 3))
    test("round(PI^2, 3)", round(math.pi ** 2, 3))
    test("sgn(cos(PI/4))", 1)
    test("sgn(cos(PI/2))", 0)
    test("sgn(cos(PI*3/4))", -1)
    test("+(sgn(cos(PI/4)))", 1)
    test("-(sgn(cos(PI/4)))", -1)
    test("hypot(3, 4)", 5)
    test("multiply(3, 7)", 21)
    test("all(1,1,1)", True)
    test("all(1,1,1,1,1,0)", False)