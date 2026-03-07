import argparse
import copy
import logging
import os
import queue
import re
import subprocess
import threading
import time
import uuid
from datetime import datetime
from argparse import Namespace
import t_level

import gmpy2

from modules import config


def positive_integer(arg):
    val = int(arg)
    if val < 1:
        raise ValueError(f"{arg} not a positive integer")
    return val


def nonnegative_integer(arg):
    val = int(arg)
    if val < 0:
        raise ValueError(f"{arg} not a non-negative integer")
    return val


def sci_int(x):
    if x is None or type(x) in [int, gmpy2.mpz]:
        return x
    if type(x) != str:
        raise TypeError(f"sci_int needs a string input, instead of {type(x)} {x}")
    if x.isnumeric():
        return int(x)
    match = re.match(r"^(\d+)(?:e|[x*]10\^)(\d+)$", x)
    if not match:
        raise ValueError(f"malformed intger string {x}, could not parse into an integer")
    return gmpy2.mpz(match.group(1)) * pow(10, gmpy2.mpz(match.group(2)))


logger = logging.getLogger("ecm")
logger.setLevel(logging.DEBUG)


def string_array_to_string(str_array):
    str = ''
    sep = ''
    for s in str_array:
        str += sep
        str += s
        if not sep:
            sep = ' '
    return str


class _EcmWorkUnit:
    """Holds parameters defining a work unit (number of curves, B1, etc.)"""

    def __init__(self, args, curves, B1, B2, B2min, id, fully_factored_event):
        self.args = args  # command line arguments
        self.curves = curves  # number of curves to run
        self.B1 = B1
        self.B2 = B2
        self.B2min = B2min
        self.id = id
        self.fully_factored_event = fully_factored_event
        self.return_code = -1
        self.factor_found = False
        self.found_factors = []
        self.output_file_path = args.output_path + \
                                '-ecmx.{0:s}.out'.format(id)
        self.processed = False
        self.thread_id = 0
        # Note: my_curves_done doesn't have to be protected from
        # concurrent access because work units are not shared
        # between workers and the number of curves done from
        # each work unit is only ever read at the end when
        # the workers are done.
        self.my_curves_done = 0

    def inc_curves_done(self):
        """Increments the number of curves done by one."""

        self.my_curves_done = self.my_curves_done + 1

    def curves_done(self):
        """Returns the number of curves performed"""

        return self.my_curves_done


