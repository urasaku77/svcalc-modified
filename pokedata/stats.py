from enum import IntEnum
import re


class StatsKey(IntEnum):
    H = 0
    A = 1
    B = 2
    C = 3
    D = 4
    S = 5


# 文字変換用の正規表現
pattern = "([HABCDS]+).*?([0-9]+)"


class Stats:
    __slots__ = ['__H', '__A', '__B', '__C', '__D', '__S']

    def __init__(self, init_value=0):
        self.__H: int = init_value
        self.__A: int = init_value
        self.__B: int = init_value
        self.__C: int = init_value
        self.__D: int = init_value
        self.__S: int = init_value

    def __getitem__(self, key: StatsKey):
        match key:
            case StatsKey.H:
                return self.__H
            case StatsKey.A:
                return self.__A
            case StatsKey.B:
                return self.__B
            case StatsKey.C:
                return self.__C
            case StatsKey.D:
                return self.__D
            case StatsKey.S:
                return self.__S

    @property
    def H(self):
        return self.__H

    @property
    def A(self):
        return self.__A

    @property
    def B(self):
        return self.__B

    @property
    def C(self):
        return self.__C

    @property
    def D(self):
        return self.__D

    @property
    def S(self):
        return self.__S

    @property
    def to_string(self):
        return "{0}-{1}-{2}-{3}-{4}-{5}".format(
            self.__H, self.__A, self.__B, self.__C, self.__D, self.__S)

    def set_values(self, h=-1, a=-1, b=-1, c=-1, d=-1, s=-1):
        self.__H = h if h > -1 else self.__H
        self.__A = a if a > -1 else self.__A
        self.__B = b if b > -1 else self.__B
        self.__C = c if c > -1 else self.__C
        self.__D = d if d > -1 else self.__D
        self.__S = s if s > -1 else self.__S
        return self

    def set_values_from_stats(self, stats):
        self.set_values(
            h=stats.H,
            a=stats.A,
            b=stats.B,
            c=stats.C,
            d=stats.D,
            s=stats.S,
        )

    def set_values_from_string(self, values_string: str):
        values_list = re.findall(pattern, values_string, re.S)
        for values in values_list:
            value: int = int(values[1])
            for key in values[0]:
                match key:
                    case "H":
                        self.__H = value
                    case "A":
                        self.__A = value
                    case "B":
                        self.__B = value
                    case "C":
                        self.__C = value
                    case "D":
                        self.__D = value
                    case "S":
                        self.__S = value

    def max_stats(self) -> StatsKey:
        max_key: StatsKey = StatsKey.S
        max_value: int = self.S
        for key in [StatsKey.D, StatsKey.C, StatsKey.B, StatsKey.A]:
            if self[key] >= max_value:
                max_key = key
                max_value = self[key]
        return max_key
