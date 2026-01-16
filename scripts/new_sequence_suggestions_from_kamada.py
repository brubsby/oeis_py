from oeispy.utils.kamada_prime_difficulty import read_prime_difficulty_txt
from oeispy.utils.oeis_query import query_sequences_from_subsequence


# for each entry in kamada's prime_difficulty.txt, search a subsequence of the found primes for oeis existence
rows = []
for row in read_prime_difficulty_txt():
    # skip forms with 0 or 1 primes
    if "(" in row['(probable) prime numbers']:
        continue
    if row["oeis"]:
        continue
    rows.append(row)

for row in sorted(rows, key=lambda row: chr(len(row['wlabel'])+65)+row['wlabel']):
    print(f"{row['wlabel']: <20} "
          f"{row['range']: <10} "
          f"https://oeis.org/search?q={row['(probable) prime numbers'][2:]}")

