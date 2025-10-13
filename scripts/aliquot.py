import argparse
import datetime
import itertools
import logging
import os
import pickle
import re
import shutil
import sqlite3
import sys
import time

import gmpy2
import requests

from logging.handlers import RotatingFileHandler
from pathlib import Path

from modules import yafu, factor, factordb

DB_NAME = "aliquot.db"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "db", DB_NAME)
YAFU_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "logs", f"aliquot-yafu-{time.time()}.log")
UNBOUNDED_20M_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "aliquot", "unbounded_20M.txt")
Path(os.path.dirname(YAFU_LOG_PATH)).mkdir(parents=True, exist_ok=True)


def positive_integer(arg):
    val = int(arg)
    if val < 1:
        raise ValueError(f"{arg} not a positive integer")
    return val


def nonnegative_integer(arg):
    val = int(arg)
    if val < 0:
        raise ValueError(f"{arg} not a positive integer")
    return val


def date_converter(val):
    val = val.decode("utf-8")
    if val.isnumeric():
        return datetime.date.today()
    return datetime.datetime.strptime(val, "%Y-%m-%d").date()


def datetime_converter(val):
    return datetime.datetime.strptime(val.decode("utf-8"), "%Y-%m-%d %H:%M:%S")


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def factorize(n, threads=1, yafu_line_reader=None):
    if type(n) != gmpy2.mpz:
        n = gmpy2.mpz(n)
    if n < 2:
        return []
    if gmpy2.num_digits(n) >= 80:
        factor_db_factors = factor.factordb_factor(n, num_retries=0, sleep_time=0)
        if factor_db_factors != -1:
            return factor_db_factors
    return yafu.factor(n, threads=threads, line_reader=yafu_line_reader)


def aliquot_sum(n, threads=1, yafu_line_reader=None, report_function=None):
    factors = factorize(n, threads=threads, yafu_line_reader=yafu_line_reader)
    if report_function is None:
        factordb.report({n: factors})
    else:
        report_function({n: factors})
    return factor.aliquot_sum(n, factors=factors)


def num_digits(n):
    return len(str(n))


def get_elf_path(n):
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "elf", f"{int(n)}.elf")


def parse_elf_line(line):
    matches = re.split('[.=*\t ]+', line)
    index = int(matches[0])
    value = gmpy2.mpz(matches[1])
    factor_strings = matches[2:]
    known_factor_dict = dict(map(lambda splote: (int(splote[0]), 1 if len(splote) == 1 else int(splote[1])),
                           map(lambda factor_string: factor_string.split("^"), factor_strings)))
    return index, value, known_factor_dict


def parse_elf_file(filename):
    ret = {}
    if os.path.exists(filename):
        with open(filename, "r") as f:
            for line in f.readlines():
                if line and line.replace("\x00", ""):
                    i, value, known_factor_dict = parse_elf_line(line)
                    ret[i] = {"value": value, "known_factors": known_factor_dict}
    return ret



def evaluate(n, i):
    """api for expression library to calculate aliquot terms, returns None if not yet known by factordb"""
    elf_path = get_elf_path(n)
    if os.path.exists(elf_path):
        with open(elf_path, "r") as f:
            for line in f.readlines():
                index, value, known_factor_dict = parse_elf_line(line)
                if i == index:
                    return value
    # either downloading for the first time or updating it with latest
    factordb.download_elf_for_seq(n)
    with open(elf_path, "r") as f:
        for line in f.readlines():
            index, value, known_factor_dict = parse_elf_line(line)
            if i == index:
                return value


