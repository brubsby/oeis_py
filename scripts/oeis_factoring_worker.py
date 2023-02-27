import logging.handlers
import os
import sys

from modules import yafu
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
    while True:
        composite_row = db.get_easiest_composite(digit_limit=1000)
        root_logger.info(f"selected C{composite_row['digits']} belonging to {composite_row['expression']}, with existing work t{composite_row['t_level']:.02f}")
        composite = composite_row['value']
        work = float(composite_row['t_level'])
        pretest_level = ((work // 5) + 1) * 5  # next multiple of 5 t-level, perhaps reduce to 1 as t-level gets higher
        factors = yafu.factor(composite, threads=8, work=composite_row['t_level'], pretest=pretest_level)
        if len(factors) > 1:
            root_logger.info("Found factors!")
        db.update_work(composite, pretest_level)
