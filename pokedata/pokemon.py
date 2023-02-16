from __future__ import annotations
import math
from decimal import Decimal
from typing import Optional

from pokedata.const import *
from data.db import DB
from pokedata.nature import get_seikaku_hosei
from pokedata.stats import Stats, StatsKey
from pokedata.waza import Waza, WazaBase
from pokedata.const import ABILITY_VALUES


class Pokemon:

    def __init__(self, db_data=None):
        self.__no: int = -1
        self.__form: int = -1
        self.__name: str = ""
        self.__lv: int = 50
        self.__base_name: str = ""
        self.__form_name: str = ""
        self.__syuzoku: Stats = Stats(0)
        self.__kotai: Stats = Stats(31)
        self.__doryoku: Stats = Stats(0)
        self.__rank: Stats = Stats(0)
        self.__seikaku: str = "まじめ"
        self.__item: str = "なし"
        self.__type: list[Types] = []
        self.__terastype: Types = Types.なし
        self.__battle_terastype: Types = Types.なし
        self.__abilities: list[str] = [""]
        self.__ability: str = self.__abilities[0]
        self.__ability_value: str = ""
        self.__ailment: Ailments = Ailments.なし
        self.__charging: bool = False
        self.__waza_list: list[Optional[WazaBase]] = [None for _ in range(10)]
        self.__waza_rate_list: list[Optional[float]] = [0.0 for _ in range(10)]
        self.__weight: float = 0.0
        self.__statechanged_handler: Optional[callable] = None

        if db_data is not None:
            self.__no = db_data['no']
            self.__form = db_data['form']
            self.__name = db_data['name']
            self.__base_name: str = db_data['base_name']
            self.__form_name: str = db_data['form_name']
            self.__syuzoku.set_values(
                h=db_data['H'], a=db_data['A'], b=db_data['B'],
                c=db_data['C'], d=db_data['D'], s=db_data['S'])
            self.__type.append(Types[db_data['type1']])
            if len(db_data['type2']) > 0:
                self.__type.append(Types[db_data['type2']])
            for key in ["ability1", "ability2", "ability3"]:
                if len(db_data[key]) > 0:
                    self.__abilities.append(db_data[key])
            self.__ability: str = self.__abilities[0]
            self.__weight: float = db_data['weight']

    def __getitem__(self, key: StatsKey) -> int:
        match key:
            case StatsKey.H:
                return self.__get_stats(StatsKey.H)
            case StatsKey.A | StatsKey.B | StatsKey.C | StatsKey.D | StatsKey.S:
                value = self.__get_stats(key)
                return value

    @staticmethod
    def by_name(name: str, default=False) -> Pokemon:
        pokemon = Pokemon(DB.get_pokemon_data_by_name(name))
        if default:
            pokemon.set_default_data()
        return pokemon

    @staticmethod
    def by_pid(pid: str, default=False) -> Pokemon:
        pokemon = Pokemon(DB.get_pokemon_data_by_pid(pid))
        if default:
            pokemon.set_default_data()
        return pokemon

    # region プロパティ
    @property
    def pid(self) -> str:
        return str(self.__no) + "-" + str(self.__form)

    @property
    def icon(self) -> str:
        return "image/pokeicon/" + self.pid + ".png"

    @property
    def name(self) -> str:
        return self.__name

    @property
    def type(self) -> list[Types]:
        return self.__type

    @property
    def terastype(self) -> Types:
        return self.__terastype

    @terastype.setter
    def terastype(self, value: Types):
        self.__terastype = value

    @property
    def battle_terastype(self) -> Types:
        return self.__battle_terastype

    @battle_terastype.setter
    def battle_terastype(self, value: Types):
        self.__battle_terastype = value
        self.statechanged()

    @property
    def lv(self) -> int:
        return self.__lv

    @property
    def syuzoku(self) -> Stats:
        return self.__syuzoku

    @property
    def kotai(self) -> Stats:
        return self.__kotai

    @property
    def doryoku(self) -> Stats:
        return self.__doryoku

    @doryoku.setter
    def doryoku(self, value) -> None:
        self.__doryoku.set_values_from_stats(value)
        self.statechanged()

    @property
    def rank(self) -> Stats:
        return self.__rank

    @property
    def seikaku(self) -> str:
        return self.__seikaku

    @seikaku.setter
    def seikaku(self, value) -> None:
        self.__seikaku = value
        self.statechanged()

    @property
    def item(self) -> str:
        return self.__item

    @item.setter
    def item(self, value) -> None:
        self.__item = value
        self.statechanged()

    @property
    def ability(self) -> str:
        return self.__ability

    @ability.setter
    def ability(self, value) -> None:
        self.__ability = value
        self.set_default_ability_value()
        self.statechanged()

    @property
    def ailment(self) -> str:
        return self.__ailment

    @ailment.setter
    def ailment(self, value) -> None:
        self.__ailment = value
        self.statechanged()

    @property
    def charging(self) -> str:
        return self.__charging

    @charging.setter
    def charging(self, value) -> None:
        self.__charging = value
        self.statechanged()

    @property
    def abilities(self) -> list[str]:
        return self.__abilities

    @property
    def rankedA(self) -> int:
        return self.get_ranked_stats(StatsKey.A)

    @property
    def rankedB(self) -> int:
        return self.get_ranked_stats(StatsKey.B)

    @property
    def rankedC(self) -> int:
        return self.get_ranked_stats(StatsKey.C)

    @property
    def rankedD(self) -> int:
        return self.get_ranked_stats(StatsKey.D)

    @property
    def rankedS(self) -> int:
        return self.get_ranked_stats(StatsKey.S)

    @property
    def ability_value(self) -> str:
        return self.__ability_value

    @ability_value.setter
    def ability_value(self, value: str):
        self.__ability_value = value
        self.statechanged()

    @property
    def ability_enable(self) -> bool:
        return self.__ability_value == "有効"

    @property
    def waza_list(self) -> list[WazaBase]:
        return self.__waza_list

    @property
    def waza_rate_list(self) -> list[float]:
        return self.__waza_rate_list

    @property
    def weight(self) -> float:
        return self.__weight

    @property
    def status_text(self) -> str:
        return "-".join([str(self.__get_stats(x)) for x in StatsKey])

    @property
    def marked_status_text(self) -> str:
        text = ""
        for key in StatsKey:
            value = get_seikaku_hosei(self.__seikaku, key)
            if value == 1.1:
                text += "[color=#ffc0cb]" + str(self.get_ranked_stats(key)) + "[/color]-"
            elif value == 0.9:
                text += "[color=#add8e6]" + str(self.get_ranked_stats(key)) + "[/color]-"
            else:
                text += str(self.get_ranked_stats(key)) + "-"
        return text[:-1]

    @property
    def to_string(self) -> str:
        return "{0}@{1} {2}".format(self.name, self.item, self.status_text)

    @property
    def statechanged_handler(self) -> callable:
        return self.__statechanged_handler

    @property
    def next_form_pid(self) -> Optional[str]:
        match self.pid:
            case "934-0":
                return "934-1"
            case "934-1":
                return "934-0"
            case _:
                return None

    @property
    def next_form_icon(self) -> str:
        form_pid = self.next_form_pid
        return "image/pokeicon/" + form_pid + ".png" if form_pid is not None else ""

    @statechanged_handler.setter
    def statechanged_handler(self, handler: Optional[callable]):
        self.__statechanged_handler = handler

    @property
    def is_empty(self) -> bool:
        return self.__no == -1

    @property
    def is_flying(self) -> bool:
        return (Types.ひこう in self.__type) or self.__ability == "ふゆう" or self.__item == "ふうせん"
    # endregion

    # 実数値
    def __get_stats(self, key: StatsKey) -> int:
        if key == StatsKey.H:
            value = (self.__syuzoku[key] * 2) + self.kotai[key] + math.floor(self.doryoku[key] / 4)
            return math.floor(value * self.__lv / 100) + 10 + self.__lv
        else:
            value = (self.__syuzoku[key] * 2) + self.kotai[key] + math.floor(self.doryoku[key] / 4)
            value = math.floor(value * self.__lv / 100) + 5
            value = math.floor(value * get_seikaku_hosei(self.__seikaku, key))
            return value

    # 最も高い実数値のキーを返す（こだいかっせい、クォークチャージ用）
    def __get_best_stats_key(self) -> StatsKey:
        max_key = StatsKey.A
        max_value = self.__get_stats(StatsKey.A)
        for key in [StatsKey.B, StatsKey.C, StatsKey.D, StatsKey.S]:
            value = self.__get_stats(key)
            if max_value < value:
                max_key = key
                max_value = value
        return max_key

    # 実数値(ランク補正込み)
    def get_ranked_stats(self, key: StatsKey) -> int:
        stats = self[key]
        rank = self.__rank[key]
        if rank > 0:
            stats = math.floor(stats / 2 * (2 + rank))
        elif rank < 0:
            stats = math.floor(stats / (2 - rank) * 2)
        return stats

    # デフォルトデータ設定
    def set_default_data(self):
        from pokedata.loader import get_default_data
        data = get_default_data(self.name)
        self.set_load_data(data, False)
        self.set_waza_from_home()

    # CSV読み込みデータの設定
    def set_load_data(self, data, use_data:bool):
        if len(data):
            self.__kotai.set_values_from_string(data[1])
            self.__doryoku.set_values_from_string(data[2])
            self.__seikaku = data[3]
            self.__item = data[4]
            self.__ability = data[5]
            self.__terastype = Types[data[6]] if data[6] != "" else Types.なし
            if use_data:
                for i in range(10):
                    if i+7 < len(data):
                        self.__waza_list[i] = WazaBase(data[i+7])

    def set_waza_from_home(self):
        from pokedata.loader import get_home_data
        waza_data = get_home_data(self.name, "./home/home_waza.csv")
        for i in range(len(waza_data)):
            self.__waza_list[i] = WazaBase(waza_data[i][0])
            self.__waza_rate_list[i] = waza_data[i][1]

    # タイプ相性値
    # テラスタイプがある場合、そのタイプで算出
    def get_type_effective(self, waza: Waza) -> float:
        value = Decimal(1.0)
        types: list[Types] = self.type if self.battle_terastype == Types.なし else [self.battle_terastype]
        for type_effective in DB.get_type_effective(waza.type, types):
            match waza.name:
                case "フリーズドライ":
                    if type_effective.df_type == Types.みず:
                        value = value * Decimal(2.0)
                    else:
                        value = value * Decimal(type_effective.value)
                case "サウザンアロー":
                    if type_effective.df_type == Types.じめん:
                        value = value * Decimal(2.0)
                    else:
                        value = value * Decimal(type_effective.value)
                case _:
                    value = value * Decimal(type_effective.value)
        return float(value)

    # 技の編集
    def set_waza(self, index: int, waza_name: str):
        if len(waza_name) == 0:
            self.__waza_list[index] = None
        elif index < len(self.__waza_list):
            self.__waza_list[index] = WazaBase(waza_name)
        else:
            self.__waza_list.append(WazaBase(waza_name))
        self.statechanged()

    # 技の回数、威力などの編集
    def use_waza_effect(self, index):
        wazabase = self.__waza_list[index]
        if wazabase is not None:
            if wazabase.has_value_list:
                wazabase.set_next_value()
                self.statechanged()
            elif wazabase.is_self_buff:
                self.__rank.add_values_from_string(wazabase.value, True)
                self.statechanged()

    # 対象のタイプを持っているか（テラスタイプの場合含む）
    def has_type(self, _type: Types) -> bool:
        if self.battle_terastype is not None:
            return _type == self.__battle_terastype
        else:
            return _type in self.__type

    # 値が変化した時の通知
    def statechanged(self):
        if self.__statechanged_handler is not None:
            self.__statechanged_handler()

    # デフォルトの性格、努力値の設定
    def set_default_evs(self):
        max_key: StatsKey = StatsKey.A
        for key in [x for x in StatsKey if x != StatsKey.H and x != StatsKey.A]:
            if self.__syuzoku[key] > self.__syuzoku[max_key]:
                max_key = key

        match max_key:
            case StatsKey.A:
                if self.__syuzoku.H > self.__syuzoku.S:
                    self.__seikaku = "いじっぱり"
                    self.__doryoku.set_values(a=252, h=252)
                else:
                    self.__seikaku = "ようき"
                    self.__doryoku.set_values(a=252, s=252)
            case StatsKey.B:
                if self.__syuzoku.A > self.__syuzoku.C:
                    self.__seikaku = "わんぱく"
                else:
                    self.__seikaku = "ずぶとい"
                self.__doryoku.set_values(h=252, b=252)
            case StatsKey.C:
                if self.__syuzoku.H > self.__syuzoku.S:
                    self.__seikaku = "ひかえめ"
                    self.__doryoku.set_values(c=252, h=252)
                else:
                    self.__seikaku = "おくびょう"
                    self.__doryoku.set_values(c=252, s=252)
            case StatsKey.D:
                if self.__syuzoku.A > self.__syuzoku.C:
                    self.__seikaku = "しんちょう"
                else:
                    self.__seikaku = "おだやか"
                self.__doryoku.set_values(h=252, d=252)
            case StatsKey.S:
                if self.__syuzoku.A > self.__syuzoku.C:
                    self.__seikaku = "ようき"
                    self.__doryoku.set_values(a=252, s=252)
                else:
                    self.__seikaku = "おくびょう"
                    self.__doryoku.set_values(c=252, s=252)

    def set_doryoku_preset(self, value):
        from pokedata import const
        preset = const.DORYOKU_PRESET[value]
        self.__seikaku = preset["nature"]
        self.__doryoku.set_values_from_stats(preset["stats"])
        self.statechanged()

    def form_change(self):
        form_id = self.next_form_pid
        if form_id is not None:
            next_form = Pokemon.by_pid(form_id)
            self.__form = next_form.__form
            self.__form_name = next_form.__form_name
            self.__syuzoku.set_values_from_stats(next_form.syuzoku)
            self.__ability = next_form.ability
            self.__type = list(next_form.type)
            self.statechanged()

    def on_stage(self):
        self.__rank = Stats(init_value=0)
        self.set_default_ability_value()

    def set_default_ability_value(self):
        for k, v in ABILITY_VALUES.items():
            if self.__ability == k:
                self.__ability_value = v[0]
