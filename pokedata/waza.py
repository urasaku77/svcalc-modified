from typing import Optional, Union

from pokedata.const import Types
from data.db import DB


class Waza:

    def __init__(self, db_data=None, base: Optional["WazaBase"] = None):
        if db_data is not None:
            self.__name: str = db_data['name']
            self.__type: Types = Types[db_data['type']]
            self.__category: str = db_data['category']
            self.__power: int = db_data['power']
            self.__hit: int = db_data['hit']
            self.__pp: int = db_data['pp']
            self.__is_touch: bool = db_data['is_touch']
            self.__is_guard: bool = db_data['is_guard']
            self.__description: bool = db_data['description']

        self.__ratio = base.ratio if base is not None else -1
        self.__count = base.count if base is not None else -1
        self.__critical = base.critical if base is not None else False

    # region プロパティ
    @property
    def name(self) -> str:
        return self.__name

    @property
    def type(self) -> Types:
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = value

    @property
    def category(self) -> str:
        return self.__category

    @category.setter
    def category(self, value) -> None:
        self.__category = value

    @property
    def power(self) -> int:
        return self.__power

    @property
    def is_touch(self) -> bool:
        return self.__is_touch

    @property
    def critical(self) -> bool:
        return self.__critical

    @critical.setter
    def critical(self, value) -> None:
        self.__critical = value

    @property
    def has_effect(self) -> bool:
        return "0%" in self.__description

    @property
    def ratio(self) -> float:
        return self.__ratio

    @property
    def count(self) -> int:
        return self.__count
    # endregion

    @staticmethod
    def ByName(name):
        return Waza(db_data=DB.get_waza_data_by_name(name))

    @staticmethod
    def ByWazaBase(base: "WazaBase"):
        return Waza(db_data=DB.get_waza_data_by_name(base.name), base=base)


class WazaBase:
    TYPE_NONE = 0
    TYPE_RATIO = 1
    TYPE_COUNT = 2

    __slots__ = ("__name", "__ratio", "__ratio_list", "__count", "__count_list", "__critical")

    def __init__(self, name):
        self.__name = name
        self.__ratio_list: Optional[tuple[float]] = None
        self.__ratio: float = 1
        self.__count_list: Optional[tuple[int]] = None
        self.__count: int = 1
        self.__critical: bool = False

        match name:
            case "タネマシンガン" | "ロックブラスト" | "つららばり" | "スケイルショット" | "ミサイルばり":
                self.__count_list = (2, 3, 4, 5)
                self.__count = 3
            case "ネズミざん":
                self.__count_list = (10, 9, 8, 7, 6, 5, 4, 3, 2, 1)
                self.__count = 10
            case "ドラゴンアロー" | "ダブルウイング":
                self.__count_list = (2,)
                self.__count = 2
            case "ふんどのこぶし":
                self.__ratio_list = (1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0)
                self.__ratio = 1.0
            case "アクロバット":
                self.__ratio_list = (1.0, 2.0)
                self.__ratio = 1.0
            case "はたきおとす":
                self.__ratio_list = (1.5, 1.0)
                self.__ratio = 1.5
            case _:
                self.__ratio_list = None
                self.__ratio = -1

    @property
    def name(self) -> str:
        return self.__name

    @property
    def ratio_list(self) -> Optional[tuple[float]]:
        return self.__ratio_list

    @property
    def ratio(self) -> float:
        return self.__ratio

    @property
    def count_list(self) -> Optional[tuple[float]]:
        return self.__count_list

    @property
    def count(self) -> int:
        return self.__count

    @property
    def critical(self) -> bool:
        return self.__critical

    @property
    def has_ratio(self) -> bool:
        return self.__ratio_list is not None

    @property
    def has_count(self) -> bool:
        return self.__count_list is not None

    @property
    def has_select_options(self) -> bool:
        return (self.__ratio_list is not None) or (self.__count_list is not None)

    @property
    def options(self) -> tuple[int, Union[float, int]]:
        if self.has_ratio:
            return WazaBase.TYPE_RATIO, self.__ratio
        elif self.has_count:
            return WazaBase.TYPE_COUNT, self.__count
        else:
            return WazaBase.TYPE_NONE, 0

    def set_next_value(self):
        if self.has_ratio:
            idx = self.__ratio_list.index(self.__ratio) + 1
            if idx >= len(self.__ratio_list):
                idx = 0
            self.__ratio = self.__ratio_list[idx]
        elif self.has_count:
            idx = self.__count_list.index(self.__count) + 1
            if idx >= len(self.__count_list):
                idx = 0
            self.__count = self.__count_list[idx]
