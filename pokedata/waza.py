from typing import Optional

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

        self.__add_power = base.value if base.is_add_power else -1
        self.__power_hosei = base.value if base.is_power_hosei else -1
        self.__multi_hit = base.value if base.is_multi_hit else -1
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
    def add_power(self) -> float:
        return self.__add_power

    @property
    def power_hosei(self) -> float:
        return self.__power_hosei

    @property
    def multi_hit(self) -> int:
        return self.__multi_hit
    # endregion

    @staticmethod
    def ByName(name):
        return Waza(db_data=DB.get_waza_data_by_name(name))

    @staticmethod
    def ByWazaBase(base: "WazaBase"):
        return Waza(db_data=DB.get_waza_data_by_name(base.name), base=base)


class WazaBase:
    TYPE_NONE = 0
    TYPE_ADD_POWER = 1
    TYPE_POWER_HOSEI = 2
    TYPE_MULTI_HIT = 3
    TYPE_SELF_BUFF = 11
    TYPE_SELF_DEBUFF = 12
    TYPE_OPPONENT_DEBUFF = 14

    def __init__(self, name):
        self.__name = name
        self.__type: int = WazaBase.TYPE_NONE
        self.__value_list: tuple[float | float] | None = None
        self.__value = None
        self.__critical: bool = False

        # 複数回攻撃
        for k, v in WazaBase.__multi_hit_values.items():
            if name in k:
                self.__type = WazaBase.TYPE_MULTI_HIT
                self.__value_list = v[0]
                self.__value = v[1]
                break

        # 威力増加技
        for k, v in WazaBase.__add_power_values.items():
            if name in k:
                self.__type = WazaBase.TYPE_ADD_POWER
                self.__value_list = v[0]
                self.__value = v[1]
                break

        # 威力補正技
        for k, v in WazaBase.__power_hosei_values.items():
            if name in k:
                self.__type = WazaBase.TYPE_POWER_HOSEI
                self.__value_list = v[0]
                self.__value = v[1]
                break

        # ステータス強化技
        for k, v in WazaBase.__self_buff_values.items():
            if name in k:
                self.__type = WazaBase.TYPE_SELF_BUFF
                self.__value = v
                break

    @property
    def name(self) -> str:
        return self.__name

    @property
    def value(self):
        return self.__value

    @property
    def critical(self) -> bool:
        return self.__critical

    @critical.setter
    def critical(self, value) -> None:
        self.__critical = value

    @property
    def type(self) -> int:
        return self.__type

    @property
    def is_add_power(self) -> bool:
        return self.__type == WazaBase.TYPE_ADD_POWER

    @property
    def is_power_hosei(self) -> bool:
        return self.__type == WazaBase.TYPE_POWER_HOSEI

    @property
    def is_multi_hit(self) -> bool:
        return self.__type == WazaBase.TYPE_MULTI_HIT

    @property
    def is_self_buff(self) -> bool:
        return self.__type == WazaBase.TYPE_SELF_BUFF

    @property
    def has_value_list(self) -> bool:
        return self.__value_list is not None

    def set_next_value(self):
        if self.__value_list is not None:
            idx = self.__value_list.index(self.__value) + 1
            if idx >= len(self.__value_list):
                idx = 0
            self.__value = self.__value_list[idx]

    __multi_hit_values = {
        "タネマシンガン|ロックブラスト|つららばり|スケイルショット|ミサイルばり": (
            (2, 3, 4, 5), 3),
        "ネズミざん": (
            (10, 9, 8, 7, 6, 5, 4, 3, 2, 1), 10),
        "ドラゴンアロー|ダブルウイング": (
            (2,), 2),
    }

    __add_power_values = {
        "ふんどのこぶし": (
            (1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0), 1.0),
        "アクロバット|しっぺがえし": (
            (1.0, 2.0), 2.0),
        "おはかまいり": (
            (1.0, 2.0, 3.0), 3.0),
    }

    __power_hosei_values = {
        "はたきおとす": (
            (1.0, 1.5), 1.5),
    }

    __self_buff_values = {
        "りゅうのまい": "AS+1",
        "つるぎのまい": "A+2",
        "ビルドアップ": "AB+1",
        "のろい": "AB+1 S-1",
        "からをやぶる": "ACS+2 BD-1",
        "めいそう": "CD+1",
        "ちょうのまい": "CDS+1",
        "わるだくみ": "C+2",
        "てっぺき": "B+2",
        "ドわすれ": "D+2",
    }
