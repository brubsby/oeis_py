from modules.kamada_prime_difficulty import read_prime_difficulty_txt
from modules.oeis_query import query_sequences_from_subsequence


# for each entry in kamada's prime_difficulty.txt, search a subsequence of the found primes for oeis existence and
# whether they need to be updated
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
    # min 4
    search_start_term = 2
    term_to_search_to = max(min(10, len(subsequence) - 4), 4)
    if term_to_search_to-search_start_term < 3:
        # if we're only querying 1 or 2 numbers, there will always be too many results
        continue
    search_terms = subsequence[search_start_term:term_to_search_to]
    # might be poor practice to query oeis ~2000 times each run, but it's easier than downloading the dump
    results = query_sequences_from_subsequence(search_terms)
    if not results:
        message = "doesn't exist"
    elif len(results) > 1:
        message = "too many results"
    elif len(results) == 1:
        if subsequence[-1] != int(results[0]["data"].split(",")[-1]):
            message = "maybe needs update"
        else:
            message = "up to date"
    print(f"{row['wlabel']: <40} "
          f"{row['wth term']: <40} "
          f"https://oeis.org/search?q={','.join(map(str, search_terms)): <40}"
          f"{message: <20}"
          f"{', '.join(map(str, subsequence)): <40}")

