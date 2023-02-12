import logging
import os
import inspect
import time
from func_timeout import func_timeout, FunctionTimedOut

# module for storing integers as dat files for search

__file_path = os.path.join("C:\\", "GitProjects", "oeis", "data", "dats")
__last = None
__last_counter = None
__start = None
__start_counter = None
__last_log = 1


def __get_filename():
    return os.path.splitext(os.path.basename(inspect.stack()[3].filename))[0] + ".dat"


def load(filename=None, default=None):
    if not filename:
        filename = os.path.join(__file_path, __get_filename())
    elif not os.path.isabs(filename):
        filename = os.path.join(__file_path, filename)
    if default is not None and not (type(default) is list or type(default) is tuple):
        default = [default]
    start_vals = None
    try:
        with open(filename) as datfile:  # file containing the start points to search
            lines = datfile.readlines()
            if lines:
                start_vals = [int(line) for line in lines]
    except FileNotFoundError:
        pass
    if not start_vals:
        if not default:
            return None
        start_vals = default
    return start_vals if len(start_vals) > 1 else start_vals[0]


def save(vals, filename=None):
    if not (type(vals) is list or type(vals) is tuple):
        vals = [vals]
    if not filename:
        filename = os.path.join(__file_path, __get_filename())
    elif not os.path.isabs(filename):
        filename = os.path.join(__file_path, filename)
    try:
        with open(filename, 'w') as datfile:  # file containing the start points to search
            [datfile.write(f"{str(val)}\n") for val in vals]
    except FunctionTimedOut:
        # if we get interrupted during this, finish writing the file so we don't lose progress
        with open(filename, 'w') as datfile:
            [datfile.write(f"{str(val)}\n") for val in vals]


def delete(filename=None):
    if not filename:
        filename = os.path.join(__file_path, __get_filename())
    elif not os.path.isabs(filename):
        filename = os.path.join(__file_path, filename)
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass


def timing_reset():
    global __start_counter, __last_counter, __last, __start
    __last = None
    __last_counter = None
    __start = None
    __start_counter = None


# counter must be monotonically increasing
def timing(vals, counter, iterations=1, total=False, filename=None, cooldown=5):
    if counter % iterations == 0:
        global __last, __last_counter, __start, __start_counter, __last_log
        now = time.time()
        log_line = ""
        if __last:
            if total:
                if counter <= __start_counter:  # counter probably reset
                    __start_counter = counter
                    return
                rate_per_second = (counter - __start_counter) / ((now - __start) or 0.001)
            else:
                if counter <= __last_counter:  # counter probably reset
                    __last_counter = counter
                    return
                rate_per_second = (counter - __last_counter) / ((now - __last) or 0.001)
            if rate_per_second > 1:
                log_line += f"{rate_per_second:.02f}/s, "
            else:
                log_line += f"{1/(rate_per_second):.01f}s per, "
        else:
            __start = now
            __start_counter = counter
        log_line += f"val(s): {vals}"
        if not cooldown:
            logging.info(log_line)
        elif __last_log and now - __last_log > cooldown:
            logging.info(log_line)
            __last_log = now
        __last = now
        __last_counter = counter
        save(vals, filename)
