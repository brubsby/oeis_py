from modules.kamada_prime_difficulty import read_prime_difficulty_txt
from modules.oeis_query import query_sequences_from_subsequence


# for each entry in kamada's prime_difficulty.txt, search a subsequence of the found primes for oeis existence
for row in read_prime_difficulty_txt():
    # skip forms with 0 or 1 primes
    if "(" in row['(probable) prime numbers']:
        continue
    # remove "n=" from list of primes and convert to int list
    subsequence = list(map(int, row['(probable) prime numbers'][2:].split(",")))
    if len(subsequence) < 4:
        # less than 4 primes found, not worth oeis sequence
        continue
    # calculate number of terms to query with
    # max 10 usually enough for uniqueness
    # -4 to account for oeis not being up-to-date (end terms missing)
    # min 5
    search_start_term = 2
    term_to_search_to = max(min(10+search_start_term, len(subsequence) - 4), 5)
    if term_to_search_to-search_start_term < 3:
        # if we're only querying 1 or 2 numbers, there will always be too many results
        continue
    search_terms = subsequence[search_start_term:term_to_search_to]
    # might be poor practice to query oeis ~2000 times each run, but it's easier than downloading the dump
    results = query_sequences_from_subsequence(search_terms)
    if not results:
        continue
    elif len(results) > 1:
        message = "too many results"
    elif len(results) == 1:
        message = f"A{results[0]['number']:06}"
        oeis_terms = list(map(int, results[0]["data"].split(",")))
        # start terms disagree a lot
        while oeis_terms[0] in [0, 1, 2]:
            oeis_terms = oeis_terms[1:]
        while subsequence[0] in [0, 1, 2]:
            subsequence = subsequence[1:]
        if subsequence != oeis_terms:
            message += f" check disparity {set(subsequence).symmetric_difference(set(oeis_terms))}"
    print(f"{row['wlabel']: <40} "
          f"{message: <40} "
          f"https://oeis.org/search?q={','.join(map(str, search_terms)): <40}"
          f"{', '.join(map(str, subsequence)): <40}")

