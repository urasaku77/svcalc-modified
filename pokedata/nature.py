from collections import namedtuple

from pokedata.stats import Stats, StatsKey

__Nature = namedtuple('Nature', ['up', 'down'])
__natures = {
    "さみしがり": __Nature(StatsKey.A, StatsKey.B),
    "いじっぱり": __Nature(StatsKey.A, StatsKey.C),
    "やんちゃ": __Nature(StatsKey.A, StatsKey.D),
    "ゆうかん": __Nature(StatsKey.A, StatsKey.S),

    "ずぶとい": __Nature(StatsKey.B, StatsKey.A),
    "わんぱく": __Nature(StatsKey.B, StatsKey.C),
    "のうてんき": __Nature(StatsKey.B, StatsKey.D),
    "のんき": __Nature(StatsKey.B, StatsKey.S),

    "ひかえめ": __Nature(StatsKey.C, StatsKey.A),
    "おっとり": __Nature(StatsKey.C, StatsKey.B),
    "うっかりや": __Nature(StatsKey.C, StatsKey.D),
    "れいせい": __Nature(StatsKey.C, StatsKey.S),

    "おだやか": __Nature(StatsKey.D, StatsKey.A),
    "おとなしい": __Nature(StatsKey.D, StatsKey.B),
    "しんちょう": __Nature(StatsKey.D, StatsKey.C),
    "なまいき": __Nature(StatsKey.D, StatsKey.S),

    "おくびょう": __Nature(StatsKey.S, StatsKey.A),
    "せっかち": __Nature(StatsKey.S, StatsKey.B),
    "ようき": __Nature(StatsKey.S, StatsKey.C),
    "むじゃき": __Nature(StatsKey.S, StatsKey.D),
}

def get_seikaku_list() -> list[str]:
    return  [x for x in __natures.keys()]

def get_seikaku_hosei(seikaku: str, key: StatsKey) -> float:
    if seikaku not in __natures:
        return 1.0
    values: __Nature = __natures[seikaku]
    return 1.1 if values.up == key else 0.9 if values.down == key else 1.0


def get_default_doryoku(seikaku: str, syuzoku: Stats) -> Stats:
    doryoku = Stats()
    if seikaku == "ようき":
        doryoku.set_values(a=252, s=252)
    if seikaku == "おくびょう":
        doryoku.set_values(c=252, s=252)
    if seikaku == "ゆうかん":
        doryoku.set_values(h=252, a=252)
    if seikaku == "れいせい":
        doryoku.set_values(h=252, c=252)
    if seikaku in ["ずぶとい", "わんぱく", "のんき"]:
        doryoku.set_values(h=252, b=252)
    if seikaku in ["おだやか", "しんちょう", "なまいき"]:
        doryoku.set_values(h=252, d=252)
    if seikaku in ["いじっぱり", "さみしがり", "やんちゃ"]:
        doryoku.set_values(a=252, s=252 if syuzoku.S >= 90 else 0, h=252 if syuzoku.S < 90 else 0)
    if seikaku in ["ひかえめ", "おっとり", "うっかりや"]:
        doryoku.set_values(c=252, s=252 if syuzoku.S >= 90 else 0, h=252 if syuzoku.S < 90 else 0)
    if seikaku in ["せっかち", "むじゃき"]:
        doryoku.set_values(a=252 if syuzoku.A > syuzoku.C else 0, c=252 if syuzoku.C > syuzoku.A else 0, s=252)
    return doryoku