def get_last_c80_term(n):
    """get last c80 term for the alimerge file, returns None if not found"""
    ret_value = None
    value = n
    this_digits = num_digits(value)
    elf_path = get_elf_path(n)
    if os.path.exists(elf_path):
        with open(elf_path, "r") as f:
            for line in f.readlines():
                last_digits = this_digits
                last_value = value
                index, value, known_factor_dict = parse_elf_line(line)
                this_digits = num_digits(value)
                if this_digits == 81 and last_digits == 80:
                    ret_value = last_value
        if ret_value:
            return ret_value
    value = n
    this_digits = num_digits(value)
    # either downloading for the first time or updating it with latest
    factordb.download_elf_for_seq(n)
    with open(elf_path, "r") as f:
        for line in f.readlines():
            last_digits = this_digits
            last_value = value
            index, value, known_factor_dict = parse_elf_line(line)
            this_digits = num_digits(value)
            if this_digits == 81 and last_digits == 80:
                ret_value = last_value
    if ret_value:
        return ret_value


class YafuLineReader:
    """Object to handle reading yafu lines to discern progress"""
    def __init__(self, yafu_file_logger, log_level, name, term, last_term, plain=False):
        self.logger = yafu_file_logger
        self.log_level = log_level
        self.name = name
        self.term = term
        self.plain = plain
        self.factors = {}
        self.remaining_composite = term
        self.composite_str = None
        self.b1 = None
        self.b2 = None
        self.rels_found = 0
        self.total_yield = 0
        self.rels_needed = None
        self.num_digits = num_digits(term)
        self.glyph = "●" if last_term is None else ("▲" if term > last_term else "▼")
        self.yafu_progress = ""
        self.stage = None
        self.secondary_stage = None
        self.max_yafu_progress = 0
        self.process_line("")
        self.has_printed_plain = False


    def _update_composite_str(self):
        elided = f"{str(self.term)[:6] + '...' + str(self.term)[-6:]}" \
            if self.num_digits > 15 else self.composite_str
        factor_str = ".".join([f"{str(p)}^{str(e)}" if e > 1 else (str(p) if num_digits(p) < 10 else f"P{str(num_digits(p))}")
                                 for p, e in sorted(self.factors.items())])
        self.composite_str = f"{factor_str}"
        if self.remaining_composite > 1:
            self.composite_str += f"{'.' if factor_str != '' else ''}C{num_digits(self.remaining_composite)}"


    def _add_factor(self, new_factor):
        new_factor = gmpy2.mpz(new_factor)
        if gmpy2.is_divisible(self.remaining_composite, new_factor):
            self.remaining_composite = self.remaining_composite // new_factor
            self.factors[new_factor] = self.factors.get(new_factor, 0) + 1
            self._update_composite_str()

    def _parse_progress(self, line):
        if "found prp" in line:
            match = re.search(r"prp(\d+) factor = (\d+)", line)
            if match:
                self._add_factor(match.group(2))
        elif line.startswith("div:"):
            self.yafu_progress = "DIV"
            match = re.search(r"div: found prime factor = (\d+)", line)
            if match:
                self._add_factor(int(match.group(1)))
        elif line.startswith("fmt:"):
            self.yafu_progress = "FMT"
        elif line.startswith("rho:"):
            self.yafu_progress = "RHO"
        elif line.startswith("pm1:"):
            match = re.search(r"B1 = ([^,]+)", line)
            if match:
                self.b1 = match.group(1)
            self.yafu_progress = f"PM1 B1={self.b1}" if self.b1 is not None else f"PM1"
        elif line.startswith("ecm:"):
            if not line.startswith("ecm: process took"):
                self.yafu_progress = "ECM"
                curves_done = curves_planned = cofactor_digits = b1 = b2 = eta = None
                match = re.search(r"(\d+)/(\d+) curves on C(\d+)[^B]+B1=([^,]+), B2=([^,\r]+)", line)
                if match:
                    curves_done, curves_planned, cofactor_digits, b1, b2 = match.group(1, 2, 3, 4, 5)
                match = re.search(r"ETA[^0-9]+(\d+) sec", line)
                if match:
                    eta = match.group(1)
                if b1 is not None:
                    self.yafu_progress += f" B1={b1}"
                if b2 is not None and b2 not in ["gmp-ecm default", "100*B1"]:
                    self.yafu_progress += f" B2={b2}"
                if curves_done is not None:
                    self.yafu_progress += f" {curves_done}"
                    if curves_planned is not None:
                        self.yafu_progress += f"/{curves_planned}"
                if eta is not None:
                    self.yafu_progress += f" ETA: {eta} sec"
        elif line.startswith("starting SIQS on"):
            self.stage = "SIQS"
        elif line.startswith("==== sieving"):  # siqs rels needed
            self.stage = "SIQS"
            match = re.search(r"(\d+) relations needed", line)
            if match:
                self.rels_needed = int(match.group(1))
        elif line.startswith("nfs: commencing nfs on"):
            self.stage = "NFS"
            self.secondary_stage = "polysel"

        if self.stage == "SIQS":
            eta = None
            match = re.search(r"(\d+) rels found", line)
            if match:
                self.rels_found = int(match.group(1))
            match = re.search(r"ETA (\d+) sec", line)
            if match:
                eta = match.group(1)
            self.yafu_progress = "SIQS"
            if self.rels_needed is not None:
                self.yafu_progress += f" {min(1.0, self.rels_found / self.rels_needed):0.1%}"
            if eta is not None:
                self.yafu_progress += f" ETA: {eta} sec"
        elif self.stage == "NFS":
            percent = eta = None
            if "poly select done" in line:
                self.secondary_stage = "sieving"
            elif line.startswith("nfs: commencing msieve filtering"):
                self.secondary_stage = "filtering"
            elif line.startswith("linear algebra"):
                self.secondary_stage = "LA"

            if self.secondary_stage == "sieving":
                match = re.search(r"found (\d+) relations", line)
                if match:
                    self.rels_found = int(match.group(1))
                    self.total_yield = 0
                match = re.search(r"[Tt]otal yield: (\d+)", line)
                if match:
                    self.total_yield = int(match.group(1))
                match = re.search(r"need at least (\d+)", line)
                if match:
                    self.rels_needed = int(match.group(1))
                match = re.search(r"ETA: (\d+h \d+m)", line)
                if match:
                    eta = match.group(1)
                if self.rels_needed is not None:
                    percent = f"{min(1.0, (self.rels_found + self.total_yield) / self.rels_needed):0.1%}"
            elif self.secondary_stage == "filtering":
                if line.startswith("nfs: raising min_rels"):
                    match = re.search(r"percent to (\d)+", line)
                    if match:
                        self.rels_needed = int(match.group(1))
                    self.secondary_stage = "sieving"
            elif self.secondary_stage == "LA":
                match = re.search(r"(\d{1,2}\.\d%), ETA (\d+h \d+m)", line)
                if match:
                    percent, eta = match.group(1, 2)
            self.yafu_progress = f"NFS {self.secondary_stage}"
            if percent is not None:
                self.yafu_progress += f" {percent}"
            if eta is not None:
                self.yafu_progress += f" ETA: {eta}"


        if line.startswith("***factors found***"):
            self.stage = "finishing"
            self.yafu_progress = ""

        if self.stage == "finishing" and line.startswith("P"):
            match = re.search(r"P(\d+) = (\d+)", line)
            if match:
                size, new_factor = match.group(1, 2)
                self._add_factor(new_factor)

        self.max_yafu_progress = max(len(self.yafu_progress), self.max_yafu_progress)


    def process_line(self, line):
        self._parse_progress(line)
        if self.composite_str is None:
            self._update_composite_str()
        if self.log_level <= logging.DEBUG:
            # if we're debugging, just print out all of the yafu output
            print(line, end="")
        else:
            # otherwise do the cutesy single line progress per composite
            timestr = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            termsize = shutil.get_terminal_size().columns
            self.outstr = f" {timestr} {self.name : <13} {self.glyph} C{self.num_digits}.{str(self.term)[:2]} = {self.composite_str}"
            if not self.plain:
                outstr = f"{self.outstr} {'>' if self.yafu_progress.strip() != '' else ' '} {self.yafu_progress: <{self.max_yafu_progress}}\r"
                print(f"{outstr[:termsize-1]}\r" if len(outstr) > termsize-1 else outstr, end="")
            # and log the output to a file
        if line and line[-1] != "\r":
            self.logger.debug(line)

    def done(self):
        if self.plain:
            print(self.outstr)
            self.has_printed_plain = True
        if not self.has_printed_plain:
            print()



