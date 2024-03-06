import importlib.util
import math
import sys
import os

import requests


def _get_digits_module(digits):
    assert type(digits) == int
    rounded_digits = min(max(digits // 10, 10), 49)
    rounded_digits_string = f"{rounded_digits}0"
    module_name = f"ecmtimes_{rounded_digits_string}"
    if module_name not in sys.modules:
        spec = importlib.util.spec_from_file_location(module_name, os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ecm_times", module_name + ".py"))
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    else:
        module = sys.modules[module_name]
    return module


def get_ecm_time(digits, b1, curves, threads=1):
    # if digits > 500:
    # extrapolated surface
    try:
        stime = 2.293859206732816e-09 * pow(1.7777651508829972, math.log10(b1) * 5.49548701883304) + 1.953699357838586 * pow(1.0008677880252723, digits * math.log10(b1) * 2.195624509993748)
        return stime * curves / threads
    except OverflowError:
        return float('inf')
    ecm_times = _get_digits_module(digits).ecm_times
    i = 0
    j = 0
    stime = 0.0
    for i in range(len(ecm_times)):
        if ecm_times[i][1] == digits:
            break
    for j in range(2, len(ecm_times[0])):
        if ecm_times[0][j] >= b1:
            break
    if i < len(ecm_times) and j < len(ecm_times[0]):
        times = ecm_times[i][j].split("s+")
        stime = float(times[0]) + float(times[1])
    return stime * curves / threads


def get_ecm_mem(digits, b1):
    ecm_times = _get_digits_module(digits).ecm_times
    i = 0
    j = 0
    smem = 0.0
    for i in range(len(ecm_times)):
        if ecm_times[i][1] == digits:
            break
    for j in range(len(ecm_times[0])):
        if ecm_times[0][j] == b1:
            break
    if i < len(ecm_times) and j < len(ecm_times[0]):
        times = ecm_times[i][j].split("s+")
        smem = float(times[0]) + float(times[1])
    return smem


if __name__ == "__main__":
    for i in range(100, 500, 10):
        this_filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ecmtimes", f"ecmtimes_{i}.py")
        if not os.path.exists(this_filepath):
            request = requests.get(f"http://www.wraithx.net/math/ecmprobs/ecmtimes_{i}.js")
            with open(this_filepath, "w") as module_file:
                module_file.write(request.text)
