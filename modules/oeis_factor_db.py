import heapq
import logging
import os
import re
import sqlite3
import pickle
import sys
import time

import requests
from lxml import html

import gmpy2

from modules import expression, factor, prime, ecmtimes, yafu
from modules import t_level as tlev

DB_NAME = "oeis_factor.db"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "db", DB_NAME)

logger = logging.getLogger("oeis_factor_db")


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


class OEISFactorDB:

    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        sqlite3.register_converter("PICKLE", pickle.loads)
        self.connection = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        self.create_db()

    def cursor(self):
        cursor = self.connection.cursor()
        cursor.row_factory = sqlite3.Row
        return cursor

    def create_db(self):
        cur = self.connection.cursor()
        cur.executescript("""
        -- composite factoring priorities:
        -- 0: factoring this number will give a new term in an oeis sequence that has the "more" tag
        -- 1: factoring this composite might give a new term in an oeis sequence that has the "more" tag
        -- 2: factoring this composite will give a new term in an oeis sequence that has a full data section
        -- 3: factoring this composite might give a new term in an oeis sequence
        -- 4: there are no known oeis sequences at present that will benefit from factoring this composite
        CREATE TABLE IF NOT EXISTS composite(
            id INTEGER PRIMARY KEY NOT NULL,
            value PICKLE UNIQUE,
            expression TEXT,
            digits INTEGER NOT NULL,
            t_level REAL,
            UNIQUE (value, expression)
        );
    
        -- "more" is the oeis keyword boolean field for whether factoring the number gets a data section addition
        -- first unknown n is the n of the next term that needs factoring
        -- first unknown k is the next k in the expression that needs factoring if it is not equal to n
        CREATE TABLE IF NOT EXISTS sequence(
            id TEXT PRIMARY KEY NOT NULL,
            more INTEGER,
            factor_requirement INTEGER,
            first_unknown_n INTEGER,
            first_unknown_k INTEGER
        );
    
        -- many-to-many table to map composites and sequences together.
        -- a sequence can have many composites and a composite can be associated with many sequences.
        -- associated_k is the "n" or "k" value associated with the expression to be factored, we usually want to factor the
        -- lowest k first, and possibly higher k if the first one is very hard
    
        CREATE TABLE IF NOT EXISTS composite_to_sequence(
            composite_id INTEGER REFERENCES composite(id) ON DELETE CASCADE,
            sequence_id TEXT REFERENCES sequence(id) ON DELETE CASCADE,
            k INTEGER,
            PRIMARY KEY (composite_id, sequence_id)
        );
        """)
        # todo make view

    def add_sequence(self, sequence_id, more=None, factor_requirement=None, first_unknown_n=None, first_unknown_k=None):
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO sequence(id, more, factor_requirement, first_unknown_n, first_unknown_k) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET "
            "more=IFNULL(excluded.more, more), "
            "factor_requirement=IFNULL(excluded.factor_requirement, factor_requirement), "
            "first_unknown_n=IFNULL(excluded.first_unknown_n, first_unknown_n), "
            "first_unknown_k=IFNULL(excluded.first_unknown_k, first_unknown_k);",
            (sequence_id, more, factor_requirement, first_unknown_n, first_unknown_k)
        )
        self.connection.commit()

    def add_composite(self, value, digits=None, expression=None, work=None, sequence_ids=None, k=None, first_sequence_more=None):
        if value is not None and type(value) != gmpy2.mpz:
            value = gmpy2.mpz(value)
        if value is not None:
            digits = gmpy2.num_digits(value)
        cursor = self.connection.cursor()
        composite_id = None
        # insert a composite if we have the value, work done, or composite size
        if value is not None:
            cursor.execute(
                "INSERT INTO composite(value, expression, digits, t_level) "
                "VALUES (?, ?, ?, ?) "
                "ON CONFLICT(value) DO UPDATE SET "
                "expression=IFNULL(excluded.expression, expression), "
                "digits=IFNULL(excluded.digits, digits), "
                "t_level=MAX(IFNULL(excluded.t_level, 0), IFNULL(t_level, 0));",
                (pickle.dumps(value) if value else None, expression, digits, work)
            )
            composite_id = cursor.lastrowid
        elif expression is not None or work is not None:
            cursor.execute(
                "INSERT INTO composite(expression, digits, t_level) "
                "VALUES (?, ?, ?) "
                "ON CONFLICT(value, expression) DO UPDATE SET "
                "expression=IFNULL(excluded.expression, expression), "
                "digits=IFNULL(excluded.digits, digits), "
                "t_level=MAX(IFNULL(excluded.t_level, 0), IFNULL(t_level, 0));",
                (expression, digits, work)
            )
            composite_id = cursor.lastrowid
        for i, sequence_id in enumerate(sequence_ids):
            self.add_sequence(sequence_id, more=first_sequence_more if i == 0 else None)
            if composite_id is not None:
                cursor.execute(
                    "INSERT OR IGNORE INTO composite_to_sequence(composite_id, sequence_id, k) VALUES (?, ?, ?);",
                    (composite_id, sequence_id, k)
                )
        self.connection.commit()

    def get_all_composites(self):
        cursor = self.cursor()
        cursor.execute("SELECT * FROM composite;")
        result = cursor.fetchall()
        return result

    def parse_wiki_page(self):
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
        parsed_data = []
        for line in info_lines:
            t_level = max(
                tlev.get_t_level([(sci_int(curves), sci_int(b1)) for curves, b1 in re.findall(work_regex, line)]),
                float((lambda x: x.group(1) if x else 0.0)(re.search(t_level_regex, line))))
            associated_sequences = re.findall(sequence_id_regex, line)
            num_digits = (lambda x: int(x.group(1)) if x else None)(re.search(composite_digits_regex, line))

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
                "work": t_level,
                "more": more,
                "sequences": associated_sequences,
            }
            parsed_data.append(parsed_line)
        return parsed_data

    def process_parsed_wiki_page(self, parsed_data):
        for row in parsed_data:
            line = row["line"]
            num_digits = row["composite_digits"]
            expr = row["expression"]
            sequences = row["sequences"]
            t_level = row["work"]
            more = row["more"]
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
                    self.add_composite(composite, digits=num_digits, expression=expr, sequence_ids=sequences, work=t_level, first_sequence_more=more)
            else:
                logger.error(f"No composite value for \n{line}")
                for sequence in sequences:
                    self.add_sequence(sequence, more=more)

    def delete_composite(self, composite):
        assert composite is not None
        cursor = self.cursor()
        cursor.execute("DELETE FROM composite WHERE value = ?;", (pickle.dumps(composite),))
        self.connection.commit()

    def get_work(self, composite):
        assert composite is not None
        cursor = self.cursor()
        cursor.execute("SELECT t_level FROM composite WHERE value = ?;", (pickle.dumps(composite),))
        result = cursor.fetchone()
        if result:
            return result['t_level']

    def update_work(self, composite, new_work):
        assert composite is not None
        cursor = self.cursor()
        cursor.execute("UPDATE composite SET t_level = MAX(?, t_level) WHERE value = ?", (new_work, pickle.dumps(composite)))
        self.connection.commit()

    # transforms the old composite into a new one, if it's still unfactored
    def validate_stored_composite_unfactored(self, old_composite):
        remaining_composites = factor.factordb_get_remaining_composites(old_composite)
        if remaining_composites == [old_composite]:
            return True  # composite is unfactored still
        elif len(remaining_composites) == 1:  # new single unfactored composite different to the one we passed in
            new_composite = remaining_composites[0]
            new_digits = gmpy2.num_digits(new_composite)
            logger.info(f"stored composite partially factored, C{gmpy2.num_digits(old_composite)} -> C{new_digits}, http://factordb.com/index.php?query={old_composite}")
            # composite was factored to something smaller, but still needs more factoring
            cursor = self.cursor()
            # see if we have anything for this new composite already
            cursor.execute("SELECT id, t_level FROM composite WHERE value = ?;", (pickle.dumps(new_composite),))
            new_composite_id, new_work = cursor.fetchone() or (None, None)
            # get the metadata for the old composite
            cursor.execute("SELECT id, t_level FROM composite WHERE value = ?;", (pickle.dumps(old_composite),))
            old_composite_id, old_work = cursor.fetchone()
            # there should be something here, otherwise there's problems
            assert old_composite_id is not None
            # conservatively take the maximum of the work for both composites
            work = max(new_work or 0, old_work)
            # get the sequences associated with the old composite
            cursor.execute("SELECT sequence_id FROM composite_to_sequence WHERE composite_id = ?", (old_composite_id,))
            sequences = [row["sequence_id"] for row in cursor.fetchall()]
            if new_composite_id:  # there was an existing composite of this value in the db
                logger.info(f"following C{new_digits} already existed in db: {new_composite}")
            # both cases work for this method
            self.add_composite(new_composite, sequence_ids=sequences, work=work)
            logger.info(f"moving sequence pointers to new composite and deleting old record")
            self.delete_composite(old_composite)
            return False  # false because the composite wasn't unfactored
        elif len(remaining_composites) == 0:
            # no composites remaining here, just delete
            self.delete_composite(old_composite)
        elif len(remaining_composites) > 1:
            # multiple new composites (not likely to happen)
            raise NotImplementedError(f"Multiple composites found in place of old composite:\nold:{old_composite}\nnew={remaining_composites}")

    def get_easiest_composite(self, digit_limit=500, pretest=0.3, threads=1):
        cur = self.cursor()
        cur.execute(f"SELECT id, value, t_level, expression, digits FROM composite WHERE digits < ? AND t_level < (digits * ?) ORDER BY t_level ASC, digits ASC", (digit_limit, pretest))
        result = cur.fetchall()
        tuples = list(map(lambda row: (self.get_ecm_time(int(row['digits']), int(row['t_level']), ((int(row['t_level']) // 5) + 1) * 5, threads=threads), row), result))
        tuples = sorted(tuples, key=lambda x: x[0])
        for completion_time, composite_row in tuples:
            if self.validate_stored_composite_unfactored(composite_row['value']):
                return composite_row, completion_time
            else:
                return self.get_easiest_composite(digit_limit=digit_limit, pretest=pretest, threads=threads)

    def get_smallest_t_level_composite(self, digit_limit=500):
        cur = self.cursor()
        cur.execute(f"SELECT id, value, t_level, expression, digits FROM composite WHERE digits < ? ORDER BY t_level ASC, digits ASC", (digit_limit,))
        composite_row = cur.fetchone()
        if self.validate_stored_composite_unfactored(composite_row['value']):
            return composite_row
        else:
            return self.get_smallest_t_level_composite(digit_limit=digit_limit)

    def get_smallest_composite(self, digit_limit=500, pretest=0.3):
        cur = self.cursor()
        cur.execute(f"SELECT id, value, t_level, expression, digits FROM composite WHERE digits < ? AND t_level < (digits * ?) ORDER BY digits ASC", (digit_limit, pretest))
        result = cur.fetchall()
        for composite_row in result:
            if self.validate_stored_composite_unfactored(composite_row['value']):
                return composite_row
            else:
                return self.get_smallest_composite(digit_limit=digit_limit, pretest=pretest)

    def get_ecm_time(self, digits, start_work, end_work, threads=1):
        b1, curves = yafu.get_b1_curves(start_work, end_work)
        return ecmtimes.get_ecm_time(digits, b1, curves, threads=threads)

    def get_smallest_known_composites_with_no_values(self):
        cur = self.connection.cursor()
        cur.row_factory = sqlite3.Row
        cur.execute("SELECT composite_to_sequence.sequence_id, value, expression, digits, t_level "
                    "FROM composite INNER JOIN composite_to_sequence "
                    "ON composite.id = composite_to_sequence.composite_id "
                    "WHERE value IS NULL "
                    "ORDER BY digits ASC")
        result = cur.fetchall()
        return result

    def get_sequences_with_no_composites(self):
        cur = self.connection.cursor()
        cur.row_factory = sqlite3.Row
        cur.execute("SELECT sequence.id "
                    "FROM sequence LEFT OUTER JOIN composite_to_sequence "
                    "ON sequence.id = composite_to_sequence.sequence_id "
                    "WHERE composite_to_sequence.sequence_id IS NULL "
                    "ORDER BY sequence.id ASC")
        result = cur.fetchall()
        return result


if __name__ == "__main__":
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    root_logger.addHandler(handler)

    db = OEISFactorDB()
    db.process_parsed_wiki_page(db.parse_wiki_page())
    # print(db.get_easiest_composite())
    [print(row["id"]) for row in db.get_sequences_with_no_composites()]