import os
import sys

import gmpy2
import requests

from modules import factordb

from scripts import aliquot


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def get_to_upload_elf_path(n):
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "aliquot", "to_upload", f"alq_{int(n)}.elf")


START_SEQ = 9101790
CHUNK_SIZE = 50

if __name__ == "__main__":
    db = aliquot.AliquotDB()
    seq = START_SEQ
    while True:
        to_upload_filename = get_to_upload_elf_path(seq)
        print(f"checking {seq} at {to_upload_filename}")
        # check if we have an upload file for the sequence
        if os.path.exists(to_upload_filename):
            to_upload_elf_dict = aliquot.parse_elf_file(to_upload_filename)
            factordb.download_elf_for_seq(seq)
            factordb_elf_dict = aliquot.parse_elf_file(aliquot.get_elf_path(seq))
            max_upload_index = max(to_upload_elf_dict.keys())
            max_factordb_index = max(factordb_elf_dict.keys())
            # if our version goes further than factordb version
            if max_upload_index > max_factordb_index:
                to_upload = [(to_upload_elf_dict[i]["value"], list(filter(lambda x: gmpy2.num_digits(x) > 10, to_upload_elf_dict[i]["known_factors"].keys()))) for i in range(max_factordb_index, max_upload_index+1)]
                to_upload = list(filter(lambda tup: gmpy2.num_digits(tup[0]) > 49, to_upload))
                to_upload_chunks = chunks(to_upload, CHUNK_SIZE)
                for chunk in to_upload_chunks:
                    response = factordb.report(dict(chunk))
                # print(to_upload)
                print(f"uploaded {len(to_upload)} composites")

        seq = db.get_next_open_sequence(seq)




