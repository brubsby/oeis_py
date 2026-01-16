import functools
import subprocess

t_level_path = "C:/GitProjects/t-level/dist/t-level.exe"

def get_t_level(curve_b1_tuples):
    if not curve_b1_tuples or not curve_b1_tuples[0]:
        return 0
    curve_strings = ";".join("@".join(map(str, tup)) for tup in curve_b1_tuples)
    t_level_return = subprocess.run(
        [t_level_path, "-q", curve_strings, "-r5"],
        capture_output=True, stdin=subprocess.DEVNULL)
    if t_level_return.returncode != 0:
        raise RuntimeError(
        f"t_level returned error code {t_level_return.returncode}, stdout was:\n"
        f"{t_level_return.stdout}"
        f"stderr was:\n"
        f"{t_level_return.stderr}")
    return float(t_level_return.stdout.strip()[1:])


@functools.cache
def get_b1_curves(start_work, end_work):
    t_level_return = subprocess.run(
        [t_level_path, "-w", str(start_work), "-t", str(end_work)],
        capture_output=True, stdin=subprocess.DEVNULL)
    if t_level_return.returncode != 0:
        raise RuntimeError(
            f"t_level returned error code {t_level_return.returncode}, stdout was:\n"
            f"{t_level_return.stdout}"
            f"stderr was:\n"
            f"{t_level_return.stderr}")
    b1, curves = t_level_return.stdout.split(b'\n')[2].strip().split(b'@')
    return int(float(curves)), int(b1)

if __name__ == "__main__":
    print(get_b1_curves(0,2))