import sys
import pathlib

# for dealing with fastgcd outputs, used in bash scripts
sys.set_int_max_str_digits(10000)
composites = set(map(int, pathlib.Path(sys.argv[1]).read_text().strip().split("\n")))

for line in sys.stdin.readlines():
    term1, term2 = map(lambda x: int(x, 16), line.split('\t'))
    if term1 == term2:
        continue
    if term1 not in composites:
        break
    print(f"{term1}=[{term2}]")
