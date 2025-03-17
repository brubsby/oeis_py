from modules import factor

import logging

composite = 14808792150068793172532790450261201276647164621470285707307674226764745750868863344476120227039785442

threads = 16

def get_furthest_composite(composite):
    pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    term = composite
    while True:
        term = factor.aliquot_sum(term, threads=12)
