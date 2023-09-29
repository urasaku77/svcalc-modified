from typing import Optional

# フォルムチェンジ可能なポケモンの番号リスト
changeble_form_in_battle = ["934"]
# パーティ選択時に表示させたくないポケモンリスト
remove_pokemon_name_from_party = ["イルカマン(マイティ)"]
# フォルムの違いはあるが、HOME上では区別されていないポケモンリスト
base_names = ["イルカマン"]

# 選出画面で判別付かないポケモンリスト
unrecognizable_pokemon = ["ウーラオス"]

def get_next_form(pid) -> Optional[str]:
    match pid:
        case "934-0":
            return "934-1"
        case "934-1":
            return "934-0"
        case _:
            return None
