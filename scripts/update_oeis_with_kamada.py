from modules.kamada_prime_difficulty import read_prime_difficulty_txt
from modules.oeis_query import query_sequence_from_name


# for each entry in kamada's prime_difficulty.txt, search a subsequence of the found primes for oeis existence and
# whether they need to be updated
for row in read_prime_difficulty_txt():
    # skip forms with 0 or 1 primes
    if "(" in row['(probable) prime numbers']:
        continue
    if not row['oeis']:
        continue
    # remove "n=" from list of primes and convert to int list
    kamada_sequence = list(map(int, row['(probable) prime numbers'][2:].split(",")))
    sequence = kamada_sequence
    kamada_search_limit = int(row['range'][3:]) if row['range'] else None
    results = query_sequence_from_name(row['oeis'])
    if not results:
        message = "doesn't exist"
    elif len(results) > 1:
        message = "too many results"
    elif len(results) == 1:
        oeis_sequence = list(map(int, results[0]["data"].split(",")))
        if kamada_sequence == oeis_sequence:
            continue
        oeis_set = set(oeis_sequence)
        kamada_set = set(kamada_sequence)
        kamada_update = oeis_set.difference(kamada_set)
        oeis_update = kamada_set.difference(oeis_set)
        # filter out the disjoint results, i.e. the primes that are greater than the search limit
        oeis_update = list(filter(lambda x: x <= kamada_search_limit, oeis_update))
        message = ""
        # if kamada_update:
        #     message += f"update kamada {sorted(kamada_update)} "
        if oeis_update:
            message += f"update oeis {sorted(oeis_update)} "
        else:
            continue
        sequence = list(sorted(oeis_set.union(kamada_set)))
    print(f"{row['wlabel']: <10} "
          f"https://oeis.org/{row['oeis']: <20}"
          f"{message: <40}"
          f"{', '.join(map(str, sequence)): <40}")

