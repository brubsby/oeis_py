import requests
import logging


logger = logging.getLogger("oeis_query")


def get_url_for_subsequence_query(subsequence):
    return f"https://oeis.org/search?fmt=json&q={','.join(map(str, subsequence))}"


# query the oeis for a subsequence, as if searching for a sequence in the search bar, and return the json result
def query_sequences_from_subsequence(subsequence):
    response = requests.get(get_url_for_subsequence_query(subsequence))
    if not response.ok:
        raise f"oeis response status code was {response.status_code}"
    return response.json()['results']


if __name__ == '__main__':
    print(query_sequences_from_subsequence([3, 6, 8, 15, 17, 29]))

