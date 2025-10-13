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
import t_level

from modules import expression, factor, ecmtimes

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
            factor_requirement TEXT,
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
        
        
        -- CREATE VIEW IF NOT EXISTS composite_view
        
        -- table to store the different clients
        -- types IN ("CPU", "GPU", "AVX512")
        
        CREATE TABLE IF NOT EXISTS client(
            id INTEGER PRIMARY KEY NOT NULL,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL,
            creation_timestamp INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        
        -- table to store ecm stage 1 curve data
        
        CREATE TABLE IF NOT EXISTS stage_1_curve(
            composite_id INTEGER REFERENCES composite(id) ON DELETE CASCADE,
            client_id INTEGER REFERENCES client(id) ON DELETE SET NULL,
            stage_1_resume_line TEXT NOT NULL,
            sigma INTEGER NOT NULL,
            b1 INTEGER NOT NULL,
            ecm_param INTEGER,
            timestamp INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP,
            duration INTEGER,
            counted_in_t_level INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (composite_id, sigma, b1)
        );
        
        -- table to store ecm stage 2 curve data
        
        CREATE TABLE IF NOT EXISTS stage_2_curve(
            composite_id INTEGER REFERENCES composite(id) ON DELETE CASCADE,
            client_id INTEGER REFERENCES client(id) ON DELETE SET NULL,
            sigma INTEGER REFERENCES stage_1_curve(sigma) ON DELETE CASCADE,
            b2_start INTEGER NOT NULL,
            b2_end INTEGER NOT NULL,
            timestamp INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP,
            duration INTEGER,
            counted_in_t_level INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (composite_id, sigma, b2_start)
        );
        
        CREATE TABLE IF NOT EXISTS reservation(
            composite_id INTEGER REFERENCES composite(id) ON DELETE CASCADE,
            client_id INTEGER REFERENCES client(id) ON DELETE CASCADE,
            type INTEGER REFERENCES client(type) ON DELETE CASCADE,
            t_level_on_completion REAL,
            timestamp INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP,
            expiry_timestamp INTEGER NOT NULL DEFAULT (CURRENT_TIMESTAMP + (86400000 * 5)),
            PRIMARY KEY (composite_id, client_id, type)
        );
        """)

    def register_client(self, name, type="CPU"):
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO client(name, type) "
            "VALUES (?, ?);",
            (name, type)
        )
        self.connection.commit()


    # METHOD=ECM; SIGMA=16975636616726985561; B1=10000; N=(2^1129+1)/3; X=0x342d705ba8bfc2207ac27682cb14362f8bf7cb4ea665f17ea4de2eb2611b98656eae6ecd51ac88108713a04d9bbad4add3237e67648c5778ba7dd02655d6349024a2bda0966edd2d077d67e52f91e84a946e2431b34033d6d1118e73067d2b8a14ba0d2aaef071cb633212419bb17270bb175d249b40766ac9fcec158efd841bd70a6963ef13f39e827caaeec9; CHECKSUM=1474905577; PROGRAM=GMP-ECM 7.0.6; Y=0x0; X0=0x0; Y0=0x0; WHO=brubsby@bubtop; TIME=Mon Mar  3 00:16:49 2025;


    def submit_stage_1_curves(self, composite, residue_line, client_name, duration):
        values = dict(tuple(kvp.strip().split("=")) for kvp in residue_line.strip().split(";") if kvp)
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO stage_1_curve "
            "(composite_id, client_id, sigma, stage_1_resume_line, b1, ecm_param, duration) "
            "VALUES ((SELECT id FROM composite WHERE value = ?), "
            "(SELECT id FROM client WHERE name = ?), "
            "?, ?, ?, ?, ?);",
            (pickle.dumps(composite), client_name, residue_line,
             values.get("SIGMA"), values.get("B1"),
             values.get("PARAM"), duration)
        )
        # TODO free reservation
        self.connection.commit()

    def submit_stage_2_curves(self, composite, sigma, client_name, b2_start, b2_end, duration):
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO stage_2_curve "
            "(composite_id, client_id, sigma, b2_start, b2_end, duration) "
            "VALUES ((SELECT id FROM composite WHERE value = ?), "
            "(SELECT id FROM client WHERE name = ?), "
            "?, ?, ?, ?);",
            (pickle.dumps(composite), client_name, sigma, b2_start, b2_end, duration)
        )
        # TODO free reservation
        self.connection.commit()

    def request_stage1_GPU_work(self, client_name, digit_limit=300, curves=8192):
        cur = self.cursor()
        cur.execute(
            f"SELECT id, value, t_level, expression, digits "
            f"FROM composite WHERE digits < ? ORDER BY t_level ASC, digits ASC",
            (digit_limit,))
        result = cur.fetchall()
        tuples = list(map(lambda row: (
        ), result))
        tuples = sorted(tuples, key=lambda x: x[0])
        for completion_time, composite_row in tuples:
            if self.validate_stored_composite_unfactored(composite_row['value']):
                # TODO make reservation
                return composite_row['value'], self.get_optimal_gpu_b1(curves, int(composite_row['t_level'])), completion_time
            else:
                return self.request_stage1_GPU_work(client_name, digit_limit=digit_limit, curves=curves)

    def make_reservation(self, composite, client_name, t_level_on_completion):
        cur = self.cursor()
        cur.execute(
            "INSERT INTO reservation "
            "(composite_id, client_id, type, t_level_on_completion) "
            "VALUES ((SELECT id FROM composite WHERE value = ?), "
            "(SELECT id FROM client WHERE name = ?), "
            "(SELECT type FROM client WHERE name = ?), "
            "?);",
            (pickle.dumps(composite), client_name, client_name, t_level_on_completion)
        )
        self.connection.commit()


    def free_reservation(self, composite, client_name):
        cur = self.cursor()
        cur.execute(
            "DELETE FROM reservation "
            "WHERE composite_id = (SELECT id FROM composite WHERE value = ?) AND "
            "client_id = (SELECT id FROM client WHERE name = ?) AND "
            "client_type = (SELECT type FROM client WHERE name = ?);",
            (pickle.dumps(composite), client_name, client_name)
        )
        self.connection.commit()


    # assume GPU always takes same amount of time per B1
    # we want to find the B1 such that t-level grows fastest per B1
    # given the number of curves we have
    def get_optimal_gpu_b1(self, gpu_curves, existing_t_level):
        # start with a b1 guess
        b1 = t_level.get_regression_b1_for_t(existing_t_level + 1)
        existing_curves, existing_b1 = t_level.get_t_level_curves(existing_t_level)
        existing_curve_tup = (existing_curves, existing_b1, None, 1)
        max_val = 0
        max_b1 = b1
        direction = -1
        magnitude = 0.01
        misses = 0
        t_level_diff_per_b1 = (t_level.get_t_level([
            existing_curve_tup,
            (gpu_curves, b1, b1, 3)]) - existing_t_level) / b1
        for i in range(100):
            if t_level_diff_per_b1 > max_val:
                max_val = t_level_diff_per_b1
                max_b1 = b1
                misses = 0
            b1 = int(b1 * (1 + direction * magnitude))
            t_level_diff_per_b1 = (t_level.get_t_level([
                existing_curve_tup,
                (gpu_curves, b1, b1, 3)]) - existing_t_level) / b1
            if t_level_diff_per_b1 < max_val:
                if i == 0:
                    direction *= -1
                else:
                    misses += 1
                    if misses > 5:
                        break
        # return int(max_b1)
        return t_level.b1_level_round(max_b1)


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

    def add_composite(self, value, digits=None, expression=None, work=None, sequence_ids=None, k=None, first_sequence_more=None, factor_requirement=None):
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
            self.add_sequence(sequence_id, more=first_sequence_more if i == 0 else None, factor_requirement=factor_requirement)
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

    def process_parsed_wiki_page(self, parsed_data):
        for row in parsed_data:
            line = row["line"]
            num_digits = row["composite_digits"]
            expr = row["expression"]
            sequences = row["sequences"]
            t_level = row["work"]
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
                    self.add_composite(composite, digits=num_digits, expression=expr, sequence_ids=sequences, work=t_level, first_sequence_more=more, factor_requirement=factor_requirement)
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


    def validate_stored_composite_unfactored(self, old_composite):
        return self.get_remaining_composites(old_composite) == [old_composite]

    # transforms the old composite into a new one, if it's still unfactored
    def get_remaining_composites(self, old_composite):
        old_composite = gmpy2.mpz(old_composite)
        remaining_composites = factor.factordb_get_remaining_composites(old_composite)
        if remaining_composites == [old_composite]:
            return remaining_composites  # composite is unfactored still
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
            rows = cursor.fetchall()
            # there should be something here, otherwise just return the remaining composites
            if len(rows) == 0:
                return remaining_composites
            old_composite_id, old_work = rows[0]
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
            return remaining_composites
        elif len(remaining_composites) == 0:
            # no composites remaining here, just delete
            self.delete_composite(old_composite)
            return remaining_composites
        elif len(remaining_composites) > 1:
            # multiple new composites (not likely to happen)
            raise NotImplementedError(f"Multiple composites found in place of old composite:\nold:{old_composite}\nnew={remaining_composites}")

    def get_easiest_composite(self, digit_limit=500, pretest=0.3, delta_t=5, threads=1):
        cur = self.cursor()
        cur.execute(f"SELECT id, value, t_level, expression, digits FROM composite WHERE digits < ? AND t_level < (digits * ?) ORDER BY t_level ASC, digits ASC", (digit_limit, pretest))
        result = cur.fetchall()
        tuples = list(map(lambda row: (self.get_ecm_time(int(row['digits']), int(row['t_level']), ((int(row['t_level']) // delta_t) + 1) * delta_t, threads=threads), row), result))
        tuples = sorted(tuples, key=lambda x: x[0])
        for completion_time, composite_row in tuples:
            if self.validate_stored_composite_unfactored(composite_row['value']):
                return composite_row
            else:
                return self.get_easiest_composite(digit_limit=digit_limit, pretest=pretest, delta_t=delta_t, threads=threads)

    def get_smallest_t_level_composite(self, digit_limit=500, factor_requirement=None):
        cur = self.cursor()
        cur.execute(f"SELECT id, value, t_level, expression, digits FROM composite WHERE digits < ? ORDER BY t_level ASC, digits ASC", (digit_limit,))
        composite_row = cur.fetchone()
        if self.validate_stored_composite_unfactored(composite_row['value']):
            return composite_row
        else:
            return self.get_smallest_t_level_composite(digit_limit=digit_limit)

    def get_smallest_composite(self, digit_limit=500, pretest_limit=0.3):
        cur = self.cursor()
        cur.execute(f"SELECT id, value, t_level, expression, digits FROM composite WHERE digits < ? AND t_level < (digits * ?) ORDER BY digits ASC", (digit_limit, pretest_limit))
        result = cur.fetchall()
        for composite_row in result:
            if self.validate_stored_composite_unfactored(composite_row['value']):
                return composite_row
            else:
                return self.get_smallest_composite(digit_limit=digit_limit, pretest_limit=pretest_limit)

    def get_all_pretested_composites(self, pretest=0.3):
        cur = self.cursor()
        cur.execute(f"SELECT id, value, t_level, expression, digits FROM composite WHERE t_level > (digits * ?) ORDER BY digits ASC", (pretest,))
        result = cur.fetchall()
        print(f"{'expression':<32} digits t-level decimal-expansion")
        for composite_row in result:
            if self.validate_stored_composite_unfactored(composite_row['value']):
                print(f"{composite_row['expression']:<38} {composite_row['digits']:<6} {composite_row['t_level']:2.1f}    {composite_row['value']}")


    def get_ecm_time(self, digits, start_work, end_work, threads=1):
        # b1, curves = yafu.get_b1_curves(start_work, end_work)
        curves, b1, _, _, _ = t_level.get_suggestion_curves_from_t_levels(start_work or 0, end_work)
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