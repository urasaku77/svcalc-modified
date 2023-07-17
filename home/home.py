import os
import json
import csv
import urllib.request
import jaconv
from typing import Optional

# フォルム違いが存在するポケモンの番号リスト
exist_few_form_pokemon_no = ["26","50","51","52","53","58","59","79","80","88","89","101","128","144","145","146","157","194","211","215","479","483","484","487","503","549","550","628","641","642","645","648","705","706","713","720","724","741","745","849","876","888","889","892","898","902","905","916","952","960"]

# フォルムチェンジ可能なポケモンの番号リスト
changeble_form_in_battle = ["934"]
# パーティ選択時に表示させたくないポケモンリスト
remove_pokemon_name_from_party = ["イルカマン(マイティ)"]
# フォルムの違いはあるが、HOME上では区別されていないポケモンリスト
base_names = ["イルカマン"]

# 選出画面で判別付かないポケモンリスト
unrecognizable_pokemon = ["ウーラオス"]

def get_pokemon_name_for_home(pokenum:str, p_detail_id:str) -> str:
    if pokenum == "26":
        if p_detail_id == "0":
            return "ライチュウ"
        elif p_detail_id == "1":
            return "アローラライチュウ"
    elif pokenum == "50":
        if p_detail_id == "0":
            return "ディグダ"
        elif p_detail_id == "1":
            return "アローラディグダ"
    elif pokenum == "51":
        if p_detail_id == "0":
            return "ダグトリオ"
        elif p_detail_id == "1":
            return "アローラダグトリオ"
    elif pokenum == "52":
        if p_detail_id == "0":
            return "ニャース"
        elif p_detail_id == "1":
            return "アローラニャース"
        elif p_detail_id == "2":
            return "ガラルニャース"
    elif pokenum == "53":
        if p_detail_id == "0":
            return "ペルシアン"
        elif p_detail_id == "1":
            return "アローラペルシアン"
    elif pokenum == "58":
        if p_detail_id == "0":
            return "ガーディ"
        elif p_detail_id == "1":
            return "ガーディ(ヒスイ)"
    elif pokenum == "59":
        if p_detail_id == "0":
            return "ウインディ"
        elif p_detail_id == "1":
            return "ウインディ(ヒスイ)"
    elif pokenum == "79":
        if p_detail_id == "0":
            return "ヤドン"
        elif p_detail_id == "1":
            return "ガラルヤドン"
    elif pokenum == "80":
        if p_detail_id == "0":
            return "ヤドラン"
        elif p_detail_id == "1":
            return "ガラルヤドラン"
    elif pokenum == "88":
        if p_detail_id == "0":
            return "ベトベター"
        elif p_detail_id == "1":
            return "アローラベトベター"
    elif pokenum == "89":
        if p_detail_id == "0":
            return "ベトベトン"
        elif p_detail_id == "1":
            return "アローラベトベトン"
    elif pokenum == "100":
        if p_detail_id == "0":
            return "ビリリダマ"
        elif p_detail_id == "1":
            return "ビリリダマ(ヒスイ)"
    elif pokenum == "101":
        if p_detail_id == "0":
            return "マルマイン"
        elif p_detail_id == "1":
            return "マルマイン(ヒスイ)"
    elif pokenum == "128":
        if p_detail_id == "0":
            return "ケンタロス"
        elif p_detail_id == "1":
            return "ケンタロス(パルデア単)"
        elif p_detail_id == "2":
            return "ケンタロス(パルデア炎)"
        elif p_detail_id == "3":
            return "ケンタロス(パルデア水)"
    elif pokenum == "144":
        if p_detail_id == "0":
            return "フリーザー"
        elif p_detail_id == "1":
            return "ガラルフリーザー"
    elif pokenum == "145":
        if p_detail_id == "0":
            return "サンダー"
        elif p_detail_id == "1":
            return "ガラルサンダー"
    elif pokenum == "146":
        if p_detail_id == "0":
            return "ファイヤー"
        elif p_detail_id == "1":
            return "ガラルファイヤー"
    elif pokenum == "157":
        if p_detail_id == "0":
            return "バクフーン"
        elif p_detail_id == "1":
            return "バクフーン(ヒスイ)"
    elif pokenum == "194":
        if p_detail_id == "0":
            return "ウパー"
        elif p_detail_id == "1":
            return "ウパー(パルデア)"
    elif pokenum == "199":
        if p_detail_id == "0":
            return "ヤドキング"
        elif p_detail_id == "1":
            return "ガラルヤドキング"
    elif pokenum == "211":
        if p_detail_id == "0":
            return "ハリーセン"
        elif p_detail_id == "1":
            return "ハリーセン(ヒスイ)"
    elif pokenum == "215":
        if p_detail_id == "0":
            return "ニューラ"
        elif p_detail_id == "1":
            return "ニューラ(ヒスイ)"
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
    elif pokenum == "483":
        if p_detail_id == "0":
            return "ディアルガ"
        elif p_detail_id == "1":
            return "ディアルガ(オリジン)"
    elif pokenum == "484":
        if p_detail_id == "0":
            return "パルキア"
        elif p_detail_id == "1":
            return "パルキア(オリジン)"
    elif pokenum == "487":
        if p_detail_id == "0":
            return "ギラティナ(アナザー)"
        elif p_detail_id == "1":
            return "ギラティナ(オリジン)"
    elif pokenum == "503":
        if p_detail_id == "0":
            return "ダイケンキ"
        elif p_detail_id == "1":
            return "ダイケンキ(ヒスイ)"
    elif pokenum == "549":
        if p_detail_id == "0":
            return "ドレディア"
        elif p_detail_id == "1":
            return "ドレディア(ヒスイ)"
    elif pokenum == "550":
        if p_detail_id == "0":
            return "バスラオ(赤)"
        elif p_detail_id == "1":
            return "バスラオ(青)"
        elif p_detail_id == "2":
            return "バスラオ(白)"
    elif pokenum == "628":
        if p_detail_id == "0":
            return "ウォーグル"
        elif p_detail_id == "1":
            return "ウォーグル(ヒスイ)"
    elif pokenum == "641":
        if p_detail_id == "0":
            return "トルネロス(化身)"
        elif p_detail_id == "1":
            return "トルネロス(霊獣)"
    elif pokenum == "642":
        if p_detail_id == "0":
            return "ボルトロス(化身)"
        elif p_detail_id == "1":
            return "ボルトロス(霊獣)"
    elif pokenum == "645":
        if p_detail_id == "0":
            return "ランドロス(化身)"
        elif p_detail_id == "1":
            return "ランドロス(霊獣)"
    elif pokenum == "648":
        if p_detail_id == "0":
            return "メロエッタ(ボイス)"
        elif p_detail_id == "1":
            return "メロエッタ(ステップ)"
    elif pokenum == "705":
        if p_detail_id == "0":
            return "ヌメイル"
        elif p_detail_id == "1":
            return "ヌメイル(ヒスイ)"
    elif pokenum == "706":
        if p_detail_id == "0":
            return "ヌメルゴン"
        elif p_detail_id == "1":
            return "ヌメルゴン(ヒスイ)"
    elif pokenum == "713":
        if p_detail_id == "0":
            return "クレベース"
        elif p_detail_id == "1":
            return "クレベース(ヒスイ)"
    elif pokenum == "720":
        if p_detail_id == "0":
            return "フーパ(いましめ)"
        elif p_detail_id == "1":
            return "フーパ(ときはな)"
    elif pokenum == "724":
        if p_detail_id == "0":
            return "ジュナイパー"
        elif p_detail_id == "1":
            return "ジュナイパー(ヒスイ)"
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
    elif pokenum == "888":
        if p_detail_id == "0":
            return "ザシアン"
        elif p_detail_id == "1":
            return "ザシアン(王)"
    elif pokenum == "889":
        if p_detail_id == "0":
            return "ザマゼンタ"
        elif p_detail_id == "1":
            return "ザマゼンタ(王)"
    elif pokenum == "892":
        if p_detail_id == "0":
            return "ウーラオス(いちげき)"
        elif p_detail_id == "1":
            return "ウーラオス(れんげき)"
    elif pokenum == "898":
        if p_detail_id == "0":
            return "バドレックス"
        elif p_detail_id == "1":
            return "バドレックス(白馬)"
        elif p_detail_id == "2":
            return "バドレックス(黒馬)"
    elif pokenum == "902":
        if p_detail_id == "0":
            return "イダイトウ♂"
        else:
            return "イダイトウ♀"
    elif pokenum == "905":
        if p_detail_id == "0":
            return "ラブトロス(化身)"
        elif p_detail_id == "1":
            return "ラブトロス(霊獣)"
    elif pokenum == "916":
        if p_detail_id == "0":
            return "パフュートン♂"
        else:
            return "パフュートン♀"
    elif pokenum == "952":
        if p_detail_id == "0":
            return "シャリタツ(そったすがた)"
        elif p_detail_id == "1":
            return "シャリタツ(たれたすがた)"
        elif p_detail_id == "2":
            return "シャリタツ(のびたすがた)"
    elif pokenum == "960":
        if p_detail_id == "0":
            return "イキリンコ(緑)"
        elif p_detail_id == "1":
            return "イキリンコ(青)"
        elif p_detail_id == "2":
            return "イキリンコ(黄)"
        elif p_detail_id == "3":
            return "イキリンコ(白)"
    else:
        return ""

def get_parameter_for_poketetsu(no:str, form:str) -> str:
    if no in ["26", "50", "51", "53", "88", "89", "641", "642", "645", "905"]:
        if form == "1":
            return "a"
    elif no in ["79", "80", "144", "145", "146", "199"]:
        if form == "1":
            return "g"
    elif no in ["58", "59", "100", "101", "157", "211", "215", "503", "549", "628", "705", "706", "713", "724"]:
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
