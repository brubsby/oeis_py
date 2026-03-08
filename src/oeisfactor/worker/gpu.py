import argparse
import asyncio
import logging
import os
import re
import shutil
import signal
import sys
import tempfile
import time
import requests

interrupt_level = 0

def locate_gpu_ecm_install():
    install_location = shutil.which("ecm")
    if not install_location:
        print("Could not find ecm binary. Please install GMP-ECM.", file=sys.stderr)
        sys.exit(1)
    import subprocess
    result = subprocess.run([install_location, "-printconfig"], capture_output=True, text=True)
    if "WITH_GPU = 1" not in result.stdout:
        print("Could not find GPU ECM binary location, maybe try `make install` in your ecm source dir", file=sys.stderr)
        sys.exit(1)
    return install_location

class GPUProc:
    def __init__(self, ecm_path, gpu_device, gpu_curves, save_file_path, b1, composite):
        self.ecm_path = ecm_path
        self.gpu_device = gpu_device
        self.gpu_curves = gpu_curves
        self.save_file_path = save_file_path
        self.b1 = b1
        self.composite = composite
        self.start_time = None
        self.estimated_end_time = None
        self.lines = []

    async def run(self):
        gpu_device_args = ["-gpudevice", str(self.gpu_device)] if self.gpu_device is not None else []
        gpu_curves_args = ["-gpucurves", str(self.gpu_curves)] if self.gpu_curves is not None else []
        gpu_ecm_args = [self.ecm_path] + gpu_device_args + gpu_curves_args + ["-gpu", "-v", "-save", self.save_file_path, str(self.b1), "0"]
        
        self.gpu_proc = await asyncio.create_subprocess_exec(
            *gpu_ecm_args, stdout=asyncio.subprocess.PIPE, stdin=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT)
        
        self.start_time = time.time()
        self.gpu_proc.stdin.write(str(self.composite).encode() + b"\n")
        await self.gpu_proc.stdin.drain()
        self.gpu_proc.stdin.close()
        
        # Read output line by line
        while True:
            line = await self.gpu_proc.stdout.readline()
            if not line:
                break
            line = line.decode('utf-8', errors='replace')
            self.lines.append(line)
            match = re.search(r"ETA (\d+) \+ (\d+) = (\d+) seconds?", line)
            if match:
                self.estimated_end_time = int(match.group(1)) + time.time()
                
            if interrupt_level >= 2:
                try:
                    self.gpu_proc.kill()
                except ProcessLookupError:
                    pass
                
        await self.gpu_proc.wait()
        return self.gpu_proc.returncode

async def main():
    global interrupt_level
    
    parser = argparse.ArgumentParser(description="Distributed GPU-ECM Worker")
    parser.add_argument("--server", type=str, default="http://localhost:5000", help="URL of the OEISFactor server")
    parser.add_argument("--name", type=str, required=True, help="Unique name for this worker")
    parser.add_argument("--gpudevice", type=int, default=None, help="use device <GPU_DEVICE> to execute GPU code")
    parser.add_argument("--gpucurves", type=int, default=8192, help="compute on <GPU_CURVES> curves in parallel on the GPU")
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

    ecm_path = locate_gpu_ecm_install()
    
    # Register worker
    try:
        resp = requests.post(f"{args.server}/api/worker/register", json={"name": args.name, "type": "GPU"})
        resp.raise_for_status()
        print(f"Registered worker '{args.name}' with server {args.server}")
    except Exception as e:
        print(f"Failed to register with server: {e}", file=sys.stderr)
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmpdir:
        while interrupt_level == 0:
            try:
                # 1. Ask for work
                resp = requests.get(f"{args.server}/api/work/gpu", params={"client_name": args.name, "curves": args.gpucurves})
                if resp.status_code == 404:
                    print("No work available, sleeping...                        ", end="\r", file=sys.stderr)
                    await asyncio.sleep(10)
                    continue
                resp.raise_for_status()
                work = resp.json()
                
                composite = int(work["composite"])
                b1 = int(work["b1"])
                
                print(f"\nGot work: Composite C{len(str(composite))} with B1={b1}", file=sys.stderr)
                
                # 2. Run GPU-ECM
                save_file_path = os.path.join(tmpdir, f"gpu_save_{int(time.time())}.txt")
                gpu_proc = GPUProc(ecm_path, args.gpudevice, args.gpucurves, save_file_path, b1, composite)
                
                print(f"Starting GPU-ECM Stage 1...", file=sys.stderr)
                returncode = await gpu_proc.run()
                duration = time.time() - (gpu_proc.start_time or time.time())
                
                if interrupt_level > 0:
                    print("Interrupted, exiting loop...", file=sys.stderr)
                    break
                    
                outs = "".join(gpu_proc.lines)
                
                # 3. Check for factors
                factor_matches = re.findall(r"GPU: factor (\d+) found in Step 1 with curve (\d+) \(-sigma (\d+):(\d+)\)", outs)
                factors_found = list(set([int(m[0]) for m in factor_matches]))
                if factors_found:
                    print(f"*** FOUND FACTORS: {factors_found} ***", file=sys.stderr)
                    
                    # Log big hits (> 60 digits)
                    for match in factor_matches:
                        factor_str, curve, param, sigma = match
                        if len(factor_str) >= 60:
                            os.makedirs("data/logs/hits", exist_ok=True)
                            log_path = os.path.join("data/logs/hits", f"hit_gpu_{int(time.time())}_{factor_str[:10]}.log")
                            with open(log_path, "w") as lf:
                                lf.write(f"Timestamp: {time.time()}\n")
                                lf.write(f"Composite: {composite}\n")
                                lf.write(f"Factor: {factor_str}\n")
                                lf.write(f"Length: {len(factor_str)} digits\n")
                                lf.write(f"B1: {b1}\n")
                                lf.write(f"Sigma: {param}:{sigma}\n")
                                lf.write(f"Curve: {curve}\n")
                            print(f"\n\n********** BIG GPU HIT: C{len(factor_str)} logged to {log_path} **********\n\n", file=sys.stderr)

                    try:
                        f_resp = requests.post(f"{args.server}/api/submit/factor", json={
                            "client_name": args.name,
                            "composite": composite,
                            "factors": factors_found
                        })
                        f_resp.raise_for_status()
                        print("Factors successfully reported to server!", file=sys.stderr)
                    except Exception as e:
                        print(f"Failed to submit factors: {e}", file=sys.stderr)
                
                # 4. Submit residues
                if os.path.exists(save_file_path):
                    with open(save_file_path, "r") as f:
                        residues = f.read().strip().split("\n")
                    
                    # Remove empty lines
                    residues = [r for r in residues if r.strip()]
                    
                    if residues:
                        print(f"Submitting {len(residues)} residues to server...", file=sys.stderr)
                        try:
                            # Batch submit all at once
                            r_resp = requests.post(f"{args.server}/api/submit/gpu", json={
                                "client_name": args.name,
                                "composite": composite,
                                "duration": duration,
                                "residue_lines": residues
                            })
                            r_resp.raise_for_status()
                            print(f"Successfully submitted residues.", file=sys.stderr)
                        except Exception as e:
                            print(f"Failed to submit residues: {e}", file=sys.stderr)
                
            except requests.exceptions.RequestException as e:
                print(f"\nNetwork error connecting to server: {e}", file=sys.stderr)
                await asyncio.sleep(5)
            except Exception as e:
                print(f"\nError in work loop: {e}", file=sys.stderr)
                await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