class _EcmWorker:
    """Class defining worker threads

    Once method start is called on an instance of this class
    it keeps consuming work units from the work queue and running
    their processing until there is no more work or the number
    is fully factored.
    """

    id_seq = 1  # sequence for thread ids

    def __init__(self, work_queue, no_more_work_event, fully_factored_event, id, timer):
        self.work_queue = work_queue
        self.no_more_work_event = no_more_work_event
        self.fully_factored_event = fully_factored_event
        self.thread = threading.Thread(target=self.work, args=())
        self.id = id
        self.id_seq = self.id_seq + 1
        self.timer = timer
        self.lastCurveDuration = 0
        # GMP-ECM output parsing stuff
        self.lastCurveOutput = ''
        self.lastCurveOutputPrefix = ''
        self.outputLastCurveIndic = -1
        self.gmpEcmOutputHasTimestamp = False
        self.stepDurationPattern = re.compile('Step (?:1|2) took (\d+)ms')


    def work(self):
        """Loops getting work units from the queue and running their processing"""

        while True:
            try:
                work_unit = self.work_queue.get_nowait()
                work_unit.thread_id = self.id
                self.do_run_ecm(work_unit)
            except queue.Empty:
                if (self.no_more_work_event.is_set()
                        or self.fully_factored_event.is_set()):
                    break
                time.sleep(1)
                continue


    def start(self):
        self.thread.start()


    def join(self):
        self.thread.join()


    def build_gmp_ecm_cmd_line(self, work_unit):
        """Returns GMP-ECM command line for a given work unit"""

        args = work_unit.args
        cmd = []
        cmd.append(args.ecm_path)
        if not args.quiet:
            cmd.append('-v')
            cmd.append('-timestamp')
        if args.nice:
            cmd.append('-n')
        if args.very_nice:
            cmd.append('-nn')
        if args.parametrization is not None:
            cmd.append('-param')
            cmd.append(f'{args.parametrization}')
        if args.input_file:
            cmd.append('-inp')
            cmd.append(f'{args.input_file}')
        if args.max_memory:
            cmd.append('-maxmem')
            cmd.append(f'{args.max_memory}')
        if args.stage2_steps:
            cmd.append('-k')
            cmd.append(str(args.stage2_steps))
        cmd.append('-c')
        cmd.append(f'{work_unit.curves}')
        cmd.append(f'{work_unit.B1}')
        if work_unit.B2:
            if work_unit.B2min:
                cmd.append(f'{work_unit.B2min}-{work_unit.B2}')
            else:
                cmd.append(f'{work_unit.B2}')

        return cmd


    def do_run_ecm(self, work_unit):
        """Processes a work unit"""

        # don't bother running a work unit if the number is fully factored
        if work_unit.fully_factored_event.is_set():
            return
        cmd = self.build_gmp_ecm_cmd_line(work_unit)
        output_file_path = work_unit.output_file_path
        with open(output_file_path, 'ab') as output_f, open(output_file_path, 'r') as output_r:
            # Reader has to ignore any previous file content
            output_r.seek(0, os.SEEK_END)
            logger.info(f'Running {work_unit.curves} curves at {work_unit.B1} (thread {work_unit.thread_id})...')
            proc = subprocess.Popen(cmd, bufsize=0, stdout=output_f, stderr=output_f)
            self.timer.on_work_unit_started(work_unit)
            logger.debug('[pid: {0:d}] '.format(proc.pid) + string_array_to_string(cmd)
                         + ' > {0:s} 2>&1'.format(output_file_path))
            haveToLeave = False
            self.clear_parsing_data()

            while True:
                if proc.poll() is not None:
                    work_unit.return_code = proc.returncode
                    # Bit 3 is set when cofactor is PRP, return code is 8 when
                    # the input number itself is found as factor
                    if (work_unit.return_code & 8) and (work_unit.return_code != 8):
                        logger.info('A factor has been found (thread {0:d}), the cofactor is PRP!'.format(self.id))
                        logger.debug('Factor found by [pid:{0:d}], cofactor is PRP.'.format(proc.pid))
                        work_unit.fully_factored_event.set()
                        work_unit.factor_found = True
                    elif work_unit.return_code & 2:
                        logger.info('A factor has been found (thread {0:d})!'.format(self.id))
                        logger.debug('Factor found by [pid:{0:d}].'.format(proc.pid))
                        work_unit.factor_found = True
                    haveToLeave = True
                else:
                    if work_unit.fully_factored_event.is_set():
                        proc.kill()
                        haveToLeave = True
                self.parse_gmp_ecm_output(work_unit, output_r)
                if haveToLeave:
                    break
                time.sleep(2)

            logger.debug(f'Work unit {work_unit.id} processed.')
            logger.info(f'Work unit {work_unit.id} found factor(s): {work_unit.found_factors}')
            work_unit.processed = True


    def clear_parsing_data(self):
        """Resets GMP-ECM output parsing data"""

        self.lastCurveOutput = ''
        self.lastCurveOutputPrefix = ''
        self.outputLastCurveIndic = -1
        self.gmpEcmOutputHasTimestamp = False


    def parse_gmp_ecm_output(self, work_unit, output_r):
        """"Parses" GMP-ECM's output to extract needed information

        Lines of interest are the following ones:
          - 'GMP-ECM <version number> ...' => first line printed by GMP-ECM, has
            to be added to the prefix
          - '[Sat Jan 16 ...]' => timestamp indicating that a new curve is being done
          - 'Using B1=...' => in case the timestamp is not present this indicates start
            of a new curve
          - 'Input number is <number>' => has to be added to the prefix
          - 'Running on <machine name>' => has to be added to the prefix
          - 'Step 1 took' => we want the duration in milliseconds just after that
          - 'Step 2 took ' => indicates curve done (won't be there if a factor is found
            in step 1) + same as step 1.
          - '********** Factor found in step 1' => indicates curve done
        When a factor is found we have to print GMP-ECM's output regarding last curve
        and when doing so don't forget the last two lines:
          ********** Factor found in step ....
          Found ....                                               # this one...
          <Composite|Probable prime> cofactor ... has x digits     # and this one
        """

        for line in output_r:
            if line.startswith('GMP-ECM '):
                self.lastCurveOutputPrefix = line
                self.lastCurveOutput = ''
                continue
            if line.startswith(('Running on', 'Input number')):
                self.lastCurveOutputPrefix = self.lastCurveOutputPrefix + line
                continue
            if line.startswith('['):
                self.lastCurveOutput = line
                self.gmpEcmOutputHasTimestamp = True
                continue
            if line.startswith('Using B1='):
                if not self.gmpEcmOutputHasTimestamp:
                    self.lastCurveOutput = ''
                self.gmpEcmOutputHasTimestamp = False
                self.lastCurveDuration = 0
            if line.startswith(('Step 1 took ', 'Step 2 took ')):
                match = self.stepDurationPattern.match(line)
                if match:
                    self.lastCurveDuration = self.lastCurveDuration + int(match.group(1)) / 1000
            if line.startswith(('Step 2 took ', '********** Factor found in step 1')):
                self.timer.curve_done(work_unit.B1, self.lastCurveDuration)
                work_unit.inc_curves_done()
            if line.startswith('********** Factor found'):
                self.outputLastCurveIndic = 0
                match = re.search(r"\d{2,}", line)
                work_unit.found_factors.append(int(match.group(0)))
            self.lastCurveOutput = self.lastCurveOutput + line
            if self.outputLastCurveIndic >= 0:
                self.outputLastCurveIndic = self.outputLastCurveIndic + 1
            if self.outputLastCurveIndic == 3:
                logger.info('GMP-ECM output (thread {0:d}):\n\n'.format(self.id)
                            + self.lastCurveOutputPrefix + self.lastCurveOutput)
                self.outputLastCurveIndic = -1



