import asyncio
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

import requests

from oeisfactor.worker import common


def locate_gpu_ecm_install():
    install_location = shutil.which("ecm")
    if not install_location:
        print("Could not find ecm binary. Please install GMP-ECM.", file=sys.stderr)
        sys.exit(1)
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

    async def _print_status(self):
        try:
            while True:
                elapsed = time.time() - self.start_time
                if self.estimated_end_time is not None:
                    total = self.estimated_end_time - self.start_time
                    pct = min(100.0, 100.0 * elapsed / total) if total > 0 else 0
                    remaining = max(0, self.estimated_end_time - time.time())
                    print(f"GPU ECM: {pct:.1f}% (~{int(remaining)}s remaining)          ", end="\r", file=sys.stderr)
                else:
                    print(f"GPU ECM: starting... ({int(elapsed)}s elapsed)          ", end="\r", file=sys.stderr)
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

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

        status_task = asyncio.create_task(self._print_status())

        while True:
            line = await self.gpu_proc.stdout.readline()
            if not line:
                break
            line = line.decode('utf-8', errors='replace')
            self.lines.append(line)
            match = re.search(r"ETA (\d+) \+ (\d+) = (\d+) seconds?", line)
            if match:
                self.estimated_end_time = int(match.group(1)) + time.time()

            if common.interrupt_level >= 2:
                try:
                    self.gpu_proc.kill()
                except ProcessLookupError:
                    pass

        status_task.cancel()
        await asyncio.gather(status_task, return_exceptions=True)
        print(f"GPU ECM: 100%                              ", file=sys.stderr)
        await self.gpu_proc.wait()
        return self.gpu_proc.returncode


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Distributed GPU-ECM Worker")
    common.add_common_args(parser)
    parser.add_argument("--gpudevice", type=int, default=None, help="use device <GPU_DEVICE> to execute GPU code")
    parser.add_argument("--gpucurves", type=int, default=8192, help="compute on <GPU_CURVES> curves in parallel on the GPU")
    args = parser.parse_args()

    common.setup_logging(args.verbose)

    loop = asyncio.get_running_loop()
    common.setup_signal_handlers(loop)

    ecm_path = locate_gpu_ecm_install()
    common.register_worker(args.server, args.name, "GPU")

    with tempfile.TemporaryDirectory() as tmpdir:
        while common.interrupt_level == 0:
            try:
                t0 = time.time()
                resp = requests.get(f"{args.server}/api/work/gpu", params={"client_name": args.name, "curves": args.gpucurves})
                logging.debug(f"GPU work request took {time.time() - t0:.2f}s")
                if resp.status_code == 404:
                    print("No work available, sleeping...                        ", end="\r", file=sys.stderr)
                    await asyncio.sleep(10)
                    continue
                resp.raise_for_status()
                work = resp.json()

                composite = int(work["composite"])
                b1 = int(work["b1"])
                expression = work.get("expression") or f"C{len(str(composite))}"
                t_level_val = work.get("t_level", 0)

                print(f"\nGot work: {expression} (C{len(str(composite))}) t{t_level_val:.1f} B1={b1}", file=sys.stderr)

                # Run GPU-ECM
                save_file_path = os.path.join(tmpdir, f"gpu_save_{int(time.time())}.txt")
                gpu_proc = GPUProc(ecm_path, args.gpudevice, args.gpucurves, save_file_path, b1, composite)
                print(f"Starting GPU-ECM Stage 1...", file=sys.stderr)
                returncode = await gpu_proc.run()
                duration = time.time() - (gpu_proc.start_time or time.time())

                if common.interrupt_level > 0:
                    print("Interrupted, exiting loop...", file=sys.stderr)
                    break

                outs = "".join(gpu_proc.lines)

                # Check for factors
                factor_matches = re.findall(r"GPU: factor (\d+) found in Step 1 with curve (\d+) \(-sigma (\d+):(\d+)\)", outs)
                factors_found = list(set([int(m[0]) for m in factor_matches]))
                if factors_found:
                    print(f"*** FOUND FACTORS: {factors_found} ***", file=sys.stderr)
                    for factor_str, curve, param, sigma in factor_matches:
                        common.log_big_hit(factor_str, composite, b1, tag="gpu",
                                           extra_fields={"Sigma": f"{param}:{sigma}", "Curve": curve})
                    common.submit_factors(args.server, args.name, composite, factors_found)

                # Submit residues
                if os.path.exists(save_file_path):
                    with open(save_file_path, "r") as f:
                        residues = [r for r in f.read().strip().split("\n") if r.strip()]
                    if residues:
                        print(f"Submitting {len(residues)} residues to server...", file=sys.stderr)
                        try:
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
