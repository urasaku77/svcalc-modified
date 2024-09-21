from typing import Optional

# フォルムチェンジ可能なポケモンの番号リスト
changeble_form_in_battle = [964, 1024]

# 統計上同じポケモンとしてカウントしたいポケモンの番号リスト
same_pokemon_in_stats = [888, 889, 964, 1024]

# パーティ選択時に表示させたくないポケモンリスト
remove_pokemon_name_from_party = [
    "イルカマン(マイティ)",
    "テラパゴス(テラスタル)",
    "テラパゴス(ステラ)",
]
# フォルムの違いはあるが、HOME上では区別されていないポケモンリスト
base_names = ["イルカマン", "イッカネズミ", "オーガポン", "テラパゴス"]

# 選出画面で判別付かないポケモンリスト
unrecognizable_pokemon = ["ウーラオス", "ザシアン", "ザマゼンタ"]

# 選出画面で判別付かないポケモン+途中で姿が変わるポケモンの番号
unrecognizable_pokemon_no = [888, 889, 892, 964, 1024]

# 選出画面で判別付かないポケモンでHOME上区別がないポケモン
unrecognizable_and_same_pokemon_in_home = ["ザシアン", "ザマゼンタ"]


def get_next_form(pid: str) -> Optional[str]:
    match pid:
        case "964-0":
            return "964-1"
        case "964-1":
            return "964-0"
        case "1024-0":
            return "1024-1"
        case "1024-1":
            return "1024-2"
        case "1024-2":
            return "1024-1"
        case _:
            return None


def check_pokemon_form(pid: str):
    if pid == "-1--1":
        return "-1"
    elif any(str(pokemon) in pid for pokemon in same_pokemon_in_stats):
        return pid[:-1] + "0"
    else:
        return pid
