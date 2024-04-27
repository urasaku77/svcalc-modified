#!python3.10
import csv
import json
import os
import urllib.request

import jaconv


def get_pokemon_name_for_home(pokenum: str, p_detail_id: str) -> str:
    if pokenum == "26":
        if p_detail_id == "0":
            return "ライチュウ"
        elif p_detail_id == "1":
            return "アローラライチュウ"
    elif pokenum == "27":
        if p_detail_id == "0":
            return "サンド"
        elif p_detail_id == "1":
            return "アローラサンド"
    elif pokenum == "28":
        if p_detail_id == "0":
            return "サンドパン"
        elif p_detail_id == "1":
            return "アローラサンドパン"
    elif pokenum == "37":
        if p_detail_id == "0":
            return "ロコン"
        elif p_detail_id == "1":
            return "アローラロコン"
    elif pokenum == "38":
        if p_detail_id == "0":
            return "キュウコン"
        elif p_detail_id == "1":
            return "アローラキュウコン"
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
    elif pokenum == "74":
        if p_detail_id == "0":
            return "イシツブテ"
        elif p_detail_id == "1":
            return "アローライシツブテ"
    elif pokenum == "75":
        if p_detail_id == "0":
            return "ゴローン"
        elif p_detail_id == "1":
            return "アローラゴローン"
    elif pokenum == "76":
        if p_detail_id == "0":
            return "ゴローニャ"
        elif p_detail_id == "1":
            return "アローラゴローニャ"
    elif pokenum == "79":
        if p_detail_id == "0":
            return "ヤドン"
        elif p_detail_id == "1":
            return "ガラルヤドン"
    elif pokenum == "80":
        if p_detail_id == "0":
            return "ヤドラン"
        elif p_detail_id == "2":
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
    elif pokenum == "110":
        if p_detail_id == "0":
            return "マタドガス"
        elif p_detail_id == "1":
            return "ガラルマタドガス"
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
    elif pokenum == "570":
        if p_detail_id == "0":
            return "ゾロア"
        elif p_detail_id == "1":
            return "ゾロア(ヒスイ)"
    elif pokenum == "571":
        if p_detail_id == "0":
            return "ゾロアーク"
        elif p_detail_id == "1":
            return "ゾロアーク(ヒスイ)"
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
    elif pokenum == "901":
        if p_detail_id == "0":
            return "ガチグマ"
        elif p_detail_id == "1":
            return "ガチグマ(アカツキ)"
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
    elif pokenum == "931":
        if p_detail_id == "0":
            return "イキリンコ(緑)"
        elif p_detail_id == "1":
            return "イキリンコ(青)"
        elif p_detail_id == "2":
            return "イキリンコ(黄)"
        elif p_detail_id == "3":
            return "イキリンコ(白)"
    elif pokenum == "978":
        if p_detail_id == "0":
            return "シャリタツ(そったすがた)"
        elif p_detail_id == "1":
            return "シャリタツ(たれたすがた)"
        elif p_detail_id == "2":
            return "シャリタツ(のびたすがた)"
    else:
        return ""


