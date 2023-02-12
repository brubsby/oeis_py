import requests
import gmpy2


ENDPOINT = "http://factordb.com/api"


class FactorDB():
    def __init__(self, n):
        self.n = n
        self.result = None

    def connect(self, reconnect=False):
        if self.result and not reconnect:
            return self.result
        self.result = requests.get(ENDPOINT, params={"query": str(self.n)})
        return self.result

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

    def is_prime(self, include_probably_prime=False):
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
        return [y for x in ml for y in x]