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

    @staticmethod
    def get(type_name: str):
        try:
            return Types[type_name]
        except KeyError:
            return Types.なし

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

# 異常状態
class Ailments(IntEnum):
    なし = 0
    やけど = 1
    こおり = 2
    まひ = 3
    どく = 4
    もうどく = 5
    ねむり =6

class Walls(IntEnum):
    なし = 0
    リフレクター = 1
    ひかりのかべ = 2
    オーロラベール = 3

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


# 特性値定義
ABILITY_VALUES: dict[str, list[str]] = {
    "そうだいしょう": ["1.0", "1.1", "1.2"],
    "こだいかっせい": ["なし", "A", "B", "C", "D", "S"],
    "クォークチャージ": ["なし", "A", "B", "C", "D", "S"],
    "しんりょく": ["無効", "有効"],
    "もうか": ["無効", "有効"],
    "げきりゅう": ["無効", "有効"],
    "スナイパー": ["無効", "有効"],
    "むしのしらせ": ["無効", "有効"],
    "ねつぼうそう": ["無効", "有効"],
    "どくぼうそう": ["無効", "有効"],
    "プラス": ["無効", "有効"],
    "マイナス": ["無効", "有効"],
    "へんげんじざい": ["有効","無効"],
    "リベロ": ["有効","無効"],
    "マルチスケイル": ["有効","無効"],
    "ファントムガード": ["有効","無効"],
    "ふしぎなうろこ": ["有効","無効"],
    "アナライズ": ["有効","無効"],
    "スロースタート": ["有効","無効"],
    "よわき": ["有効","無効"],
}