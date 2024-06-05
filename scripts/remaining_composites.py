import argparse
import logging
import sys

import gmpy2

from modules import batch_factordb

__version__ = "0.0.1"


def stdin_composite_generator():
    for line in sys.stdin.readlines():
        try:
            composite = int(line)
        except ValueError:
            continue
        yield composite


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=f"Looks up composites provided in stdin to determine if they have been fully or partially factored")
        parser.add_argument(
            "--version",
            action="version",
            version="%(prog)s (version {version})".format(version=__version__))
        parser.add_argument(
            "-v",
            "--verbose",
            action="count",
            default=0,
            help="verbosity (-v, -vv, etc)")
        parser.add_argument(
            "-r",
            "--remove",
            action="store_true",
            dest="remove_partially_factored",
            help="completely removes partially factored candidates, a bit faster")
        parser.add_argument(
            "-u",
            "--unordered",
            action="store_true",
            dest="unordered",
            help="return composites as they're retrieved, gets going a bit faster")


        args = parser.parse_args()

        loglevel = logging.WARNING
        if args.verbose > 0:
            loglevel = logging.INFO
        if args.verbose > 1:
            loglevel = logging.DEBUG

        root = logging.getLogger()
        root.setLevel(loglevel)

        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(loglevel)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        root.addHandler(handler)


        for factordb_result in batch_factordb.batch_factordb(stdin_composite_generator(), ordered=not args.unordered):
            if factordb_result.get_status() in ["C", "U"]:
                print(factordb_result.get_val())
            elif factordb_result.get_status() in ["CF"] and not args.remove_partially_factored:
                logging.debug(factordb_result.get_factor_from_api())
                for factor in map(lambda x: int(x[0]), factordb_result.get_factor_from_api()):
                    if not gmpy2.is_prime(factor):
                        print(factor)
    except (KeyboardInterrupt, BrokenPipeError):
        pass
