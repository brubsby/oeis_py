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

from oeispy.utils import expression, factor, ecmtimes

DB_NAME = "oeis_factor.db"
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "db", DB_NAME)

logger = logging.getLogger("oeis_factor_db")


class OEISFactorDB:

    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        sqlite3.register_converter("PICKLE", pickle.loads)
        self.connection = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
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
            client_type INTEGER REFERENCES client(type) ON DELETE CASCADE,
            t_level_on_completion REAL,
            timestamp INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP,
            expiry_timestamp INTEGER NOT NULL DEFAULT (CURRENT_TIMESTAMP + (86400000 * 5)),
            PRIMARY KEY (composite_id, client_id, client_type)
        );
        """)

    def register_client(self, name, type="CPU"):
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO client(name, type) "
            "VALUES (?, ?) "
            "ON CONFLICT(name) DO UPDATE SET type=excluded.type;",
            (name, type)
        )
        self.connection.commit()


    # METHOD=ECM; SIGMA=16975636616726985561; B1=10000; N=(2^1129+1)/3; X=0x342d705ba8bfc2207ac27682cb14362f8bf7cb4ea665f17ea4de2eb2611b98656eae6ecd51ac88108713a04d9bbad4add3237e67648c5778ba7dd02655d6349024a2bda0966edd2d077d67e52f91e84a946e2431b34033d6d1118e73067d2b8a14ba0d2aaef071cb633212419bb17270bb175d249b40766ac9fcec158efd841bd70a6963ef13f39e827caaeec9; CHECKSUM=1474905577; PROGRAM=GMP-ECM 7.0.6; Y=0x0; X0=0x0; Y0=0x0; WHO=brubsby@bubtop; TIME=Mon Mar  3 00:16:49 2025;


    def submit_stage_1_curves(self, composite, residue_lines, client_name, duration):
        cursor = self.connection.cursor()
        
        cursor.execute("SELECT id FROM composite WHERE value = ?", (pickle.dumps(composite),))
        comp_res = cursor.fetchone()
        if not comp_res:
            raise ValueError("Composite not found")
        composite_id = comp_res[0]
        
        cursor.execute("SELECT id FROM client WHERE name = ?", (client_name,))
        client_res = cursor.fetchone()
        if not client_res:
            raise ValueError("Client not found")
        client_id = client_res[0]
        
        insert_data = []
        # Support single string fallback
        if isinstance(residue_lines, str):
            residue_lines = [residue_lines]
            
        for residue_line in residue_lines:
            if not residue_line.strip():
                continue
            values = dict(tuple(kvp.strip().split("=")) for kvp in residue_line.strip().split(";") if kvp)
            insert_data.append((
                composite_id,
                client_id,
                values.get("SIGMA"),
                residue_line,
                values.get("B1"),
                values.get("PARAM"),
                duration
            ))
            
        cursor.executemany(
            "INSERT INTO stage_1_curve "
            "(composite_id, client_id, sigma, stage_1_resume_line, b1, ecm_param, duration) "
            "VALUES (?, ?, ?, ?, ?, ?, ?);",
            insert_data
        )
        # TODO free reservation
        self.connection.commit()

    def _update_composite_t_level(self, cursor, composite_id):
        """Add newly completed curves to the composite's t_level.

        The current t_level already encodes all previously counted work (both ours
        and external). We convert it to an equivalent curve tuple as the baseline,
        then stack only the uncounted new curves on top. After updating, we mark
        those curves counted so they are never added again.
        """
        cursor.execute("SELECT t_level FROM composite WHERE id = ?", (composite_id,))
        row = cursor.fetchone()
        current_t = (row['t_level'] or 0) if row else 0

        # Only grab curves not yet counted — avoids double-counting with current_t
        cursor.execute("""
            SELECT s1.b1, s2.b2_end, s1.ecm_param, COUNT(*) as n_curves
            FROM stage_1_curve s1
            JOIN stage_2_curve s2 ON s1.sigma = s2.sigma AND s1.composite_id = s2.composite_id
            WHERE s1.composite_id = ? AND s2.counted_in_t_level = 0
            GROUP BY s1.b1, s2.b2_end, s1.ecm_param
        """, (composite_id,))

        new_curve_groups = cursor.fetchall()
        if not new_curve_groups:
            return

        curve_tuples = []
        # Treat current t_level as the baseline (external + previously counted work)
        if current_t > 0:
            baseline_curves, baseline_b1 = t_level.get_t_level_curves(current_t)
            curve_tuples.append((baseline_curves, baseline_b1, None, 1))
        for row in new_curve_groups:
            curve_tuples.append((row['n_curves'], row['b1'], row['b2_end'], row['ecm_param'] or 1))

        new_t = t_level.get_t_level(curve_tuples)

        cursor.execute(
            "UPDATE composite SET t_level = MAX(?, IFNULL(t_level, 0)) WHERE id = ?",
            (new_t, composite_id)
        )
        # Mark the newly counted stage_1 curves (those whose stage_2 we just counted)
        cursor.execute("""
            UPDATE stage_1_curve SET counted_in_t_level = 1
            WHERE composite_id = ? AND counted_in_t_level = 0
              AND sigma IN (
                  SELECT sigma FROM stage_2_curve
                  WHERE composite_id = ? AND counted_in_t_level = 0
              )
        """, (composite_id, composite_id))
        # Mark the newly counted stage_2 curves
        cursor.execute("""
            UPDATE stage_2_curve SET counted_in_t_level = 1
            WHERE composite_id = ? AND counted_in_t_level = 0
        """, (composite_id,))

    def submit_stage_2_curves_batch(self, completions, client_name):
        """Insert multiple stage 2 completions in a single transaction and update t-levels."""
        cursor = self.cursor()
        cursor.execute("SELECT id FROM client WHERE name = ?", (client_name,))
        client_res = cursor.fetchone()
        if not client_res:
            raise ValueError("Client not found")
        client_id = client_res[0]

        insert_data = [
            (
                pickle.dumps(gmpy2.mpz(c["composite"])),
                client_id,
                c["sigma"],
                c["b2_start"],
                c["b2_end"],
                c["duration"],
            )
            for c in completions
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO stage_2_curve "
            "(composite_id, client_id, sigma, b2_start, b2_end, duration) "
            "VALUES ((SELECT id FROM composite WHERE value = ?), ?, ?, ?, ?, ?);",
            insert_data,
        )

        # Recalculate t-level for each distinct composite in this batch (usually just one)
        seen = set()
        for c in completions:
            composite_key = pickle.dumps(gmpy2.mpz(c["composite"]))
            if composite_key in seen:
                continue
            seen.add(composite_key)
            cursor.execute("SELECT id FROM composite WHERE value = ?", (composite_key,))
            row = cursor.fetchone()
            if row:
                self._update_composite_t_level(cursor, row[0])

        self.connection.commit()

        # Return new t_levels keyed by composite string
        new_t_levels = {}
        for c in completions:
            composite_key = pickle.dumps(gmpy2.mpz(c["composite"]))
            if composite_key not in new_t_levels:
                cursor.execute("SELECT t_level, expression FROM composite WHERE value = ?", (composite_key,))
                row = cursor.fetchone()
                if row:
                    new_t_levels[c["composite"]] = {"t_level": row["t_level"], "expression": row["expression"]}
        return new_t_levels

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
        best_composite = None
        best_score = float('inf')
        best_b1 = None
        
        # Check the top theoretical easiest composites
        for i, row in enumerate(self.iter_unfactored_composites(digit_limit, skip_with_outstanding_residues=True, validate=False)):
            if i >= 50:
                break
                
            t_level_val = float(row['t_level'] or 0)
            digits = int(row['digits'])
            
            b1 = self.get_optimal_gpu_b1(curves, t_level_val)
            
            # Estimate how much this B1 will increase the t_level
            existing_curves, existing_b1 = t_level.get_t_level_curves(t_level_val)
            new_t_level = t_level.get_t_level([
                (existing_curves, existing_b1, None, 1),
                (curves, b1, b1, 3)
            ])
            delta_t = new_t_level - t_level_val
            
            if delta_t <= 0:
                continue
                
            # Time cost proxy: B1 * digits^2
            # We want to minimize (cost / delta_t)
            score = (b1 * (digits ** 2)) / delta_t
            
            if score < best_score:
                best_score = score
                best_composite = row['value']
                best_b1 = b1
                best_expression = row['expression']
                best_t_level = t_level_val

        if best_composite:
            # TODO: self.make_reservation(best_composite, client_name, ...)
            return best_composite, best_b1, 0, best_expression, best_t_level

        return None

    def request_full_CPU_work(self, client_name, digit_limit=300, t_step=1):
        """Select best composite and return curves+B1 needed to reach the next t-level milestone.

        Uses get_suggestion_curves to compute exactly how many curves at what B1 are needed
        to advance the composite by t_step t-levels. The client should run at most this many
        curves, truncating to fit within its time budget.
        """
        best_composite = None
        best_score = float('inf')
        best_b1 = None
        best_curves = None

        for i, row in enumerate(self.iter_unfactored_composites(digit_limit, validate=False)):
            if i >= 50:
                break

            t_level_val = float(row['t_level'] or 0)
            digits = int(row['digits'])
            target_t = t_level_val + t_step

            existing_curves, existing_b1 = t_level.get_t_level_curves(t_level_val)
            input_lines = [(existing_curves, existing_b1, None, 1)] if t_level_val > 0 else []

            suggested_curves, b1, _, _, _ = t_level.get_suggestion_curves(
                input_lines, t_level_val, target_t, None, None, 1, 1
            )

            new_t_level = t_level.get_t_level([
                *input_lines,
                (suggested_curves, b1, b1, 1)
            ])
            delta_t = new_t_level - t_level_val

            if delta_t <= 0:
                continue

            score = (b1 * (digits ** 2)) / delta_t

            if score < best_score:
                best_score = score
                best_composite = row['value']
                best_b1 = b1
                best_curves = suggested_curves
                best_expression = row['expression']
                best_t_level = t_level_val

        if best_composite:
            return best_composite, best_b1, best_curves, best_expression, best_t_level
        return None

    def submit_full_cpu_curves(self, composite, curve_groups, client_name):
        """Update t_level directly from full CPU ECM runs (no stage_1/stage_2 records).

        curve_groups: list of dicts with {count, b1, b2, ecm_param}
        """
        cursor = self.cursor()
        composite_mpz = gmpy2.mpz(str(composite))
        cursor.execute("SELECT id, t_level FROM composite WHERE value = ?", (pickle.dumps(composite_mpz),))
        row = cursor.fetchone()
        if not row:
            raise ValueError("Composite not found")
        composite_id, current_t = row['id'], float(row['t_level'] or 0)

        curve_tuples = []
        if current_t > 0:
            baseline_curves, baseline_b1 = t_level.get_t_level_curves(current_t)
            curve_tuples.append((baseline_curves, baseline_b1, None, 1))
        for g in curve_groups:
            curve_tuples.append((g['count'], g['b1'], g['b2'], g.get('ecm_param') or 1))

        new_t = t_level.get_t_level(curve_tuples)
        cursor.execute(
            "UPDATE composite SET t_level = MAX(?, IFNULL(t_level, 0)) WHERE id = ?",
            (new_t, composite_id)
        )
        self.connection.commit()
        return new_t

    def request_stage2_CPU_work(self, client_name, limit=100):
        cur = self.cursor()

        # We get the stage 1 resume line, composite info, and the sigma to identify it
        cur.execute("""
            SELECT s1.sigma, s1.stage_1_resume_line, s1.b1, s1.ecm_param,
                   c.value, c.t_level, c.expression, c.id as composite_id
            FROM stage_1_curve s1
            JOIN composite c ON s1.composite_id = c.id
            LEFT JOIN stage_2_curve s2 ON s1.sigma = s2.sigma AND s1.composite_id = s2.composite_id
            WHERE s2.sigma IS NULL
            ORDER BY c.digits ASC, s1.timestamp ASC
            LIMIT ?;
        """, (limit,))

        results = cur.fetchall()

        # No per-row FactorDB validation here — that was making up to `limit` HTTP
        # requests to factordb.com on every work request, adding minutes of latency.
        # Externally-factored composites are caught when a factor is submitted.
        work_batch = []
        for row in results:
            work_batch.append({
                "sigma": row["sigma"],
                "resume_line": row["stage_1_resume_line"],
                "b1": row["b1"],
                "composite": str(row["value"]),
                "expression": row["expression"],
                "t_level": row["t_level"],
            })
            # TODO: add reservation so other CPUs don't grab these same curves

        return work_batch

    def make_reservation(self, composite, client_name, t_level_on_completion):
        cur = self.cursor()
        cur.execute(
            "INSERT INTO reservation "
            "(composite_id, client_id, client_type, t_level_on_completion) "
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
        if sequence_ids is None:
            sequence_ids = []
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
        tuples = list(map(lambda row: (self.get_ecm_time(int(row['digits']), int(row['t_level'] or 0), ((int(row['t_level'] or 0) // delta_t) + 1) * delta_t, threads=threads), row), result))
        tuples = sorted(tuples, key=lambda x: x[0])
        for completion_time, composite_row in tuples:
            if self.validate_stored_composite_unfactored(composite_row['value']):
                return composite_row
            else:
                return self.get_easiest_composite(digit_limit=digit_limit, pretest=pretest, delta_t=delta_t, threads=threads)

    def iter_unfactored_composites(self, digit_limit=500, pretest=0.3, skip_with_outstanding_residues=False, validate=True):
        """Yields valid, unfactored composites from easiest to hardest (by t_level).

        Set validate=False to skip FactorDB HTTP lookups (composites that got
        factored externally will be caught at factor-submission time instead).
        """
        cur = self.cursor()

        if skip_with_outstanding_residues:
            # We filter out any composite that has a row in stage_1_curve without a matching row in stage_2_curve
            query = """
                SELECT c.id, c.value, c.t_level, c.expression, c.digits 
                FROM composite c
                WHERE c.digits < ? AND c.t_level < (c.digits * ?)
                  AND c.id NOT IN (
                      SELECT s1.composite_id 
                      FROM stage_1_curve s1
                      LEFT JOIN stage_2_curve s2 ON s1.sigma = s2.sigma AND s1.composite_id = s2.composite_id
                      WHERE s2.sigma IS NULL
                  )
                ORDER BY c.t_level ASC, c.digits ASC
            """
        else:
            query = """
                SELECT id, value, t_level, expression, digits 
                FROM composite 
                WHERE digits < ? AND t_level < (digits * ?) 
                ORDER BY t_level ASC, digits ASC
            """
            
        cur.execute(query, (digit_limit, pretest))
        
        for row in cur.fetchall():
            if not validate or self.validate_stored_composite_unfactored(row['value']):
                yield row

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
    import argparse
    parser = argparse.ArgumentParser(description="OEIS Factor DB Utility")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose (DEBUG) logging")
    args = parser.parse_args()

    root_logger = logging.getLogger()
    
    if args.verbose:
        root_logger.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    root_logger.addHandler(handler)

    db = OEISFactorDB()

    # print(db.get_easiest_composite())
    [print(row["id"]) for row in db.get_sequences_with_no_composites()]
