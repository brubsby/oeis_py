import subprocess
import re

# data was collected by changing the ecm source to print out estimated curves for every single digit number, and with higher precision

order = ["B1", "B2", "dF", "k", "S", "param", 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100]

def get_curve_info(B1, composite, param=1):
    if type(composite) != bytes:
        composite = bytes(str(composite), "utf-8")
    # ECM should finish rho / dickman calculation quickly
    process = subprocess.run(["timeout", "0.1", "./ecm", "-v", "-param", str(param), str(B1)], input=composite, capture_output=True)
    output = process.stdout.split(b"\n")
    CURVES_KEY = b'10\t11\t12\t13\t14\t15\t16\t17\t18\t19\t20\t21\t22\t23\t24\t25\t26\t27\t28\t29\t30\t31\t32\t33\t34\t35\t36\t37\t38\t39\t40\t41\t42\t43\t44\t45\t46\t47\t48\t49\t50\t51\t52\t53\t54\t55\t56\t57\t58\t59\t60\t61\t62\t63\t64\t65\t66\t67\t68\t69\t70\t71\t72\t73\t74\t75\t76\t77\t78\t79\t80\t81\t82\t83\t84\t85\t86\t87\t88\t89\t90\t91\t92\t93\t94\t95\t96\t97\t98\t99\t100'
    digits = map(int, CURVES_KEY.split())
    expected_curves = map(lambda x: float(x), output[output.index(CURVES_KEY) + 1].split())
    line = output[output.index(CURVES_KEY) - 3].decode("utf-8")
    B2 = int(re.search(r"(?<=B2=)\d+", line).group(0))
    line = output[output.index(CURVES_KEY) - 2].decode("utf-8")
    dF = int(re.search(r"(?<=dF=)\d+", line).group(0))
    k = int(re.search(r"(?<=k=)\d+", line).group(0))
    if B2 < 1e7:
        S = 1
    elif B2 < 1e8:
        S = 2
    elif B2 < 1e9:
        S = -3
    elif B2 < 1e10:
        S = -6
    elif B2 < 3e11:
        S = -12
    else:
        S = -30
    return [B1, B2, dF, k, S, param, *expected_curves]

b1s = []
composite = 1111111111111111111111111111111111111111111111111

for c in range(3, 10):
    for a in range(0,10):
        for b in range(1,10):
            val = (b * 10 + a) * pow(10, c)
            if val <= 50000000000:
                b1s.append(val)

for b1 in sorted(b1s):
    print(get_curve_info(b1, composite, param=0))
