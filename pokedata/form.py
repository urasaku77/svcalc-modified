exist_few_form_pokemon_no = ["128","194","479","550","741","745","849","876","916"]

def get_pokemon_name_for_home(pokenum:str, p_detail_id:str) -> str:
    if pokenum == "128":
        if p_detail_id == "1":
            return "ケンタロス(パルデア単)"
        elif p_detail_id == "2":
            return "ケンタロス(パルデア炎)"
        elif p_detail_id == "3":
            return "ケンタロス(パルデア水)"
    elif pokenum == "194":
        if p_detail_id == "0":
            return "ウパー"
        elif p_detail_id == "1":
            return "ウパー(パルデア)"
    elif pokenum == "479":
        if p_detail_id == "0":
            return "ロトム"
        elif p_detail_id == "1":
            return "ヒートロトム"
        elif p_detail_id == "2":
            return "ウォッシュロトム"
        elif p_detail_id == "3":
            return "フロストロトム"
        elif p_detail_id == "4":
            return "スピンロトム"
        elif p_detail_id == "5":
            return "カットロトム"
    elif pokenum == "550":
        if p_detail_id == "0":
            return "バスラオ(赤)"
        elif p_detail_id == "1":
            return "バスラオ(青)"
        elif p_detail_id == "2":
            return "バスラオ(白)"
    elif pokenum == "741":
        if p_detail_id == "0":
            return "オドリドリ(めらめら)"
        elif p_detail_id == "1":
            return "オドリドリ(ぱちぱち)"
        elif p_detail_id == "2":
            return "オドリドリ(ふらふら)"
        elif p_detail_id == "3":
            return "オドリドリ(まいまい)"
    elif pokenum == "745":
        if p_detail_id == "0":
            return "ルガルガン(まひる)"
        elif p_detail_id == "1":
            return "ルガルガン(まよなか)"
        elif p_detail_id == "2":
            return "ルガルガン(たそがれ)"
    elif pokenum == "849":
        if p_detail_id == "0":
            return "ストリンダー(ハイ)"
        elif p_detail_id == "1":
            return "ストリンダー(ロー)"
    elif pokenum == "876":
        if p_detail_id == "0":
            return "イエッサン♂"
        else:
            return "イエッサン♀"
    elif pokenum == "916":
        if p_detail_id == "0":
            return "パフュートン♂"
        else:
            return "パフュートン♀"

def get_parameter_for_poketetsu(no:str, form:str) -> str:
    if no == "128":
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
    elif no == "849":
        if form == "1":
            return "f"
    elif no == "876":
        if form == "1":
            return "f"
    elif no == "916":
        if form == "1":
            return "f"