class _Timer:
    """Timer class, outputs progress, elapsed time, average curve duration, etc."""


    def __init__(self, work_units, seconds_between_output, start_t=0):
        self.time_table = dict(dict())
        self.time_table_lck = threading.Lock()
        for wk in work_units:
            self.time_table[wk.B1] = {'curvesDone': 0,
                                      'avgCurveDurationInSeconds': 0.0,
                                      'curves': (self.time_table[wk.B1]['curves'] + wk.curves) if (
                                                  wk.B1 in self.time_table) else wk.curves,
                                      'isStarted': False,
                                      'startTime': datetime.min,
                                      'Done': False}
        self.thread = threading.Thread(target=self.work, args=())
        self.end_event = threading.Event()
        self.seconds_between_output = seconds_between_output
        self.start_t = start_t
        self.work_string = t_level.get_t_level_curves_string(self.start_t)


    def work(self):
        logger.debug('Starting timer...')
        lastOuputTime = datetime.now()
        while True:
            with self.time_table_lck:
                for B1, B1Info in self.time_table.items():
                    if B1Info['Done']:
                        continue
                    if not B1Info['isStarted']:
                        continue
                    now = datetime.now()
                    startT = B1Info['startTime']
                    deltaT = now - startT
                    curvesDone = B1Info['curvesDone']
                    curves = B1Info['curves']
                    if curvesDone:
                        curveString = f'{self.work_string};{B1Info["curvesDone"]}@{B1}'
                        logger.info(f"{B1Info['curvesDone']} curve(s) completed @ B1={B1} out of {B1Info['curves']} (Elapsed time: {str(deltaT).split('.')[0]},"
                                    f" avg curve duration: {B1Info['avgCurveDurationInSeconds']:.2f}s, ETA: {str((curves / curvesDone - 1) * deltaT).split('.')[0]})"
                                    f" t-level: {t_level.string_to_t_level(curveString):.2f}")
                        lastOuputTime = datetime.now()
                    if curvesDone == curves:
                        B1Info['Done'] = True
            while (datetime.now() - lastOuputTime).total_seconds() < self.seconds_between_output:
                if self.end_event.is_set():
                    return
                time.sleep(2)


    def curve_done(self, B1, curveDurationSeconds):
        """Informs the timer that a curve has been completed at the given B1"""

        with self.time_table_lck:
            tableEntry = self.time_table[B1]
            assert tableEntry['isStarted']
            curvesDoneBefore = tableEntry['curvesDone']
            tableEntry['curvesDone'] = tableEntry['curvesDone'] + 1
            tableEntry['avgCurveDurationInSeconds'] = (curvesDoneBefore * tableEntry['avgCurveDurationInSeconds']
                                                       + curveDurationSeconds) / (curvesDoneBefore + 1)


    def on_work_unit_started(self, work_unit):
        """Informs the timer that the processing of a work unit has started"""

        with self.time_table_lck:
            tableEntry = self.time_table[work_unit.B1]
            if not tableEntry['isStarted']:
                tableEntry['isStarted'] = True
                tableEntry['startTime'] = datetime.now()


    def start(self):
        self.thread.start()


    def end(self):
        self.end_event.set()


