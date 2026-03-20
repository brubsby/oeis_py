import argparse
import logging
import os
import signal
import sys
import time

import requests

interrupt_level = 0


def fmt_seconds(s: float) -> str:
    """Format a duration in seconds as 01d03h35m50s, dropping leading zero units.
    Handles negative values with a leading '-'.
    """
    negative = s < 0
    s = abs(int(s))
    d, s = divmod(s, 86400)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    parts = []
    started = False
    for val, suffix in ((d, "d"), (h, "h"), (m, "m")):
        if val or started:
            parts.append(f"{val:02d}{suffix}")
            started = True
    parts.append(f"{s:02d}s")
    result = "".join(parts)
    return f"-{result}" if negative else result


def setup_logging(verbose: int):
    loglevel = logging.WARNING
    if verbose > 0:
        loglevel = logging.INFO
    if verbose > 1:
        loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel, format="%(message)s")


def setup_signal_handlers(loop):
    def handle_signal(signame):
        global interrupt_level
        interrupt_level += 1
        print(f"\nReceived {signame}. Interrupt level: {interrupt_level}", file=sys.stderr)
        if interrupt_level >= 3:
            sys.exit(1)

    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame), lambda signame=signame: handle_signal(signame))


def add_common_args(parser: argparse.ArgumentParser):
    """Add args shared by all worker types: --server, --name, -v."""
    parser.add_argument("--server", type=str, default="http://localhost:5000", help="URL of the OEISFactor server")
    parser.add_argument("--name", type=str, required=True, help="Unique name for this worker")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="verbosity (-v, -vv, etc)")


def register_worker(server: str, name: str, worker_type: str, extra_info: str = ""):
    """Register with the server, printing confirmation or exiting on failure."""
    try:
        resp = requests.post(f"{server}/api/worker/register", json={"name": name, "type": worker_type})
        resp.raise_for_status()
        suffix = f" {extra_info}" if extra_info else ""
        print(f"Registered worker '{name}' with server {server}{suffix}")
    except Exception as e:
        print(f"Failed to register with server: {e}", file=sys.stderr)
        sys.exit(1)


def log_big_hit(factor_str: str, composite, b1: int, tag: str,
                context: str = None, extra_fields: dict = None) -> str | None:
    """Write a log file for factors >= 60 digits. Returns the log path, or None if too small."""
    if len(factor_str) < 60:
        return None
    os.makedirs("data/logs/hits", exist_ok=True)
    log_path = os.path.join("data/logs/hits", f"hit_{tag}_{int(time.time())}_{factor_str[:10]}.log")
    with open(log_path, "w") as lf:
        lf.write(f"Timestamp: {time.time()}\n")
        lf.write(f"Composite: {composite}\n")
        lf.write(f"Factor: {factor_str}\n")
        lf.write(f"Length: {len(factor_str)} digits\n")
        lf.write(f"B1: {b1}\n")
        if context:
            lf.write(f"Context: {context}\n")
        if extra_fields:
            for k, v in extra_fields.items():
                lf.write(f"{k}: {v}\n")
    print(f"\n\n********** BIG HIT ({tag.upper()}): C{len(factor_str)} logged to {log_path} **********\n\n", file=sys.stderr)
    return log_path


def submit_factors(server: str, name: str, composite, factors: list):
    """POST factors to the server. factors is a list of ints."""
    try:
        f_resp = requests.post(f"{server}/api/submit/factor", json={
            "client_name": name,
            "composite": int(composite),
            "factors": factors,
        })
        f_resp.raise_for_status()
        print("Factors successfully reported to server!", file=sys.stderr)
    except Exception as e:
        print(f"Failed to submit factors: {e}", file=sys.stderr)
