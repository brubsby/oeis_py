import argparse
import datetime
import itertools
import logging
import math
import os
import pickle
import re
import sqlite3
import sys
import time

import gmpy2
import requests

from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from modules import yafu, factor, factordb

DB_NAME = "aliquot.db"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "db", DB_NAME)
YAFU_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "logs", f"aliquot-yafu.log")
Path(os.path.dirname(YAFU_LOG_PATH)).mkdir(parents=True, exist_ok=True)


def positive_integer(arg):
    val = int(arg)
    if val < 1:
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
    if gmpy2.num_digits(n) >= 50:
        factor_db_factors = factor.factordb_factor(n, num_retries=0, sleep_time=0)
        if factor_db_factors != -1:
            return factor_db_factors
    return yafu.factor(n, threads=threads, line_reader=yafu_line_reader)


def aliquot_sum(n, threads=1, yafu_line_reader=None):
    return factor.aliquot_sum(n, factors=factorize(n, threads=threads, yafu_line_reader=yafu_line_reader))


class YafuLineReader:
    """Object to handle reading yafu lines to discern progress"""
    def __init__(self, yafu_file_logger, log_level, term, last_term):
        self.logger = yafu_file_logger
        self.log_level = log_level
        self.term = term
        self.factors = {}
        self.remaining_composite = term
        self.composite_str = None
        self.b1 = None
        self.b2 = None
        self.rels_found = 0
        self.rels_needed = None
        self.num_digits = gmpy2.num_digits(term)
        self.glyph = "●" if last_term is None else ("▲" if term > last_term else "▼")
        self.yafu_progress = ""
        self.stage = None
        self.max_yafu_progress = 0


    def _update_composite_str(self):
        elided = f"{str(self.term)[:6] + '...' + str(self.term)[-6:]}" \
            if self.num_digits > 15 else self.composite_str
        factor_str = ".".join([f"{str(p)}^{str(e)}" if e > 1 else (str(p) if gmpy2.num_digits(p) < 10 else f"P{str(gmpy2.num_digits(p))}")
                                 for p, e in self.factors.items()])
        self.composite_str = f"{elided} = {factor_str}"
        if self.remaining_composite > 1:
            self.composite_str += f".C{gmpy2.num_digits(self.remaining_composite)}"


    def _add_factor(self, new_factor):
        new_factor = gmpy2.mpz(new_factor)
        if gmpy2.is_divisible(self.remaining_composite, new_factor):
            self.remaining_composite = self.remaining_composite // new_factor
            self.factors[new_factor] = self.factors.get(new_factor, 0) + 1
            self._update_composite_str()

    def _parse_progress(self, line):
        if "found prp" in line:
            match = re.search(r"prp(\d+) = (\d+)", line)
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
                if b2 is not None and b2 not in ["gmp-ecm default", "100*"]:
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
            self.rels_needed = int(match.group(1))
        elif line.startswith("***factors found***"):
            self.yafu_progress = ""

        if self.stage == "SIQS":
            eta = None
            match = re.search(r"(\d+) rels found", line)
            if match:
                self.rels_found = int(match.group(1))
            match = re.search(r"ETA (\d) sec")
            if match:
                eta = match.group(1)
            self.yafu_progress = "SIQS"
            if self.rels_needed is not None:
                self.yafu_progress += f" {min(1.0, self.rels_found / self.rels_needed):0.1%}"
            if eta is not None:
                self.yafu_progress += f" ETA: {eta} sec"


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
            print(f" {timestr} {self.glyph} C{self.num_digits} = {self.composite_str} > {self.yafu_progress: <{self.max_yafu_progress}}\r", end="")
            # and log the output to a file
        self.logger.debug(line)



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
        latest_term_fdb = factordb.get_latest_aliquot_term(sequence)
        value = latest_term_fdb.get_value()
        term_size = gmpy2.num_digits(value)
        composite_size = gmpy2.num_digits(latest_term_fdb.get_factor_list()[-1])
        term_id = latest_term_fdb.get_id()
        cur = self.connection.cursor()
        # TODO calculate new info instead of NULL
        cur.execute("""
        UPDATE aliquot
        SET term_size = ?, composite_size = ?, leading_id = ?,
        guide = NULL, class = NULL, abundance = NULL, known_factors = NULL, progress = NULL, is_driver = NULL
        WHERE sequence = ?;
        """, (term_size, composite_size, term_id, sequence))
        self.connection.commit()



    def get_smallest(self, term=True):
        cur = self.connection.cursor()
        ordering_clauses = ['term_size ASC', 'composite_size ASC']
        ordering_clauses = ordering_clauses if term else list(reversed(ordering_clauses))
        # higher classes have lower stability
        ordering_clauses.append('class DESC')
        ordering = ', '.join(ordering_clauses)
        cur.execute(f"SELECT * FROM aliquot WHERE reservation = '' ORDER BY {ordering};")
        rows = cur.fetchall()
        for row in rows:
            fdb = factordb.FactorDB(row[-2], is_id=True)
            fdb.connect()
            if fdb.get_status() == 'FF':
                # sequence entry out of date, should probably just query the aliquot sequence page
                # just go on to the next number for now
                self.update_sequence(row[0])
                return self.get_smallest(term=term)
            else:
                return fdb.get_value()


    def get_term_size_floor(self, term=True):
        cur = self.connection.cursor()
        cur.execute(f"SELECT MIN(term_size) FROM aliquot WHERE reservation = '';")
        row = cur.fetchone()
        val = row[0]
        return val

    def fetch_data(self):
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
        "--update",
        action="store_true",
        dest="update",
        help="print an update post with the first 200 out of date sequences that we know about",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-e",
        "--smallest-term",
        action="store_true",
        dest="smallest_term",
        help="run yafu on the smallest terms on the blue page",
    )
    group.add_argument(
        "-c",
        "--smallest-composite",
        action="store_true",
        dest="smallest_composite",
        help="run yafu on the smallest composites on the blue page",
    )
    group.add_argument(
        "-q"
        "--composite",
        nargs="?",
        dest="composite",
        help="specific composite to start on",
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

    num_threads = args.threads
    composite = args.composite
    smallest_term = args.smallest_term
    smallest_composite = args.smallest_composite
    update = args.update
    fetch = args.fetch

    if fetch:
        db = AliquotDB()
        db.fetch_data()
    if update:
        db = AliquotDB()
        print(db.get_update_post())
        sys.exit()

    file_logger = logging.getLogger('yafu.log')
    file_logger_handler = TimedRotatingFileHandler(YAFU_LOG_PATH, when='midnight', backupCount=3)
    file_logger_handler.terminator = ""
    file_logger_handler.setFormatter(logging.Formatter('%(message)s'))
    file_logger.propagate = False
    file_logger.setLevel(logging.DEBUG)
    file_logger.addHandler(file_logger_handler)

    if composite:
        last_term = None
        term = factordb.get_latest_aliquot_term(composite).get_value()
        while True:
            line_reader = YafuLineReader(file_logger, loglevel, term, last_term)
            last_term = term
            term = aliquot_sum(last_term, threads=num_threads, yafu_line_reader=line_reader)

    elif smallest_term or smallest_composite:
        db = AliquotDB()
        while True:
            last_term = None
            term = db.get_smallest(term=smallest_term)
            line_reader = YafuLineReader(file_logger, loglevel, term, last_term)
            term_size_target = db.get_term_size_floor() + 1
            last_term = term
            term = aliquot_sum(last_term, threads=num_threads, yafu_line_reader=line_reader)
            while gmpy2.num_digits(term) <= term_size_target:
                line_reader = YafuLineReader(file_logger, loglevel, term, last_term)
                last_term = term
                term = aliquot_sum(last_term, threads=num_threads, yafu_line_reader=line_reader)



