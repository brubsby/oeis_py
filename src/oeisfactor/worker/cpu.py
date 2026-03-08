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

async def read_stdout(proc, output_queue):
    try:
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            await output_queue.put(line.decode('utf-8', errors='replace').strip())
    except Exception as e:
        logging.error(f"Error reading stdout: {e}")
    finally:
        await output_queue.put(None)  # sentinel: this reader is done

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
            asyncio.create_task(read_stdout(proc, output_queue))
            for proc in self.procs
        ]
        self.tasks.extend(reader_tasks)

        finished_readers = 0
        while finished_readers < len(self.procs):
            if interrupt_level >= 2:
                await self.kill()
                break

            line = await output_queue.get()
            if line is None:  # sentinel: one reader finished
                finished_readers += 1
                continue

            if line.startswith("Step 2"):
                self.completed_lines += 1
                print(f"Completed {self.completed_lines}/{len(residue_lines)} CPU curves...                 ", end="\r", file=sys.stderr)
            elif line.startswith("Using"):
                # Keep track of the last "Using" line, which contains sigma/B1 info right before a factor
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

    seconds_per_curve = None  # EMA of observed Stage 2 time per curve; None until first batch completes

    while interrupt_level == 0:
        try:
            # Compute how many curves to request.
            # Target args.hours of wall-clock work, rounded down to a multiple of args.threads
            # so every thread gets an equal share. Minimum is args.threads so all threads are saturated.
            if seconds_per_curve is not None:
                raw = (args.hours * 3600) / seconds_per_curve
                chunk_size = max(args.threads, (int(raw) // args.threads) * args.threads)
            else:
                chunk_size = args.threads  # first batch: just enough to saturate threads

            resp = requests.get(f"{args.server}/api/work/cpu", params={"client_name": args.name, "limit": chunk_size})
            if resp.status_code == 404 or not resp.json().get("work_batch"):
                print("No CPU work available, sleeping...                        ", end="\r", file=sys.stderr)
                await asyncio.sleep(10)
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
                print(f"Running CPU Stage 2 on {len(residues)} curves with B1={b1}...", file=sys.stderr)

                cpu_proc = CPUProc(ecm_path, args.threads, b1)
                await cpu_proc.run(residues)
                duration = time.time() - (cpu_proc.start_time or time.time())

                # Update EMA of seconds-per-curve for future chunk size estimates
                if len(residues) > 0 and duration > 0:
                    observed = duration / len(residues)
                    seconds_per_curve = observed if seconds_per_curve is None else (0.7 * seconds_per_curve + 0.3 * observed)
                
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
                try:
                    c_resp = requests.post(f"{args.server}/api/submit/cpu/batch", json={
                        "client_name": args.name,
                        "completions": [
                            {
                                "composite": int(job["composite"]),
                                "sigma": job["sigma"],
                                "b2_start": b1,
                                "b2_end": b1 * 100,
                                "duration": duration / len(jobs),
                            }
                            for job in jobs
                        ]
                    })
                    c_resp.raise_for_status()
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
