import asyncio
import itertools
import json
import time

from modules import factordb
import aiohttp
import aiohttp_retry
import threading
import random


ENDPOINT = "http://factordb.com/api"
NO_RETRY_CODES = {200, 500, 501}
RETRY_CODES = set(filter(lambda x: x not in NO_RETRY_CODES, range(100, 600)))
RETRY_EXCEPTIONS = {aiohttp.client_exceptions.ServerDisconnectedError, asyncio.TimeoutError}
LIMIT_PER_HOST = 6
RETRY_ATTEMPTS = 9999


async def evaluate_response_callback(response):
    try:
        await response.json(content_type=None)
        return True
    except json.decoder.JSONDecodeError:
        return False


async def async_single_factordb(session, query):
    async with session.get(ENDPOINT, params={"query": str(query)}) as response:
        return query, await response.json(content_type=None)


async def async_batch_factordb(composites, ordered=True):
        tasks = []
        retvals = {}
        connector = aiohttp.TCPConnector(limit_per_host=LIMIT_PER_HOST)
        async with aiohttp_retry.RetryClient(
                connector=connector,
                # timeout=None,
                retry_options=aiohttp_retry.ExponentialRetry(
                    attempts=RETRY_ATTEMPTS,
                    statuses=RETRY_CODES,
                    exceptions=RETRY_EXCEPTIONS,
                    evaluate_response_callback=evaluate_response_callback)) as client_session:
            try:
                queries = []
                for query in composites:
                    queries.append(query)
                    tasks.append(async_single_factordb(client_session, query))
                if ordered:
                    i = 0
                    for val in asyncio.as_completed(tasks):
                        key, val = await val
                        retvals[key] = val
                        while queries[i] in retvals:
                            retval = retvals[queries[i]]
                            if retval:
                                retval["val"] = queries[i]
                            yield retval
                            i += 1
                            if i >= len(queries):
                                break
                        if i >= len(queries):
                            break
                else:
                    for val in asyncio.as_completed(tasks):
                        key, val = await val
                        val["val"] = key
                        yield val
            except GeneratorExit:
                return



class FactorDBResult():

    def __init__(self, result_json):
        self.result = result_json

    def requery(self):
        f = factordb.FactorDB(self.get_val())
        f.connect()
        self.result = f.get_json()
        return self.result

    def get_val(self):
        if self.result:
            return self.result.get("val")
        return None

    def get_id(self):
        if self.result:
            return self.result.get("id")
        return None

    def get_status(self):
        if self.result:
            return self.result.get("status")
        return None

    def get_factor_from_api(self):
        if self.result:
            return self.result.get("factors")
        return None

    def is_prime(self, include_probably_prime=True):
        if self.result:
            status = self.result.get("status")
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
        ml = [[int(x)] * y for x, y in factors]
        return sorted([y for x in ml for y in x])


def batch_factordb(queries, ordered=True):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    try:
        async_gen = async_batch_factordb(queries, ordered=ordered)
        while True:
            yield FactorDBResult(loop.run_until_complete(async_gen.__anext__()))
    except (StopAsyncIteration, GeneratorExit):
        return


def serial_factordb_batch(queries):
    for query in queries:
        f = factordb.FactorDB(query)
        factordb_json = f.connect().json()
        factordb_json['val'] = query
        yield FactorDBResult(factordb_json)


if __name__ == "__main__":
    start = time.time()
    for resp in batch_factordb([random.randrange(1000000000000000000000, 1000000000000000000000000000000) for i in range(100)]):
        print(resp.get_val(), resp.get_factor_list(), resp.get_status())
    print(f"trial 1 = {time.time() - start}")
    # start = time.time()
    # for resp in serial_factordb_batch([random.randrange(100000, 100000000000) for i in range(20)]):
    #     print(resp)
    # print(f"trial 2 = {time.time() - start}")