class AliquotDB:

    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        sqlite3.register_converter("PICKLE", pickle.loads)
        sqlite3.register_converter("DATE", date_converter)
        sqlite3.register_converter("DATETIME", datetime_converter)
        self.connection = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        self.create_db()

    def cursor(self):
        cursor = self.connection.cursor()
        cursor.row_factory = sqlite3.Row
        return cursor

    def create_db(self):
        cur = self.connection.cursor()
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS aliquot(
            sequence INTEGER PRIMARY KEY NOT NULL,
            sequence_index INTEGER,
            term_size INTEGER,
            composite_size INTEGER,
            guide TEXT,
            class INTEGER,
            abundance FLOAT,
            known_factors TEXT,
            reservation TEXT,
            progress DATE,
            last_updated DATETIME,
            priority FLOAT,
            leading_id INTEGER,
            is_driver BOOLEAN
        );
        """)

    def update_sequence(self, sequence):
        latest_term_fdb, index = factordb.get_latest_aliquot_term(sequence)
        value = latest_term_fdb.get_value()
        term_size = num_digits(value)
        composite_size = num_digits(latest_term_fdb.get_factor_list()[-1])
        term_id = latest_term_fdb.get_id()
        cur = self.connection.cursor()
        # if term size is less than 50 after query, sequence probably has a cycle
        # fdb autocompletes sequences under 50 digits
        if latest_term_fdb.get_status() in ["P", "PRP", "Prp"] or term_size < 45:
            cur.execute("DELETE FROM aliquot WHERE sequence = ?", (sequence,))
            print(f"{sequence} terminates!")
        else:
            # TODO calculate new info instead of NULL
            cur.execute("""
            UPDATE aliquot
            SET sequence_index = ?, term_size = ?, composite_size = ?, leading_id = ?,
            guide = NULL, class = NULL, abundance = NULL, known_factors = NULL, progress = NULL, is_driver = NULL
            WHERE sequence = ?;
            """, (index, term_size, composite_size, term_id, sequence))
        self.connection.commit()


    def get_earliest_under(self, num_digits, offset=None):
        cur = self.connection.cursor()
        cur.execute(f"SELECT * FROM aliquot WHERE reservation = '' AND term_size < ? ORDER BY sequence LIMIT 1 OFFSET ?;",
                    (num_digits, offset if offset else 0))
        rows = cur.fetchall()
        for row in rows:
            fdb = None
            if row[-2] is not None:
                fdb = factordb.FactorDB(row[-2], is_id=True)
                fdb.connect()
            if fdb is None or fdb.get_status() == 'FF':
                # sequence entry out of date, update this one and requery the db for the earliest
                self.update_sequence(row[0])
                return self.get_earliest_under(num_digits, offset=offset)
            else:
                return fdb, row



    def get_smallest(self, term=True, offset=None):
        cur = self.connection.cursor()
        if term:
            ordering_clauses = ['term_size ASC', 'sequence ASC']
        else:
            ordering_clauses = ['composite_size ASC', 'sequence ASC']
        ordering = ', '.join(ordering_clauses)
        cur.execute(f"SELECT * FROM aliquot WHERE reservation = '' ORDER BY {ordering} LIMIT 1 OFFSET {str(offset) if offset else '0'};")
        rows = cur.fetchall()
        for row in rows:
            fdb = None
            if row[-2] is not None:
                fdb = factordb.FactorDB(row[-2], is_id=True)
                fdb.connect()
            if fdb is None or fdb.get_status() == 'FF':
                # sequence entry out of date, update this one and requery the db for the smallest
                self.update_sequence(row[0])
                return self.get_smallest(term=term, offset=offset)
            else:
                return fdb, row


    def get_term_size_floor(self, term=True):
        cur = self.connection.cursor()
        cur.execute(f"SELECT MIN(term_size) FROM aliquot WHERE reservation = '';")
        row = cur.fetchone()
        val = row[0]
        return val

    def fetch_blue_page_data(self):
        response = requests.get("https://www.rechenkraft.net/aliquot/AllSeq.json")
        response.raise_for_status()
        data_list = response.json()["aaData"]
        cur = self.connection.cursor()
        cur.executemany("""
            INSERT INTO aliquot(
            sequence, sequence_index, term_size, composite_size, guide, class, abundance, known_factors, reservation,
            progress, last_updated, priority, leading_id, is_driver
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(sequence) DO UPDATE SET 
            sequence_index = excluded.sequence_index,
            term_size = excluded.term_size,
            composite_size = excluded.composite_size,
            guide = excluded.guide,
            class = excluded.class,
            abundance = excluded.abundance,
            known_factors = excluded.known_factors,
            reservation = excluded.reservation,
            progress = excluded.progress,
            last_updated = excluded.last_updated,
            priority = excluded.priority,
            leading_id = excluded.leading_id,
            is_driver = excluded.is_driver
            WHERE (reservation != excluded.reservation) OR last_updated < excluded.last_updated;
        """, data_list)
        self.connection.commit()


    def insert_unbounded_20m_data(self):
        cur = self.connection.cursor()
        unbounded_20m_data_regex = r"Sequence (\d+) to (\d+) digits"
        with open(UNBOUNDED_20M_PATH) as f:
            cur.executemany("""
            INSERT INTO aliquot(sequence, term_size) VALUES (?, ?)
            ON CONFLICT(sequence) DO NOTHING;
            """, map(lambda match: match.group(1, 2),
                     filter(None, map(lambda line: re.search(unbounded_20m_data_regex, line), f.readlines()))))
        self.connection.commit()



    def get_update_post(self):
        cur = self.connection.cursor()
        cur.execute("""
        SELECT sequence FROM aliquot WHERE guide IS NULL ORDER BY sequence ASC;
        """)
        rows = list(cur.fetchall())
        chunked = list(chunks(list(itertools.chain.from_iterable(rows)), 13))
        lines = [" ".join([str(innerinner) for innerinner in inner]) for inner in chunked]
        lines = ["Update " + line for line in lines]
        return "\n".join(lines)


    def get_next_open_sequence(self, sequence):
        cur = self.connection.cursor()
        cur.execute("""
        SELECT sequence FROM aliquot WHERE sequence > ? ORDER BY sequence ASC LIMIT 1;
        """, (sequence,))
        return cur.fetchone()[0]



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="verbosity (-v, -vv, etc)")
    parser.add_argument(
        "-f",
        "--fetch",
        action="store_true",
        help="fetch the latest reservations and status from the blue page into the db")
    parser.add_argument(
        "-t",
        "--threads",
        action="store",
        dest="threads",
        type=positive_integer,
        default=os.cpu_count(),
        help="number of threads to use in yafu",
    )
    parser.add_argument(
        "-d",
        "--digit-limit",
        action="store",
        dest="digit_limit",
        type=positive_integer,
        help="digit limit under which to continue a factoring a sequence",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        dest="update",
        help="print an update post with the first 200 out of date sequences that we know about",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-e",
        "--earliest-sequence",
        action="store_true",
        dest="earliest_sequence",
        help="run yafu on the earliest sequences in the database",
    )
    group.add_argument(
        "-r",
        "--smallest-term",
        action="store_true",
        dest="smallest_term",
        help="run yafu on the smallest terms in the database",
    )
    group.add_argument(
        "-c",
        "--smallest-composite",
        action="store_true",
        dest="smallest_composite",
        help="run yafu on the smallest composites in the database",
    )
    group.add_argument(
        "-q"
        "--composite",
        nargs="?",
        dest="composite",
        help="specific composite to start on",
    )
    parser.add_argument(
        "-o",
        "--offset",
        action="store",
        dest="offset",
        type=nonnegative_integer,
        help="offset from which to choose a sequence from a query, helps for parallelizing work on the same query",
    )
    parser.add_argument(
        "-p",
        "--plain",
        action="store_true",
        dest="plain",
        help="only output a line when it is done, no carriage return"
    )
    args = parser.parse_args()
    loglevel = logging.WARNING
    if args.verbose > 0:
        loglevel = logging.INFO
    if args.verbose > 1:
        loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel, format="%(message)s")

    logger = logging.getLogger("aliquot")
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(loglevel)
    handler.terminator = ""
    formatter = logging.Formatter(
        fmt='%(asctime)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    db = AliquotDB()

    num_threads = args.threads
    composite = args.composite
    earliest_sequence = args.earliest_sequence
    smallest_term = args.smallest_term
    smallest_composite = args.smallest_composite
    update = args.update
    fetch = args.fetch
    offset = args.offset
    digit_limit = args.digit_limit if args.digit_limit else db.get_term_size_floor()
    plain = args.plain

    if fetch:
        print("Fetching data from the blue page...")
        db.fetch_blue_page_data()
    if update:
        print(db.get_update_post())
        sys.exit()

    file_logger = logging.getLogger('yafu.log')
    file_logger_handler = RotatingFileHandler(YAFU_LOG_PATH, maxBytes=int(1e7), backupCount=3)
    file_logger_handler.terminator = ""
    file_logger_handler.setFormatter(logging.Formatter('%(message)s'))
    file_logger.propagate = False
    file_logger.setLevel(logging.DEBUG)
    file_logger.addHandler(file_logger_handler)

    factordb_report_pool = factordb.ReportThreadPool()

    if composite:
        while True:
            last_term = None
            term_fdb, index = factordb.get_latest_aliquot_term(composite)
            term = term_fdb.get_value()
            if term_fdb.get_status() in ["P", "PRP", "Prp"] or num_digits(term) < 45:
                print("Sequence terminated!")
                sys.exit()
            while True:
                name = f"{composite}:i{index}"
                line_reader = YafuLineReader(file_logger, loglevel, name, term, last_term, plain=plain)
                last_term = term
                term = aliquot_sum(last_term, threads=num_threads, yafu_line_reader=line_reader, report_function=factordb_report_pool.report)
                index += 1
                # factordb will continue sequences below 50 for us
                if num_digits(term) < 50:
                    break

    elif smallest_term or smallest_composite or earliest_sequence:
        while True:
            last_term = None
            if smallest_term or smallest_composite:
                term_fdb, row = db.get_smallest(term=smallest_term, offset=offset)
            else:
                term_fdb, row = db.get_earliest_under(digit_limit, offset=offset)
            term = term_fdb.get_value()
            seq = row[0]
            index = row[1]
            # TODO consider extracting the partial factorization for factordb
            name = f"{seq}:i{index}"
            line_reader = YafuLineReader(file_logger, loglevel, name, term, last_term, plain=plain)
            last_term = term
            term = aliquot_sum(last_term, threads=num_threads, yafu_line_reader=line_reader, report_function=factordb_report_pool.report)
            while num_digits(term) <= digit_limit:
                if num_digits(term) < 50:
                    last_term = None
                    term_fdb, index = factordb.get_latest_aliquot_term(seq)
                    term = term_fdb.get_value()
                    if term_fdb.get_status() in ["P", "PRP", "Prp"] or num_digits(term) < 45:
                        # probably terminates, move on to next one, and the query will update it as terminated.
                        break
                    if num_digits(term) > digit_limit:
                        break
                index += 1
                name = f"{seq}:i{index}"
                line_reader = YafuLineReader(file_logger, loglevel, name, term, last_term, plain=plain)
                last_term = term
                term = aliquot_sum(last_term, threads=num_threads, yafu_line_reader=line_reader, report_function=factordb_report_pool.report)
