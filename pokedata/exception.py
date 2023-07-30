from typing import Optional

# フォルム違いが存在するポケモンの番号リスト
exist_few_form_pokemon_no = ["26","50","51","52","53","58","59","79","80","88","89","100","101","128","144","145","146","157","194","199","211","215","479","483","484","487","503","549","550","570","571","628","641","642","645","648","705","706","713","720","724","741","745","849","876","888","889","892","898","902","905","916","952","960"]

# フォルムチェンジ可能なポケモンの番号リスト
changeble_form_in_battle = ["934"]
# パーティ選択時に表示させたくないポケモンリスト
remove_pokemon_name_from_party = ["イルカマン(マイティ)"]
# フォルムの違いはあるが、HOME上では区別されていないポケモンリスト
base_names = ["イルカマン"]

# 選出画面で判別付かないポケモンリスト
unrecognizable_pokemon = ["ウーラオス"]

def get_parameter_for_poketetsu(no:str, form:str) -> str:
    if no in ["26", "50", "51", "53", "88", "89", "641", "642", "645", "905"]:
        if form == "1":
            return "a"
    elif no in ["79", "80", "144", "145", "146", "199"]:
        if form == "1":
            return "g"
    elif no in ["58", "59", "100", "101", "157", "211", "215", "503", "549", "570", "571", "628", "705", "706", "713", "724"]:
        if form == "1":
            return "h"
    elif no in ["483", "484", "487"]:
        if form == "1":
            return "o"
    elif no == "52":
        if form == "1":
            return "a"
        elif form == "2":
            return "g"
    elif no == "80":
        if form == "2":
            return "g"
    elif no == "128":
        if form == "1":
            return "a"
        elif form == "2":
            return "b"
        elif form == "3":
            return "c"
    elif no == "194":
        if form == "1":
            return "p"
    elif no == "479":
        if form == "1":
            return "h"
        elif form == "2":
            return "w"
        elif form == "3":
            return "f"
        elif form == "4":
            return "s"
        elif form == "5":
            return "c"
    elif no == "550":
        if form == "1":
            return "f"
        elif form == "2":
            return "w"
    elif no == "720":
        if form == "1":
            return "u"
    elif no == "741":
        if form == "1":
            return "p"
        elif form == "2":
            return "f"
        elif form == "3":
            return "m"
    elif no == "745":
        if form == "1":
            return "f"
        elif form == "2":
            return "d"
    elif no in ["648", "849", "876", "888", "889", "902", "916", "934"]:
        if form == "1":
            return "f"
    elif no == "892":
        if form == "1":
            return "r"
    elif no == "898":
        if form == "1":
            return "w"
        elif form == "2":
            return "b"
    else:
        return ""

def get_next_form(pid) -> Optional[str]:
    match pid:
        case "934-0":
            return "934-1"
        case "934-1":
            return "934-0"
        case _:
            return None
