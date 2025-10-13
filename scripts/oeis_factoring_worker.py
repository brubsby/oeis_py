import logging.handlers
import os
import sys
import t_level

from modules import yafu, ecm, factordb
from modules.oeis_factor_db import OEISFactorDB


# pick up and do work on composites from the page
# https://oeis.org/w/index.php?title=OEIS_sequences_needing_factors&stable=0
if __name__ == "__main__":
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    yafu_logger = logging.getLogger("yafu")
    yafu_logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s |  %(levelname)s: %(message)s')
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    logFilePath = os.path.join("..", "data", "logs", "yafu.log")
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=logFilePath, when='midnight', backupCount=30)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    yafu_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)
    yafu_logger.info("started")

    db = OEISFactorDB()
    # db.process_parsed_wiki_page(db.parse_wiki_page())

    ecm_only = True
    num_threads = 12
    composite_size_limit = 500
    pretest_limit = 0.3
    delta_t_levels_per_job = 1
    if ecm_only:
        while True:
            composite_row = db.get_smallest_composite(digit_limit=composite_size_limit, pretest_limit=pretest_limit)
            target_t_level = ((int(composite_row['t_level']) // delta_t_levels_per_job) + 1) * delta_t_levels_per_job
            completion_time = db.get_ecm_time(int(composite_row['digits']), int(composite_row['t_level']), target_t_level, threads=num_threads)
            root_logger.info(f"selected C{composite_row['digits']} belonging to {composite_row['expression']}, from t{composite_row['t_level']:.02f} to t{target_t_level:.02f}, should complete in {completion_time/3600:.02f} hours")
            composite = composite_row['value']
            work = float(composite_row['t_level'])
            pretest_level = ((work // delta_t_levels_per_job) + 1) * delta_t_levels_per_job
            curves, b1, _, _, _ = t_level.get_suggestion_curves_from_t_levels(work or 0, pretest_level)
            factors = ecm.ecm(composite, b1, curves, num_threads, start_t=work)
            factordb.report({composite: factors})
            if len(factors):
                root_logger.info("Found factors!")
            db.update_work(composite, pretest_level)
    else:
        # run smallest
        while True:
            composite_row = db.get_smallest_composite(digit_limit=composite_size_limit)
            root_logger.info(f"selected C{composite_row['digits']} belonging to {composite_row['expression']}, with existing work t{composite_row['t_level']:.02f}")
            composite = composite_row['value']
            work = float(composite_row['t_level'])
            factors = yafu.factor(composite, threads=num_threads, work=composite_row['t_level'])
            if len(factors) > 1:
                root_logger.info(f"Found factors! {factors}")
