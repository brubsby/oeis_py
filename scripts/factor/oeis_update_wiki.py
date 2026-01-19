import logging
import math
import re
import sys
import time

import gmpy2

from oeispy.utils import expression, factor
from oeispy.utils.oeis_factor_db import OEISFactorDB

work_regex = re.compile(r"(((\d+)@(\d+(?:(?:e|\*10\^)\d+)?)(,\s)?)+|t\d+)")

# reasons we might need to update the page:
# 1. work is higher now (in the case that expression is the same)
# 2. composite has decreased in size due to finding a factor
# 3. composite has been factored, "[factored]" probably good here for work
# possibly also include link to updating the sequence in the case of 3
# 4. expression collision (merge sequence references), composite collision can stay separate
if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    db = OEISFactorDB()
    parsed_data = db.parse_wiki_page()
    updated_lines = []
    for row in parsed_data:
        line = row["line"]
        wiki_num_digits = row["composite_digits"]
        expr = row["expression"]
        sequences = row["sequences"]
        wiki_work = row["work"]
        more = row["more"]
        factor_requirement = row["factor_requirement"]
        updated = False
        value = None
        if "Cbig" in line or (wiki_num_digits and wiki_num_digits > 10000):  # don't mess with the enormous ones
            continue
        # skip the ones with no expression, we will perhaps get to these later
        if not expr:
            continue
        value = None
        # first check if line is factored completely
        try:
            # TODO speed up calculations here, very slow sometimes
            start = time.time()
            value = expression.evaluate(expr)
            logger.debug(f"{expr} took {time.time() - start:.02f} seconds to calculate")
        except Exception as e:
            logger.error(f"Failed to evaluate expression: {expr}")
            logger.error(e)
            # can't calculate a value for this line, continue
            continue
        if not value:
            continue
        remaining_composites = factor.factordb_get_remaining_composites(value)
        if value > math.prod(remaining_composites) * 11 and factor_requirement == "semiprimality":
            updated_lines.append(re.sub(work_regex, "[factors found]", line))
            if "[factors found]" not in updated_lines[-1]:
                updated_lines[-1] = updated_lines[-1] + "[factors found]"
            continue
        elif len(remaining_composites) == 0:
            updated_lines.append(re.sub(work_regex, "[factored]", line))
            if "[factored]" not in updated_lines[-1]:
                updated_lines[-1] = updated_lines[-1] + "[factored]"
            # factored completely
            continue
        # check composite length
        calculated_composite_digits = [gmpy2.num_digits(composite) for composite in remaining_composites]
        if not any(map(lambda calculated_digits: abs(calculated_digits - wiki_num_digits) <= 1, calculated_composite_digits)):
            # there exists a value that has no remaining composites of approximate length to wiki line
            # this means that we likely found a factor and need to update the wiki line
            line = re.sub(r"C(big|\d+)", f"C{min(calculated_composite_digits)}", line)
            updated = True
        # check work
        logger.debug(f"Getting work for:\n{line}")
        work_done = max([db.get_work(composite) or 0 for composite in remaining_composites])
        if work_done - wiki_work >= 1:
            old_line = line
            t_string = f"t{work_done:g}"
            work_position = 56
            line = re.sub(work_regex, t_string, line)
            if line == old_line:
                line = line.strip()
                if len(line) > work_position:
                    line = line[:work_position] + f"{t_string}, " + line[work_position:]
                else:
                    line = line.ljust(56) + t_string
            updated = True
        if updated:
            updated_lines.append(line)
            continue
    print("lines to update:")
    for line in updated_lines:
        print(line)
