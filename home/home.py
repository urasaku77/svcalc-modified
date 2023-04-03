import os
import json
import csv
import urllib.request
import jaconv
from typing import Optional

exist_few_form_pokemon_no = ["128","194","479","550","741","745","849","876","916"]
changeble_form_in_battle = ["934"]

remove_pokemon_name_from_party = ["イルカマン(マイティ)"]
base_names = ["イルカマン"]

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
    else:
        return ""

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
    elif no in ["849", "876", "916", "934"]:
        if form == "1":
            return "f"
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

class home():
    cid = ""
    rst = 0
    ts2 = ""
    pdetail = {}

    print("ランクマッチ情報取得")
    url = 'https://api.battle.pokemon-home.com/tt/cbd/competition/rankmatch/list'
    headers = {
        "accept": "application/json, text/javascript, */*",
        "countrycode": 304,
        "authorization": "Bearer",
        "langcode": 1,
        "user-agent": "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Mobile Safari/537.36",
        "content-type": "application/json"
    }
    param = {
        "soft":"Sc"
    }
    req = urllib.request.Request(url, json.dumps(param).encode(), headers)
    with urllib.request.urlopen(req) as res:
        rankmatch_list = json.load(res)
        cid = 0
        for item in rankmatch_list["list"][next(iter(rankmatch_list["list"]))]:
            if rankmatch_list["list"][next(iter(rankmatch_list["list"]))][item]['rule'] == 0:
                cid = item
        rst = rankmatch_list["list"][next(iter(rankmatch_list["list"]))][cid]["rst"]
        ts2 = rankmatch_list["list"][next(iter(rankmatch_list["list"]))][cid]["ts2"]

    print("ポケモン情報取得")
    for i in range(1,7):
        url = 'https://resource.pokemon-home.com/battledata/ranking/scvi/'+str(cid)+"/"+str(rst)+"/"+str(ts2)+"/pdetail-"+str(i)
        headers = {
            "accept": "application/json, text/javascript, */*",
            "user-agent": "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Mobile Safari/537.36",
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as res:
            pdetail_tmp = json.load(res)
            pdetail = dict(pdetail, **pdetail_tmp)

    pokedex = ""
    with open('home/bundle.json', 'r',encoding="utf-8") as json_open:
        pokedex = json.load(json_open)

    if os.path.isfile('home/home_waza.csv') == True:
        os.remove('home/home_waza.csv')
    if os.path.isfile('home/home_tokusei.csv') == True:
        os.remove('home/home_tokusei.csv')
    if os.path.isfile('home/home_seikaku.csv') == True:
        os.remove('home/home_seikaku.csv')
    if os.path.isfile('home/home_motimono.csv') == True:
        os.remove('home/home_motimono.csv')
    if os.path.isfile('home/home_terastal.csv') == True:
        os.remove('home/home_terastal.csv')

    print("CSV更新")
    for pokenum in pdetail.keys():
        for p_detail_id in pdetail[pokenum].keys():
            name = ""
            if pokenum in exist_few_form_pokemon_no:
                name = get_pokemon_name_for_home(pokenum, p_detail_id)
            else:
                name = pokedex['poke'][int(pokenum) -1]

            with open('home/home_waza.csv', 'a',encoding="utf-8") as waza_csv:
                for waza in pdetail[pokenum][p_detail_id]['temoti']['waza']:
                        writer = csv.writer(waza_csv, lineterminator="\n")
                        writer.writerow([name, jaconv.z2h(pokedex['waza'][waza['id']],kana=False,digit=True, ascii=True),waza['val']])

            with open('home/home_tokusei.csv', 'a',encoding="utf-8") as tokusei_csv:
                for tokusei in pdetail[pokenum][p_detail_id]['temoti']['tokusei']:
                        writer = csv.writer(tokusei_csv, lineterminator="\n")
                        writer.writerow([name, jaconv.z2h(pokedex['tokusei'][tokusei['id']],kana=False,digit=True, ascii=True),tokusei['val']])

            with open('home/home_seikaku.csv', 'a',encoding="utf-8") as seikaku_csv:
                for seikaku in pdetail[pokenum][p_detail_id]['temoti']['seikaku']:
                        writer = csv.writer(seikaku_csv, lineterminator="\n")
                        writer.writerow([name, jaconv.z2h(pokedex['seikaku'][seikaku['id']],kana=False,digit=True, ascii=True),seikaku['val']])

            with open('home/home_motimono.csv', 'a',encoding="utf-8") as motimono_csv:
                for motimono in pdetail[pokenum][p_detail_id]['temoti']['motimono']:
                        writer = csv.writer(motimono_csv, lineterminator="\n")
                        writer.writerow([name, jaconv.z2h(pokedex['itemname'][motimono['id']],kana=False,digit=True, ascii=True),motimono['val']])

            with open('home/home_terastal.csv', 'a',encoding="utf-8") as terastal_csv:
                for terastal in pdetail[pokenum][p_detail_id]['temoti']['terastal']:
                        writer = csv.writer(terastal_csv, lineterminator="\n")
                        writer.writerow([name, pokedex['pokeType'][int(terastal['id'])],terastal['val']])
    print("CSV更新完了")