def _create_workers(count, work_queue, no_more_work_event, fully_factored_event, timer):
    workers = []
    id = 1
    for i in range(count):
        worker = _EcmWorker(work_queue, no_more_work_event, fully_factored_event, id, timer)
        workers.append(worker)
        worker.start()
        id = id + 1
    return workers


def _create_work_units(args, work_units, fully_factored_event):
    file_index = 0
    curves = args.curves
    b1 = args.b1
    b2 = args.b2
    b2min = args.b2min
    ct = int(curves / args.threads)
    rc = curves - args.threads * ct
    worker_c = 0
    while (worker_c < args.threads):
        curvz = ct + (1 if (worker_c < rc) else 0)
        if (not curvz):
            break
        id = '{0:d}_{1:d}'.format(file_index, worker_c)
        work_unit = _EcmWorkUnit(args, curvz, b1, b2, b2min, id, fully_factored_event)
        work_units.append(work_unit)
        worker_c += 1
    file_index += 1


def _enqueue_work_units(work_queue, work_units, fully_factored_event):
    for work_unit in work_units:
        if fully_factored_event.is_set():
            return
        logger.debug(f'Queueing {work_unit.curves} curves @ B1={work_unit.B1}')
        work_queue.put(work_unit)


def _run_ecm(args):
    work_queue = queue.Queue(args.threads)
    no_more_work_event = threading.Event()
    work_units = []
    found_factors = set()
    dirpath = None
    if not args.output_path:
        # if output path isn't specified, make a temp-dir
        this_uuid = uuid.uuid4()
        dirpath = os.path.join("..", "data", "temp", str(this_uuid))
        os.makedirs(dirpath, exist_ok=True)
        args.output_path = os.path.join(dirpath, "ecm.out")
    if not args.delta_progress:
        args.delta_progress = 600
    if not args.ecm_path:
        args.ecm_path = config.get_ecm_path() or "ecm"
    if not args.input_file:
        if not dirpath:
            this_uuid = uuid.uuid4()
            dirpath = os.path.join("..", "data", "temp", str(this_uuid))
            os.makedirs(dirpath, exist_ok=True)
        args.input_file = os.path.join(dirpath, "ecm.in")
        if args.factor:
            with open(args.input_file, 'w') as input_file:
                input_file.write(f'{args.factor}\n')
    with open(args.output_path, 'ab') as output_file:
        fully_factored_event = threading.Event()
        _create_work_units(args, work_units, fully_factored_event)
        timer = _Timer(work_units, args.delta_progress, start_t=args.start_t)
        workers = _create_workers(args.threads, work_queue, no_more_work_event, fully_factored_event, timer)
        timer.start()
        # Enqueue the created work units
        _enqueue_work_units(work_queue, work_units, fully_factored_event)
        no_more_work_event.set()
        for worker in workers:
            worker.join()
        timer.end()
        if fully_factored_event.is_set():
            logger.info('Number is fully factored!!')
        for work_unit in work_units:
            if work_unit.processed:
                found_factors.update(work_unit.found_factors)
                with open(work_unit.output_file_path, 'rb') as worker_output_file:
                    for line in worker_output_file:
                        output_file.write(line)
                os.remove(work_unit.output_file_path)

    results = dict()
    for wk in work_units:
        results[wk.B1] = results[wk.B1] + wk.curves_done() if (wk.B1 in results) else wk.curves_done()
    for b1, c in results.items():
        logger.info(f'Ran {c} curves @ B1={b1}')
    if dirpath:
        os.remove(args.output_path)
        os.remove(args.input_file)
        os.removedirs(dirpath)
    return found_factors


