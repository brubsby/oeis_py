import argparse
import logging
import os

from modules import factor


def positive_integer(arg):
    val = int(arg)
    if val < 1:
        raise ValueError(f"{arg} not a positive integer")
    return val


def get_furthest_composite(composite):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="verbosity (-v, -vv, etc)")
    parser.add_argument(
        "-t",
        "--threads",
        action="store",
        dest="threads",
        type=positive_integer,
        default=os.cpu_count(),
        help="number of threads to use in yafu"
    )
    parser.add_argument(
        "composite",
        action="store",
        type=positive_integer,
        help="composite to start on"
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

    term = composite
    while True:
        print(term)
        term = factor.aliquot_sum(term, threads=num_threads)
