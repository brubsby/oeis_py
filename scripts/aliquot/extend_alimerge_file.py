import os
import sys

import requests

from scripts import aliquot

ALIMERGE_FILE_URL = "http://www.aliquotes.com/OE_5000000_C80.txt"
ALIMERGE_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "aliquot", "OE_5000000_C80.txt")

if __name__ == "__main__":
    if not os.path.exists(ALIMERGE_FILE_PATH):
        try:
            response = requests.get(ALIMERGE_FILE_URL)
            response.raise_for_status()
            with open(ALIMERGE_FILE_PATH, 'wb') as f:
                f.write(response.content)
        except Exception as e:
            raise e

    aliquot_db = aliquot.AliquotDB()

    with open(ALIMERGE_FILE_PATH, 'r+') as f:
        last_line = f.readlines()[-1]
        seq = int(last_line.strip().split(" ")[0])
        while True:
            seq = aliquot_db.get_next_open_sequence(seq)
            val = aliquot.get_last_c80_term(seq)
            if val is None:
                print(f"Sequence {seq} didn't have a C80, quitting...")
                sys.exit()
            row_str = f" {seq} {int(val)}"
            print(row_str, file=f)
            print(row_str)



