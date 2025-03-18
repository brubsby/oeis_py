import math
import sys
import time
from lxml import html

import gmpy2
import requests

from modules import config

REPORT_ENDPOINT = "http://factordb.com/report.php"
ENDPOINT = "http://factordb.com/api"
SEQUENCE_ENDPOINT = f"https://factordb.com/sequences.php"
_session = None


def _get_session():
    global _session
    if _session is None:
        _session = requests.Session()

        cookie = config.get_factordb_cookie()
        if cookie:
            _session.cookies.set("fdbuser", cookie)
    return _session


class FactorDB():
    def __init__(self, val, is_id=False):
        self.n = None
        self.id = None
        if not is_id:
            self.n = val
        else:
            self.id = val
        self.result = None


    def connect(self, reconnect=False, sleep=1):
        if self.result and not reconnect:
            return self.result
        try:
            self.result = _get_session().get(ENDPOINT, params={"query": str(self.n)} if self.n else {"id": str(self.id)})
        except requests.exceptions.ConnectionError:
            time.sleep(sleep)
            return self.connect(reconnect, sleep * 2)
        return self.result

    def requery(self):
        return self.connect(reconnect=True)

    def get_json(self):
        if self.result:
            return self.result.json()
        return None

    def get_value(self):
        if self.result:
            if not self.n:
                self.n = math.prod(self.get_factor_list())
            return self.n
        return None

    def get_id(self):
        if self.result:
            if not self.id:
                self.id = self.result.json().get("id")
            return self.id
        return None

    def get_status(self):
        if self.result:
            return self.result.json().get("status")
        return None

    def get_factor_from_api(self):
        if self.result:
            return self.result.json().get("factors")
        return None

    def is_prime(self, include_probably_prime=True):
        if self.result:
            status = self.result.json().get("status")
            return status == 'P' or (status == 'PRP' and include_probably_prime)
        return None

    def get_factor_list(self):
        """
        get_factors: [['2', 3], ['3', 2]]
        Returns: [2, 2, 2, 3, 3]
        """
        factors = self.get_factor_from_api()
        if not factors:
            return None
        ml = [[gmpy2.mpz(x)] * y for x, y in factors]
        return sorted([y for x in ml for y in x])



def report(composite_to_factors_dict, sleep=1):
    payload = {
        "report": "\n".join([f"{int(composite)}={list(map(int, factors))}" for composite, factors in composite_to_factors_dict.items()]),
        "format": "0"
    }
    try:
        response = _get_session().get(REPORT_ENDPOINT, params=payload)
        return response
    except Exception as e:
        print(e, file=sys.stderr)
        time.sleep(sleep)
        return report(composite_to_factors_dict, sleep=sleep*2)


def get_latest_aliquot_term(composite, sleep=1):
    payload = {
        "se": "1",
        "action": "last",
        "aq": str(composite),
    }
    try:
        response = _get_session().get(SEQUENCE_ENDPOINT, params=payload)
        response.raise_for_status()
    except Exception as e:
        print(e, file=sys.stderr)
        time.sleep(sleep)
        return get_latest_aliquot_term(composite, sleep=sleep * 2)
    if response and response.ok:
        tree = html.fromstring(response.text)
        elements = tree.xpath("/html/body/table[2]/tr[2]/td[4]/a[1]/@href")
        href = elements[0] if elements else None
        if href:
            id = href.split("=")[1]
            fdb = FactorDB(id, is_id=True)
            fdb.connect()
            return fdb
    raise "Couldn't get latest composite"


if __name__ == "__main__":
    print(get_latest_aliquot_term(4391946))