class ArgStub(object):
    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return None


def ecm(number, b1, curves=1, threads=1, b2=None, b2min=None, param=None, k=None, start_t=0):
    args = ArgStub()
    args.factor = number
    args.curves = curves
    args.threads = threads
    args.b1 = b1
    args.b2 = b2
    args.b2min = b2min
    args.param = param
    args.k = k
    args.start_t = start_t
    return _run_ecm(args)


if __name__ == "__main__":
    cmd_line_parser = argparse.ArgumentParser()
    cmd_line_parser.add_argument('-v', '--verbosity', action='count',
                                 default=0,
                                 help='Increase verbosity level.')
    cmd_line_parser.add_argument('-t', '--threads', type=positive_integer, default=1,
                                 help='Number of threads.')
    cmd_line_parser.add_argument('-d', '--delta_progress', required=False, type=positive_integer,
                                 default=600,  # ten minutes
                                 help='The number of seconds between progress outputs.')
    cmd_line_parser.add_argument('-q', '--quiet', required=False, action='store_true',
                                 help='Make GMP-ECM less verbose.')
    cmd_line_parser.add_argument('-maxmem', '--max_memory',
                                 help='Maximum memory usage per thread.')
    cmd_line_parser.add_argument('-k', '--stage2_steps', type=positive_integer, required=False,
                                 help='Number of steps to perform in stage 2.')
    cmd_line_parser.add_argument('-n', '--nice', required=False, action='store_true',
                                 help='Run ecm in "nice" mode (below normal priority).')
    cmd_line_parser.add_argument('-nn', '--very_nice', required=False, action='store_true',
                                 help='Run ecm in "very nice" mode (idle priority).')
    cmd_line_parser.add_argument('-param', '--parametrization', required=False, type=int,
                                 help='Which parametrization should be used (option is sent as is to GMP-ECM).')
    cmd_line_parser.add_argument('-o', '--output_path',
                                 help='Output file path.')
    cmd_line_parser.add_argument('-s', '--save',
                                 help='Stage-1 save file path.')
    cmd_line_parser.add_argument('-e', '--ecm_path',
                                 help='Path of ecm executable.')
    cmd_line_parser.add_argument('-c', '--curves', type=positive_integer, default=1,
                                 help='Number of curves to run at given parameters')
    cmd_line_parser.add_argument('-b1', required=True, type=sci_int,
                                 help='What value of B1 should be used for the curves')
    cmd_line_parser.add_argument('-b2', type=sci_int,
                                 help='What value of B2 should be used for the curves, default is gmp-ecm default')
    cmd_line_parser.add_argument('-b2min', type=sci_int,
                                 help='What value of B2min should be used for the curves, default is B1')
    input_group = cmd_line_parser.add_mutually_exclusive_group()
    input_group.add_argument('-i', '--input_file',
                             help='Input file.')
    input_group.add_argument('-f', '--factor',
                             help='Input number to factor.')
    arguments = cmd_line_parser.parse_args()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if (arguments.verbosity >= 1) else logging.INFO)
    console_handler.setFormatter(logging.Formatter('| %(asctime)s | %(message)s'))
    logger.addHandler(console_handler)

    print(_run_ecm(arguments))
