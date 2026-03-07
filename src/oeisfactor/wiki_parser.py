import logging
import re
import time
import requests
from lxml import html
import gmpy2
import t_level

from oeispy.utils import expression, factor

logger = logging.getLogger(__name__)

def sci_int(x):
    if x is None or type(x) in [int, gmpy2.mpz]:
        return x
    if type(x) != str:
        raise TypeError(f"sci_int needs a string input, instead of {type(x)} {x}")
    if x.isnumeric():
        return int(x)
    match = re.match(r"^(\d+)(?:e|[x*]10\^)(\d+)$", x)
    if not match:
        raise ValueError(f"malformed intger string {x}, could not parse into an integer")
    return gmpy2.mpz(match.group(1)) * pow(10, gmpy2.mpz(match.group(2)))

def parse_wiki_page():
    page_request = requests.get("https://oeis.org/wiki/OEIS_sequences_needing_factors?stable=0")
    page_content = page_request.content
    parsed = html.fromstring(page_content)
    text = parsed.text_content()
    info_lines = list(filter(lambda line: re.search(r"^A[0-9]{6}", line), text.split("\n")))
    work_regex = re.compile(r"(\d+)@(\d+(?:(?:e|\*10\^)\d+)?)")
    t_level_regex = re.compile(r"\Wt(\d{1,2})")
    sequence_id_regex = re.compile(r"A\d{6}(?![(^_])")
    composite_digits_regex = re.compile(r"\WC(\d+)")
    expression_regex = re.compile(r"C(?:\d+|big)\s{1,15}(\*?)(.*?)(?:t\d+|\d+@|\s{2,}|$)")
    factor_requirement_regex = re.compile(r"\[(specific small factors|smallest factor|semiprimality|\d-almost primality)\]")
    parsed_data = []
    for line in info_lines:
        line_t_level = max(
            t_level.get_t_level([(int(sci_int(curves)), int(sci_int(b1)), None, None) for curves, b1 in re.findall(work_regex, line)]),
            float((lambda x: x.group(1) if x else 0.0)(re.search(t_level_regex, line))))
        associated_sequences = re.findall(sequence_id_regex, line)
        num_digits = (lambda x: int(x.group(1)) if x else None)(re.search(composite_digits_regex, line))
        factor_requirement = (lambda x: str(x.group(1)) if x else None)(re.search(factor_requirement_regex, line))

        search = re.search(expression_regex, line)
        expr = more = None
        if search:
            more = search.group(1) == "*"
            expr = search.group(2)
            expr = expr.split(" or ")[0]
            expr = expr.replace("[F^R(1801) is semiprime]", "")
            expr = expr.strip()
        parsed_line = {
            "line": line,
            "expression": expr,
            "composite_digits": num_digits,
            "work": line_t_level,
            "more": more,
            "sequences": associated_sequences,
            "factor_requirement": factor_requirement,
        }
        parsed_data.append(parsed_line)
    return parsed_data

def process_parsed_wiki_page(db, parsed_data):
    for row in parsed_data:
        line = row["line"]
        num_digits = row["composite_digits"]
        expr = row["expression"]
        sequences = row["sequences"]
        t_level_val = row["work"]
        more = row["more"]
        factor_requirement = row["factor_requirement"]
        value = None
        if "Cbig" in line or (num_digits and num_digits > 10000):  # don't mess with the enormous ones
            continue
        try:
            # TODO speed up calculations here, very slow sometimes
            start = time.time()
            value = expression.evaluate(expr)
            logger.debug(f"{expr} took {time.time()-start:.02f} seconds to calculate")
        except Exception as e:
            logger.error(f"Failed to evaluate expression: {expr}")
            logger.error(e)
        if value:
            remaining_composites = factor.factordb_get_remaining_composites(value)
            for composite in remaining_composites:
                calculated_digits = gmpy2.num_digits(composite) if composite else None
                if num_digits and composite and abs(calculated_digits - num_digits) > 1:
                    logger.error(f"calculated ({calculated_digits}) and reported ({num_digits}) digit length disparity for:\n{line}")
                db.add_composite(composite, digits=num_digits, expression=expr, sequence_ids=sequences, work=t_level_val, first_sequence_more=more, factor_requirement=factor_requirement)
        else:
            logger.error(f"No composite value for \n{line}")
            for sequence in sequences:
                db.add_sequence(sequence, more=more)
