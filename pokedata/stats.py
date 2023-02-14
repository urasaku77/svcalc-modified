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
pattern = "([HABCDS]+).*?([+\-]?[-0-9]+)"


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
        if key == StatsKey.H:
            return self.__H
        elif key == StatsKey.A:
            return self.__A
        elif key == StatsKey.B:
            return self.__B
        elif key == StatsKey.C:
            return self.__C
        elif key == StatsKey.D:
            return self.__D
        elif key == StatsKey.S:
            return self.__S

    def __setitem__(self, key: StatsKey, value):
        if key == StatsKey.H:
            self.__H = value
        elif key == StatsKey.A:
            self.__A = value
        elif key == StatsKey.B:
            self.__B = value
        elif key == StatsKey.C:
            self.__C = value
        elif key == StatsKey.D:
            self.__D = value
        elif key == StatsKey.S:
            self.__S = value

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
    def rank_text(self):
        text = ""
        for key in StatsKey:
            if key == StatsKey.H:
                continue
            value = self[key]
            if value > 0:
                text += key.name + "+" + str(value) + " "
            elif value < 0:
                text += key.name + str(value) + " "
        return text

    @property
    def to_string(self):
        return "{0}-{1}-{2}-{3}-{4}-{5}".format(
            self.__H, self.__A, self.__B, self.__C, self.__D, self.__S)

    def init_values(self, value: int):
        self.__H = value
        self.__A = value
        self.__B = value
        self.__C = value
        self.__D = value
        self.__S = value

    def set_values(self, h=None, a=None, b=None, c=None, d=None, s=None):
        self.__H = h if h is not None else self.__H
        self.__A = a if a is not None else self.__A
        self.__B = b if b is not None else self.__B
        self.__C = c if c is not None else self.__C
        self.__D = d if d is not None else self.__D
        self.__S = s if s is not None else self.__S
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

    def set_values_from_int(self, type: str, value: int):
        match type:
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

    def add_values_from_string(self, values_string: str):
        values_list = re.findall(pattern, values_string, re.S)
        for values in values_list:
            value: int = int(values[1])
            for key in values[0]:
                match key:
                    case "H":
                        self.__H += value
                    case "A":
                        self.__A += value
                    case "B":
                        self.__B += value
                    case "C":
                        self.__C += value
                    case "D":
                        self.__D += value
                    case "S":
                        self.__S += value

    def max_stats(self) -> StatsKey:
        max_key: StatsKey = StatsKey.S
        max_value: int = self.S
        for key in [StatsKey.D, StatsKey.C, StatsKey.B, StatsKey.A]:
            if self[key] >= max_value:
                max_key = key
                max_value = self[key]
        return max_key
