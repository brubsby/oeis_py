import argparse
import asyncio
import logging
import os
import re
import shutil
import signal
import sys
import time
import requests
from oeispy.utils import ecmtimes

interrupt_level = 0

def locate_ecm_install():
    install_location = shutil.which("ecm")
    if not install_location:
        print("Could not find ecm binary. Please install GMP-ECM.", file=sys.stderr)
        sys.exit(1)
    return install_location

async def handle_stdin(residues, stdin):
    try:
        for residue in residues:
            stdin.write((residue + "\n").encode('utf-8'))
            await stdin.drain()
        stdin.close()
    except (BrokenPipeError, ConnectionResetError):
        pass
    except Exception as e:
        logging.error(f"Error handling stdin: {e}")

async def read_stdout(proc, proc_index, output_queue):
    try:
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            await output_queue.put((proc_index, line.decode('utf-8', errors='replace').strip()))
    except Exception as e:
        logging.error(f"Error reading stdout: {e}")
    finally:
        await output_queue.put((proc_index, None))  # sentinel: this reader is done

class CPUProc:
    def __init__(self, ecm_path, threads, b1):
        self.ecm_path = ecm_path
        self.threads = threads
        self.b1 = b1
        self.start_time = None
        self.procs = []
        self.tasks = []
        self.found_factors = []
        self.completed_lines = 0
        self.completed_sigmas = set()

    async def run(self, residue_lines):
        self.start_time = time.time()

        cpu_ecm_args = [self.ecm_path, "-resume", "-", str(self.b1)]

        # Start processes, giving each its own slice of residues (interleaved partition).
        # No shared queue means no TOCTOU race where two tasks both pass queue.empty()
        # but only one item remains, leaving a task blocked in queue.get() forever.
        for i in range(self.threads):
            proc = await asyncio.create_subprocess_exec(
                *cpu_ecm_args,
                stdout=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            self.procs.append(proc)
            my_residues = residue_lines[i::self.threads]
            self.tasks.append(asyncio.create_task(handle_stdin(my_residues, proc.stdin)))

        # Launch one concurrent stdout reader per process feeding a shared queue.
        # This replaces the sequential readline() loop which would block on a slow/stuck
        # process while other processes' output piled up unread.
        output_queue = asyncio.Queue()
        reader_tasks = [
            asyncio.create_task(read_stdout(proc, i, output_queue))
            for i, proc in enumerate(self.procs)
        ]
        self.tasks.extend(reader_tasks)

        current_sigma = {}  # proc_index -> sigma currently being processed
        finished_readers = 0
        while finished_readers < len(self.procs):
            if interrupt_level >= 2:
                await self.kill()
                break

            proc_index, line = await output_queue.get()
            if line is None:  # sentinel: one reader finished
                finished_readers += 1
                continue

            if line.startswith("Step 2"):
                self.completed_lines += 1
                if proc_index in current_sigma:
                    self.completed_sigmas.add(current_sigma[proc_index])
                print(f"Completed {self.completed_lines}/{len(residue_lines)} CPU curves...                 ", end="\r", file=sys.stderr)
            elif line.startswith("Using"):
                # Parse sigma from "Using B1=..., sigma=0:16975636616726985561"
                m = re.search(r"sigma=\d+:(\d+)", line)
                if m:
                    current_sigma[proc_index] = int(m.group(1))
                self.last_using_line = line
            elif line.startswith("********** Factor found in step 2:"):
                found_factor = int(line.strip().split(" ")[-1])
                self.found_factors.append({
                    "factor": found_factor,
                    "using_line": getattr(self, "last_using_line", "Unknown")
                })
                print(f"\n*** FOUND FACTOR IN STAGE 2: {found_factor} ***", file=sys.stderr)
                # Immediately kill other procs to avoid wasted work
                await self.kill()
                return

        # Clean up tasks
        for task in self.tasks:
            task.cancel()

        # Wait for all to finish
        for proc in self.procs:
            if proc.returncode is None:
                await proc.wait()

    async def kill(self):
        for task in self.tasks:
            task.cancel()
        for proc in self.procs:
            if proc.returncode is None:
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass

class CPUProcFull:
    """Runs full ECM (stage 1 + stage 2) on a composite without saving residues."""
    def __init__(self, ecm_path, threads, b1):
        self.ecm_path = ecm_path
        self.threads = threads
        self.b1 = b1
        self.start_time = None
        self.procs = []
        self.tasks = []
        self.found_factors = []
        self.completed_curves = []  # list of (sigma, b2)
        self.last_using_line = "Unknown"

    @property
    def completed_count(self):
        return len(self.completed_curves)

    async def run(self, composite_str, curves_per_thread):
        self.start_time = time.time()

        output_queue = asyncio.Queue()
        for i in range(self.threads):
            proc = await asyncio.create_subprocess_exec(
                self.ecm_path, '-c', str(curves_per_thread), str(self.b1),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            self.procs.append(proc)
            self.tasks.append(asyncio.create_task(handle_stdin([composite_str], proc.stdin)))
            self.tasks.append(asyncio.create_task(read_stdout(proc, i, output_queue)))

        current_sigma = {}
        current_b2 = {}
        finished_readers = 0
        while finished_readers < self.threads:
            if interrupt_level >= 2:
                await self.kill()
                break

            proc_index, line = await output_queue.get()
            if line is None:
                finished_readers += 1
                continue

            if line.startswith("Step 2"):
                if proc_index in current_sigma:
                    self.completed_curves.append((current_sigma[proc_index], current_b2.get(proc_index)))
                print(f"Completed {self.completed_count} full ECM curves...                 ", end="\r", file=sys.stderr)
            elif line.startswith("Using"):
                m_sigma = re.search(r"sigma=\d+:(\d+)", line)
                m_b2 = re.search(r"B2=(\d+)", line)
                if m_sigma:
                    current_sigma[proc_index] = int(m_sigma.group(1))
                if m_b2:
                    current_b2[proc_index] = int(m_b2.group(1))
                self.last_using_line = line
            elif line.startswith("********** Factor found in step"):
                found_factor = int(line.strip().split(" ")[-1])
                self.found_factors.append({
                    "factor": found_factor,
                    "using_line": self.last_using_line
                })
                print(f"\n*** FOUND FACTOR: {found_factor} ***", file=sys.stderr)
                await self.kill()
                return

        for task in self.tasks:
            task.cancel()
        for proc in self.procs:
            if proc.returncode is None:
                await proc.wait()

    async def kill(self):
        for task in self.tasks:
            task.cancel()
        for proc in self.procs:
            if proc.returncode is None:
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass


async def main():
    global interrupt_level
    
    parser = argparse.ArgumentParser(description="Distributed CPU-ECM Worker")
    parser.add_argument("--server", type=str, default="http://localhost:5000", help="URL of the OEISFactor server")
    parser.add_argument("--name", type=str, required=True, help="Unique name for this worker")
    parser.add_argument("-t", "--threads", type=int, default=os.cpu_count() or 1, help="Number of CPU threads to use")
    parser.add_argument("--hours", type=float, default=1.0, help="Target hours of work to fetch per batch")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="verbosity (-v, -vv, etc)")
    args = parser.parse_args()

    loglevel = logging.WARNING
    if args.verbose > 0:
        loglevel = logging.INFO
    if args.verbose > 1:
        loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel, format="%(message)s")

    def handle_signal(signame):
        global interrupt_level
        interrupt_level += 1
        print(f"\nReceived {signame}. Interrupt level: {interrupt_level}", file=sys.stderr)
        if interrupt_level >= 3:
            sys.exit(1)

    loop = asyncio.get_running_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame), lambda signame=signame: handle_signal(signame))

    ecm_path = locate_ecm_install()
    
    # Register worker
    try:
        resp = requests.post(f"{args.server}/api/worker/register", json={"name": args.name, "type": "CPU"})
        resp.raise_for_status()
        print(f"Registered worker '{args.name}' with server {args.server} using {args.threads} threads")
    except Exception as e:
        print(f"Failed to register with server: {e}", file=sys.stderr)
        sys.exit(1)

    # speed_factor: ratio of reference-machine time to our observed time (EMA).
    # Calibrated from actual runs; stable across B1/digit changes because it's
    # a property of the hardware, not the work. last_b1/last_digits are used
    # together with ecmtimes to estimate the reference time for the next batch.
    speed_factor = None
    last_b1 = None
    last_digits = None
    full_speed_factor = None  # separate calibration for full ECM (stage 1 + stage 2)

    while interrupt_level == 0:
        try:
            # Compute how many curves to request based on target hours.
            # Use the reference timing table scaled by our observed speed factor
            # so that a B1 change is handled correctly (fast small-B1 curves don't
            # inflate the estimate for slow large-B1 ones).
            target_seconds = args.hours * 3600
            if speed_factor is not None:
                ref_per_curve = ecmtimes.get_ecm_time(last_digits, last_b1, 1, args.threads)
                actual_per_curve = ref_per_curve / speed_factor
                raw = target_seconds / actual_per_curve
                chunk_size = max(args.threads, (int(raw) // args.threads) * args.threads)
            else:
                chunk_size = args.threads  # first batch: just enough to saturate threads

            resp = requests.get(f"{args.server}/api/work/cpu", params={"client_name": args.name, "limit": chunk_size})
            if resp.status_code == 404 or not resp.json().get("work_batch"):
                # No stage-2 residues available — fall back to running full ECM curves
                full_resp = requests.get(f"{args.server}/api/work/cpu/full", params={
                    "client_name": args.name,
                    "digit_limit": 300,
                })
                if full_resp.status_code == 404:
                    print("No work available, sleeping...                        ", end="\r", file=sys.stderr)
                    await asyncio.sleep(10)
                    continue
                full_resp.raise_for_status()
                full_work = full_resp.json()
                composite_str = full_work["composite"]
                b1 = int(full_work["b1"])
                suggested_curves = int(full_work["suggested_curves"])
                full_expression = full_work.get("expression") or f"C{len(composite_str)}"
                full_t_level = full_work.get("t_level", 0)
                digits = len(composite_str)

                # Cap suggested_curves to at most one hour of work
                target_seconds = args.hours * 3600
                if full_speed_factor is not None:
                    ref_per_curve = ecmtimes.get_ecm_time(digits, b1, 1, args.threads)
                    actual_per_curve = ref_per_curve / full_speed_factor
                    hour_cap = max(args.threads, (int(target_seconds / actual_per_curve) // args.threads) * args.threads)
                else:
                    hour_cap = args.threads  # conservative until calibrated
                full_chunk = min(suggested_curves, hour_cap)
                full_chunk = max(args.threads, (full_chunk // args.threads) * args.threads)
                curves_per_thread = max(1, full_chunk // args.threads)

                print(f"\nNo stage-2 work: {full_expression} (C{digits}) t{full_t_level:.1f} — running {full_chunk} full ECM curves B1={b1}", file=sys.stderr)
                cpu_proc = CPUProcFull(ecm_path, args.threads, b1)
                await cpu_proc.run(composite_str, curves_per_thread)
                duration = time.time() - (cpu_proc.start_time or time.time())

                # Update full-ECM speed factor (kept separate from stage-2 speed factor)
                if cpu_proc.completed_count > 0 and duration > 0:
                    ref_time = ecmtimes.get_ecm_time(digits, b1, cpu_proc.completed_count, args.threads)
                    observed_factor = ref_time / duration
                    full_speed_factor = observed_factor if full_speed_factor is None else (0.7 * full_speed_factor + 0.3 * observed_factor)

                # Report any factors found
                if cpu_proc.found_factors:
                    composite_int = int(composite_str)
                    for match in cpu_proc.found_factors:
                        factor_str = str(match['factor'])
                        if len(factor_str) >= 60:
                            os.makedirs("data/logs/hits", exist_ok=True)
                            log_path = os.path.join("data/logs/hits", f"hit_cpu_full_{int(time.time())}_{factor_str[:10]}.log")
                            with open(log_path, "w") as lf:
                                lf.write(f"Timestamp: {time.time()}\n")
                                lf.write(f"Composite: {composite_str}\n")
                                lf.write(f"Factor: {factor_str}\n")
                                lf.write(f"Length: {len(factor_str)} digits\n")
                                lf.write(f"B1: {b1}\n")
                                lf.write(f"Context: {match['using_line']}\n")
                            print(f"\n\n********** BIG CPU HIT: C{len(factor_str)} logged to {log_path} **********\n\n", file=sys.stderr)
                    try:
                        f_resp = requests.post(f"{args.server}/api/submit/factor", json={
                            "client_name": args.name,
                            "composite": composite_int,
                            "factors": [f['factor'] for f in cpu_proc.found_factors]
                        })
                        f_resp.raise_for_status()
                        print("Factor reported to server!", file=sys.stderr)
                    except Exception as e:
                        print(f"Failed to submit factor: {e}", file=sys.stderr)

                # Submit t-level update
                if cpu_proc.completed_count > 0 and interrupt_level < 2:
                    from collections import Counter
                    b2_counts = Counter(b2 for _, b2 in cpu_proc.completed_curves if b2 is not None)
                    curve_groups = [{"count": c, "b1": b1, "b2": b2, "ecm_param": 1} for b2, c in b2_counts.items()]
                    if curve_groups:
                        try:
                            t_resp = requests.post(f"{args.server}/api/submit/cpu/full", json={
                                "client_name": args.name,
                                "composite": composite_str,
                                "curve_groups": curve_groups,
                            })
                            t_resp.raise_for_status()
                            new_t = t_resp.json().get("new_t_level")
                            new_t_str = f"{new_t:.1f}" if new_t is not None else "?"
                            print(f"Submitted {cpu_proc.completed_count} full ECM curves: {full_expression} t{full_t_level:.1f} -> t{new_t_str}", file=sys.stderr)
                        except Exception as e:
                            print(f"Failed to submit full CPU curves: {e}", file=sys.stderr)
                continue
            resp.raise_for_status()
            
            work_batch = resp.json()["work_batch"]
            if not work_batch:
                await asyncio.sleep(10)
                continue
                
            print(f"\nGot {len(work_batch)} Stage 2 curves from server", file=sys.stderr)
            
            # Group curves by B1 bound so we can run them together efficiently
            # Note: They should generally all have the same B1 but it's safe to group
            b1_groups = {}
            for work in work_batch:
                b1 = int(work["b1"])
                if b1 not in b1_groups:
                    b1_groups[b1] = []
                b1_groups[b1].append(work)
                
            for b1, jobs in b1_groups.items():
                if interrupt_level > 0:
                    break

                residues = [j["resume_line"] for j in jobs]
                expression = jobs[0].get("expression") or f"C{len(jobs[0]['composite'])}"
                t_level_val = jobs[0].get("t_level", 0)
                print(f"\nStage 2: {expression} (C{len(jobs[0]['composite'])}) t{t_level_val:.1f} — {len(residues)} curves B1={b1}", file=sys.stderr)

                cpu_proc = CPUProc(ecm_path, args.threads, b1)
                await cpu_proc.run(residues)
                duration = time.time() - (cpu_proc.start_time or time.time())

                # Update speed factor from this batch.
                # speed_factor = reference_time / actual_time (both for the same n curves + threads).
                # Being a hardware ratio it's stable across B1/digit values, so we can use it
                # with ecmtimes at any future B1 to get an accurate curve count estimate.
                digits = len(jobs[0]["composite"])
                if len(residues) > 0 and duration > 0:
                    ref_time = ecmtimes.get_ecm_time(digits, b1, len(residues), args.threads)
                    observed_factor = ref_time / duration
                    speed_factor = observed_factor if speed_factor is None else (0.7 * speed_factor + 0.3 * observed_factor)
                    last_b1 = b1
                    last_digits = digits
                
                # Check for found factors
                if cpu_proc.found_factors:
                    print(f"Found factors during Stage 2: {[f['factor'] for f in cpu_proc.found_factors]}", file=sys.stderr)
                    # We only know the composite of the first job because we batched, 
                    # but if we found a factor it means they probably all shared a composite.
                    composite = int(jobs[0]["composite"]) 
                    
                    # Log big hits (> 60 digits)
                    for match in cpu_proc.found_factors:
                        factor_str = str(match['factor'])
                        using_line = match['using_line']
                        if len(factor_str) >= 60:
                            os.makedirs("data/logs/hits", exist_ok=True)
                            log_path = os.path.join("data/logs/hits", f"hit_cpu_{int(time.time())}_{factor_str[:10]}.log")
                            with open(log_path, "w") as lf:
                                lf.write(f"Timestamp: {time.time()}\n")
                                lf.write(f"Composite: {composite}\n")
                                lf.write(f"Factor: {factor_str}\n")
                                lf.write(f"Length: {len(factor_str)} digits\n")
                                lf.write(f"B1: {b1}\n")
                                lf.write(f"Context: {using_line}\n")
                            print(f"\n\n********** BIG CPU HIT: C{len(factor_str)} logged to {log_path} **********\n\n", file=sys.stderr)
                    
                    try:
                        f_resp = requests.post(f"{args.server}/api/submit/factor", json={
                            "client_name": args.name,
                            "composite": composite,
                            "factors": [f['factor'] for f in cpu_proc.found_factors]
                        })
                        f_resp.raise_for_status()
                        print("Factors successfully reported to server!", file=sys.stderr)
                    except Exception as e:
                        print(f"Failed to submit factors: {e}", file=sys.stderr)
                        
                # Submit all completions in one batch call instead of one POST per job
                # If killed mid-batch, only submit curves whose sigma actually completed.
                completed_jobs = [j for j in jobs if j["sigma"] in cpu_proc.completed_sigmas] if interrupt_level >= 2 else jobs
                if not completed_jobs:
                    break
                try:
                    c_resp = requests.post(f"{args.server}/api/submit/cpu/batch", json={
                        "client_name": args.name,
                        "completions": [
                            {
                                "composite": int(job["composite"]),
                                "sigma": job["sigma"],
                                "b2_start": b1,
                                "b2_end": b1 * 100,
                                "duration": duration / len(completed_jobs),
                            }
                            for job in completed_jobs
                        ]
                    })
                    c_resp.raise_for_status()
                    new_t_levels = c_resp.json().get("new_t_levels", {})
                    composite_key = jobs[0]["composite"]
                    new_t_info = new_t_levels.get(composite_key, {})
                    new_t = new_t_info.get("t_level")
                    new_t_str = f"{new_t:.1f}" if new_t is not None else "?"
                    print(f"Submitted {len(completed_jobs)} curves: {expression} t{t_level_val:.1f} -> t{new_t_str}", file=sys.stderr)
                except Exception as e:
                    print(f"Failed to mark CPU curves complete: {e}", file=sys.stderr)
                        
        except requests.exceptions.RequestException as e:
            print(f"\nNetwork error connecting to server: {e}", file=sys.stderr)
            await asyncio.sleep(5)
        except Exception as e:
            print(f"\nError in work loop: {e}", file=sys.stderr)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
