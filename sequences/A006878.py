import itertools
import sys
import logging

from sequence import Sequence


class A006878(Sequence):

    def __init__(self):
        super().__init__(lookup_list=[
            0,
            1,
            7,
            8,
            16,
            19,
            20,
            23,
            111,
            112,
            115,
            118,
            121,
            124,
            127,
            130,
            143,
            144,
            170,
            178,
            181,
            182,
            208,
            216,
            237,
            261,
            267,
            275,
            278,
            281,
            307,
            310,
            323,
            339,
            350,
            353,
            374,
            382,
            385,
            442,
            448,
            469,
            508,
            524,
            527,
            530,
            556,
            559,
            562,
            583,
            596,
            612,
            664,
            685,
            688,
            691,
            704,
            705,
            744,
            949,
            950,
            953,
            956,
            964,
            965,
            986,
            987,
            1000,
            1008,
            1050,
            1087,
            1131,
            1132,
            1153,
            1184,
            1210,
            1213,
            1219,
            1220,
            1228,
            1234,
            1242,
            1255,
            1307,
            1308,
            1321,
            1324,
            1332,
            1335,
            1348,
            1356,
            1408,
            1411,
            1437,
            1440,
            1443,
            1549,
            1550,
            1563,
            1566,
            1569,
            1585,
            1588,
            1601,
            1617,
            1638,
            1651,
            1659,
            1662,
            1820,
            1823,
            1847,
            1853,
            1856,
            1859,
            1862,
            1865,
            1868,
            1871,
            1874,
            1895,
            1903,
            1916,
            1919,
            1958,
            2039,
            2042,
            2045,
            2046,
            2090,
        ], start_index=1)

    def calculate(self, n):
        pass


sys.modules[__name__] = A006878()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for n, val in A006878().enumerate():
        print(f"{n} {val}")