class home:
    cid = ""
    rst = 0
    ts2 = ""
    pdetail = {}

    print("ランクマッチ情報取得")
    url = "https://api.battle.pokemon-home.com/tt/cbd/competition/rankmatch/list"
    headers = {
        "accept": "application/json, text/javascript, */*",
        "countrycode": 304,
        "authorization": "Bearer",
        "langcode": 1,
        "user-agent": "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Mobile Safari/537.36",
        "content-type": "application/json",
    }
    param = {"soft": "Sc"}
    req = urllib.request.Request(url, json.dumps(param).encode(), headers)
    with urllib.request.urlopen(req) as res:
        rankmatch_list = json.load(res)
        cid = 0
        for item in rankmatch_list["list"][next(iter(rankmatch_list["list"]))]:
            if (
                rankmatch_list["list"][next(iter(rankmatch_list["list"]))][item]["rule"]
                == 0
            ):
                cid = item
        rst = rankmatch_list["list"][next(iter(rankmatch_list["list"]))][cid]["rst"]
        ts2 = rankmatch_list["list"][next(iter(rankmatch_list["list"]))][cid]["ts2"]

    with open("stats/season.txt", mode="w", encoding="utf-8") as ranking_txt:
        ranking_txt.write(next(iter(rankmatch_list["list"])))

    print("ポケモンランキング取得")
    url = (
        "https://resource.pokemon-home.com/battledata/ranking/scvi/"
        + str(cid)
        + "/"
        + str(rst)
        + "/"
        + str(ts2)
        + "/pokemon"
    )
    headers = {
        "accept": "application/json, text/javascript, */*",
        "user-agent": "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Mobile Safari/537.36",
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as res:
        ranking = json.load(res)
        if os.path.isfile("stats/ranking.txt") is True:
            os.remove("stats/ranking.txt")

        for pokemon in ranking:
            pid = str(pokemon["id"]).zfill(4) + "-0" + str(pokemon["form"])
            with open("stats/ranking.txt", mode="a", encoding="utf-8") as ranking_txt:
                ranking_txt.write(pid + "\n")
                if pokemon["id"] == 1017:
                    ranking_txt.write(str(pokemon["id"]) + "-01\n")
                    ranking_txt.write(str(pokemon["id"]) + "-02\n")
                    ranking_txt.write(str(pokemon["id"]) + "-03\n")

    print("ポケモン情報取得")
    for i in range(1, 7):
        url = (
            "https://resource.pokemon-home.com/battledata/ranking/scvi/"
            + str(cid)
            + "/"
            + str(rst)
            + "/"
            + str(ts2)
            + "/pdetail-"
            + str(i)
        )
        headers = {
            "accept": "application/json, text/javascript, */*",
            "user-agent": "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Mobile Safari/537.36",
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as res:
            pdetail_tmp = json.load(res)
            pdetail = dict(pdetail, **pdetail_tmp)

    pokedex = ""
    with open("stats/bundle.json", "r", encoding="utf-8") as json_open:
        pokedex = json.load(json_open)

    if os.path.isfile("stats/home_waza.csv") is True:
        os.remove("stats/home_waza.csv")
    if os.path.isfile("stats/home_tokusei.csv") is True:
        os.remove("stats/home_tokusei.csv")
    if os.path.isfile("stats/home_seikaku.csv") is True:
        os.remove("stats/home_seikaku.csv")
    if os.path.isfile("stats/home_motimono.csv") is True:
        os.remove("stats/home_motimono.csv")
    if os.path.isfile("stats/home_terastal.csv") is True:
        os.remove("stats/home_terastal.csv")

    print("CSV更新")
    for pokenum in pdetail.keys():
        for p_detail_id in pdetail[pokenum].keys():
            name = get_pokemon_name_for_home(pokenum, p_detail_id)
            if name == "":
                name = pokedex["poke"][int(pokenum) - 1]

            with open("stats/home_waza.csv", "a", encoding="utf-8") as waza_csv:
                for waza in pdetail[pokenum][p_detail_id]["temoti"]["waza"]:
                    writer = csv.writer(waza_csv, lineterminator="\n")
                    writer.writerow(
                        [
                            name,
                            jaconv.z2h(
                                pokedex["waza"][waza["id"]],
                                kana=False,
                                digit=True,
                                ascii=True,
                            ),
                            waza["val"],
                        ]
                    )

            with open("stats/home_tokusei.csv", "a", encoding="utf-8") as tokusei_csv:
                for tokusei in pdetail[pokenum][p_detail_id]["temoti"]["tokusei"]:
                    writer = csv.writer(tokusei_csv, lineterminator="\n")
                    writer.writerow(
                        [
                            name,
                            jaconv.z2h(
                                pokedex["tokusei"][tokusei["id"]],
                                kana=False,
                                digit=True,
                                ascii=True,
                            ),
                            tokusei["val"],
                        ]
                    )

            with open("stats/home_seikaku.csv", "a", encoding="utf-8") as seikaku_csv:
                for seikaku in pdetail[pokenum][p_detail_id]["temoti"]["seikaku"]:
                    writer = csv.writer(seikaku_csv, lineterminator="\n")
                    writer.writerow(
                        [
                            name,
                            jaconv.z2h(
                                pokedex["seikaku"][seikaku["id"]],
                                kana=False,
                                digit=True,
                                ascii=True,
                            ),
                            seikaku["val"],
                        ]
                    )

            with open("stats/home_motimono.csv", "a", encoding="utf-8") as motimono_csv:
                for motimono in pdetail[pokenum][p_detail_id]["temoti"]["motimono"]:
                    writer = csv.writer(motimono_csv, lineterminator="\n")
                    writer.writerow(
                        [
                            name,
                            jaconv.z2h(
                                pokedex["itemname"][motimono["id"]],
                                kana=False,
                                digit=True,
                                ascii=True,
                            ),
                            motimono["val"],
                        ]
                    )

            with open("stats/home_terastal.csv", "a", encoding="utf-8") as terastal_csv:
                for terastal in pdetail[pokenum][p_detail_id]["temoti"]["terastal"]:
                    teras = int(terastal["id"]) if int(terastal["id"]) != 99 else 18
                    writer = csv.writer(terastal_csv, lineterminator="\n")
                    writer.writerow([name, pokedex["pokeType"][teras], terastal["val"]])
    print("CSV更新完了")
