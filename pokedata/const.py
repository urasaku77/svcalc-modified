from enum import IntEnum
from pokedata.stats import Stats


# タイプ定義
class Types(IntEnum):
    なし = -1
    ノーマル = 0
    ほのお = 1
    みず = 2
    でんき = 3
    くさ = 4
    こおり = 5
    かくとう = 6
    どく = 7
    じめん = 8
    ひこう = 9
    エスパー = 10
    むし = 11
    いわ = 12
    ゴースト = 13
    ドラゴン = 14
    あく = 15
    はがね = 16
    フェアリー = 17

    @property
    def icon(self):
        return "image/typeicon/" + self.name + ".png"

    @staticmethod
    def all() -> list:
        return [x for x in Types if (1 <= x <= 17)]


# 天候定義
class Weathers(IntEnum):
    なし = 0
    晴れ = 1
    雨 = 2
    砂嵐 = 3
    雪 = 4


# フィールド定義
class Fields(IntEnum):
    なし = 0
    エレキ = 1
    サイコ = 2
    グラス = 3
    ミスト = 4


DORYOKU_PRESET = {
    "ASようき": {"nature": "ようき", "stats": Stats(0).set_values(a=252, s=252)},
    "ASいじっぱり": {"nature": "いじっぱり", "stats": Stats(0).set_values(a=252, s=252)},
    "CSおくびょう": {"nature": "おくびょう", "stats": Stats(0).set_values(c=252, s=252)},
    "CSひかえめ": {"nature": "ひかえめ", "stats": Stats(0).set_values(c=252, s=252)},
    "HAいじっぱり": {"nature": "いじっぱり", "stats": Stats(0).set_values(h=252, a=252)},
    "HBずぶとい": {"nature": "ずぶとい", "stats": Stats(0).set_values(h=252, b=252)},
    "HBわんぱく": {"nature": "わんぱく", "stats": Stats(0).set_values(h=252, b=252)},
    "HCひかえめ": {"nature": "ひかえめ", "stats": Stats(0).set_values(h=252, c=252)},
    "HDしんちょう": {"nature": "しんちょう", "stats": Stats(0).set_values(h=252, d=252)},
    "HDおだやか": {"nature": "おだやか", "stats": Stats(0).set_values(h=252, d=252)},
}


# 技種別定義
物理 = "物理"
特殊 = "特殊"
変化 = "変化"
