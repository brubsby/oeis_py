import requests
import csv


# return a list of dicts from parsing kamada's prime_difficulty.txt
def read_prime_difficulty_txt():
    url = "https://stdkmd.net/nrr/prime/prime_difficulty.txt"
    response = requests.get(url)
    content = response.content.decode('utf-8')
    lines = filter(lambda row: len(row) > 0 and row[0] != '#',
                   map(lambda row: '|'.join(map(lambda part: part.strip(), row.split('|'))),
                       content.splitlines()))
    return csv.DictReader(lines, delimiter='|')

