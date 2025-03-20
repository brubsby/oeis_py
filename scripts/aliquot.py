import argparse
import datetime
import itertools
import logging
import os
import pickle
import sqlite3

import gmpy2
import requests

from modules import factor, factordb

DB_NAME = "aliquot.db"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "db", DB_NAME)

logger = logging.getLogger("aliquot_db")


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
        ordering = ', '.join(ordering_clauses if term else reversed(ordering_clauses))
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
        SELECT sequence FROM aliquot WHERE guide IS NULL ORDER BY composite_size ASC, term_size ASC LIMIT 200;
        """)
        rows = list(cur.fetchall())
        chunked = list(chunks(list(itertools.chain.from_iterable(rows)), 10))
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
        type=positive_integer,
        help="specific composite to start on",
    )
    args = parser.parse_args()
    loglevel = logging.WARNING
    if args.verbose > 0:
        loglevel = logging.INFO
    if args.verbose > 1:
        loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel, format="%(message)s")

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
    elif composite:
        term = composite
        while True:
            print(term)
            term = factor.aliquot_sum(term, threads=num_threads)
    elif smallest_term or smallest_composite:
        db = AliquotDB()
        while True:
            term = db.get_smallest(term=smallest_term)
            next_term = factor.aliquot_sum(term, threads=num_threads)
            while gmpy2.num_digits(next_term) <= 101:
                term = next_term
                next_term = factor.aliquot_sum(term, threads=num_threads)


