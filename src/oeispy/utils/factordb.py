import concurrent.futures.thread
import logging
import math
import time
import json
import os
from lxml import html

import gmpy2
import requests

from oeispy.utils import config

REPORT_ENDPOINT = "http://factordb.com/report.php"
ENDPOINT = "http://factordb.com/api"
SEQUENCE_ENDPOINT = "https://factordb.com/sequences.php"
ELF_ENDPOINT = "https://factordb.com/elf.php"
_session = None
logger = logging.getLogger("factordb")


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
            self.result.json()
        except (requests.exceptions.ConnectionError, requests.exceptions.JSONDecodeError, json.decoder.JSONDecodeError) as e:
            logger.error(e)
            time.sleep(sleep)
            return self.connect(True, sleep * 2)
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

    def get_factor_dict(self):
        """
        get_factors: [['2', 3], ['3', 2]]
        Returns: [[mpz(2), 3], [mpz(3), 2]]
        """
        factors = self.get_factor_from_api()
        if not factors:
            return None
        return dict((gmpy2.mpz(x), y) for x, y in factors)


class ReportThreadPool:
    """
    We don't necessarily care what the report has to say, just that it happens, so why not have a queue
    and move on with our lives
    """

    def __init__(self, max_workers=5):
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        self.future_pool = []

    def __del__(self):
        self.executor.shutdown()

    def _report(self, composite_to_factors_dict, sleep=1):
        payload = {
            "report": "\n".join([f"{int(composite)}={list(map(int, factors))}" for composite, factors in
                                 composite_to_factors_dict.items()]),
            "format": "0"
        }
        try:
            response = _get_session().get(REPORT_ENDPOINT, params=payload)
            return response
        except Exception as e:
            logger.error(e)
            time.sleep(sleep)
            return report(composite_to_factors_dict, sleep=sleep * 2)

    def report(self, composite_to_factors_dict, sleep=1):
        if len(self.future_pool) >= self.max_workers:
            concurrent.futures.wait((self.future_pool[0],))
            del self.future_pool[0]
        future = self.executor.submit(self._report, self, composite_to_factors_dict, sleep)
        self.future_pool.append(future)


def report(composite_to_factors_dict, sleep=1):
    payload = {
        "report": "\n".join([f"{int(composite)}={list(map(int, factors))}" for composite, factors in composite_to_factors_dict.items()]),
        "format": "0"
    }
    try:
        response = _get_session().get(REPORT_ENDPOINT, params=payload)
        return response
    except Exception as e:
        logger.error(e)
        time.sleep(sleep)
        return report(composite_to_factors_dict, sleep=sleep*2)


def get_latest_aliquot_term(n, sleep=1):
    payload = {
        "se": "1",
        "action": "last",
        "aq": str(n),
    }
    try:
        response = _get_session().get(SEQUENCE_ENDPOINT, params=payload)
        response.raise_for_status()
        tree = html.fromstring(response.text)
        latest_composite_href = tree.xpath("/html/body/table[2]/tr[2]/td[4]/a[1]/@href")
        href = latest_composite_href[0] if latest_composite_href else None
        latest_composite_index = tree.xpath("/html/body/table[2]/tr[2]/td[2]/text()")
        index = int(latest_composite_index[0]) if latest_composite_index else None
        if href:
            id = href.split("=")[1]
            fdb = FactorDB(id, is_id=True)
            fdb.connect()
            return fdb, index
        raise "Couldn't get latest composite"
    except Exception as e:
        logger.error(e)
        time.sleep(sleep)
        return get_latest_aliquot_term(n, sleep=sleep * 2)


def download_elf_for_seq(n, sleep=1):
    payload = {
        "seq": n,
        "type": 1,
    }
    try:
        response = _get_session().get(ELF_ENDPOINT, params=payload)
        response.raise_for_status()
        elf_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "elf", f"{int(n)}.elf")
        content = response.content
        if not content.startswith(b"0"):
            raise ConnectionError("wrong elf downloaded")
        with open(elf_path, 'wb') as f:
            f.write(response.content)
    except Exception as e:
        logger.error(e)
        time.sleep(sleep)
        return download_elf_for_seq(n, sleep=sleep * 2)
    if not os.path.exists(elf_path):
        raise "couldn't find .elf file we supposedly just downloaded"
    # TODO error if improper format?


if __name__ == "__main__":
    print(get_latest_aliquot_term(4391946))