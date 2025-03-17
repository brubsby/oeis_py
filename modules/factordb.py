import sys
import time
from modules import config

import requests
import gmpy2


REPORT_ENDPOINT = "http://factordb.com/report.php"
ENDPOINT = "http://factordb.com/api"
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
    def __init__(self, n):
        self.n = n
        self.result = None


    def connect(self, reconnect=False, sleep=1):
        if self.result and not reconnect:
            return self.result
        try:
            self.result = _get_session().get(ENDPOINT, params={"query": str(self.n)})
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

    def get_id(self):
        if self.result:
            return self.result.json().get("id")
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
