import sqlite3
import platformdirs
import os
import json
import logging
import requests
import gmpy2
import sympy
import time
from pathlib import Path

# Try to import factor_cache
try:
    from sympy import factor_cache
except ImportError:
    try:
        from sympy.ntheory.factor_ import factor_cache
    except ImportError:
        factor_cache = None

APP_NAME = "oeisexpr"
APP_AUTHOR = "oeisexpr"

FACTORDB_ENDPOINT = "http://factordb.com/api"

def get_db_path():
    user_data_dir = platformdirs.user_data_dir(APP_NAME, APP_AUTHOR)
    os.makedirs(user_data_dir, exist_ok=True)
    return Path(user_data_dir) / "factordb_cache.db"

def get_connection():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS factors (
            n TEXT PRIMARY KEY,
            factors_json TEXT,
            status TEXT
        )
    """)
    conn.commit()
    return conn

def get_local_factors(n):
    """
    Returns (status, factors_list) if found, else (None, None).
    factors_list is [[p, e], ...]
    """
    n_str = str(n)
    with get_connection() as conn:
        cursor = conn.execute("SELECT status, factors_json FROM factors WHERE n = ?", (n_str,))
        row = cursor.fetchone()
        if row:
            status, factors_json = row
            try:
                factors = json.loads(factors_json)
                logging.debug(f"Cache HIT for {n_str[:20]}...: status={status}")
                return status, factors
            except json.JSONDecodeError:
                pass
    logging.debug(f"Cache MISS for {n_str[:20]}...")
    return None, None

def save_local_factors(n, status, factors):
    """
    factors: [[p, e], ...]
    """
    n_str = str(n)
    factors_json = json.dumps(factors)
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO factors (n, factors_json, status) VALUES (?, ?, ?)",
            (n_str, factors_json, status)
        )
        conn.commit()

def fetch_from_factordb(n):
    """
    Queries factordb.com for factors of n.
    Returns (status, factors) or (None, None) on failure.
    Retries up to 3 times on failure.
    """
    retries = 3
    delay = 1
    
    for attempt in range(retries):
        try:
            logging.info(f"Querying factordb for {n} (attempt {attempt+1}/{retries})...")
            response = requests.get(FACTORDB_ENDPOINT, params={"query": str(n)}, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            status = data.get("status")
            factors_data = data.get("factors") # [['2', 1], ...]
            logging.debug(f"Factordb response for {str(n)[:20]}...: status={status}")
            
            # Convert factors to consistent format
            factors = []
            if factors_data:
                for f_str, exponent in factors_data:
                    factors.append([f_str, exponent])
            
            return status, factors
        except (requests.RequestException, ValueError) as e:
            logging.warning(f"Failed to query factordb for {n}: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                return None, None

def get_factors_from_cache_or_db(n):
    """
    Checks local cache, then factordb for factors of n.
    Returns (status, factors) or (None, None).
    """
    # 1. Check local cache
    status, factors = get_local_factors(n)
    
    # 2. If not found or stale (status "C" or "CF"), fetch from factordb
    if not status or status in ["C", "CF"]:
        new_status, new_factors = fetch_from_factordb(n)
        if new_status:
            status, factors = new_status, new_factors
            save_local_factors(n, status, factors)
            
    return status, factors

def get_external_impl(self, n):
    """
    Hook for sympy.factor_cache.get_external.
    Returns list[int] of factors or None.
    """
    # Optimization: Skip external lookup for numbers SymPy can handle easily.
    # 2^70 is approx 1.18e21. SymPy handles this range reasonably well.
    if n < 2**70:
        return None

    status, factors = get_factors_from_cache_or_db(n)

    # 3. Process result
    if status and factors:
        # Sympy expects a list of integer factors. 
        # If we have [["2", 2], ["3", 1]], we should return [2, 2, 3].
        # Only useful if status indicates we have some factors.
        # Even "CF" (Composite, factors known) is useful.
        # "FF" (Fully Factored) or "P" (Prime) is best.
        
        # If status is "C" (Composite, no factors) or "CF" (Composite, factors known but potentially includes composite residue),
        # we return None to avoid SymPy's strict isprime() check failing on the residue.
        # We only return factors if we are sure they are all prime ("FF" or "P").
        if status not in ["FF", "P"]:
            return None
        
        result_factors = []
        for p_str, e in factors:
            try:
                p = int(p_str)
                result_factors.extend([p] * e)
            except ValueError:
                pass
        
        # Recursion prevention:
        # factor_cache.add(n, factors) validates factors by calling isprime(p).
        # isprime(p) checks factor_cache.get(p).
        # If we return [n] for n, factor_cache tries to validate n is prime by calling isprime(n).
        # isprime(n) calls get_external(n) again -> Loop.
        # So we must NOT return [n] if n is prime. Let SymPy's isprime handle it.
        if len(result_factors) == 1 and result_factors[0] == n:
            return None
        
        if result_factors:
            logging.debug(f"Returning external factors for {n}: {result_factors}")
            return result_factors
            
    return None

def setup_factor_cache():
    if factor_cache is not None:
        import types
        # Bind the method to the instance
        factor_cache.get_external = types.MethodType(get_external_impl, factor_cache)
        logging.info("Enabled external factor lookup via factordb.")
    else:
        logging.warning("Could not enable external factor lookup: factor_cache not found.")

if __name__ == "__main__":
    # Test script
    logging.basicConfig(level=logging.DEBUG)
    print("Testing oeis_factor_cache...")
    
    setup_factor_cache()
    
    # Test with a known number
    test_n = 123456789
    print(f"Factoring {test_n}...")
    print(sympy.factorint(test_n))
    
    # Test with a large prime from factordb (if network works)
    # p = 2^67-1 = 147573952589676412927
    test_p = 147573952589676412927
    print(f"Factoring {test_p}...")
    print(sympy.factorint(test_p))

