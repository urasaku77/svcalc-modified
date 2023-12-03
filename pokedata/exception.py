from typing import Optional

# フォルムチェンジ可能なポケモンの番号リスト
changeble_form_in_battle = [964]
# パーティ選択時に表示させたくないポケモンリスト
remove_pokemon_name_from_party = ["イルカマン(マイティ)"]
# フォルムの違いはあるが、HOME上では区別されていないポケモンリスト
base_names = ["イルカマン", "オーガポン"]

# 選出画面で判別付かないポケモンリスト
unrecognizable_pokemon = ["ウーラオス"]

def get_next_form(pid: str) -> Optional[str]:
    match pid:
        case "964-0":
            return "964-1"
        case "964-1":
            return "964-0"
        case _:
            return None
