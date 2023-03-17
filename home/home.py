import os
import json
import csv
import urllib.request
import jaconv

from pokedata.form import exist_few_form_pokemon_no, get_pokemon_name_for_home

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
                print(item)
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
    with open('./bundle.json', 'r',encoding="utf-8") as json_open:
        pokedex = json.load(json_open)

    if os.path.isfile('./home_waza.csv') == True:
        os.remove('./home_waza.csv')
    if os.path.isfile('./home_tokusei.csv') == True:
        os.remove('./home_tokusei.csv')
    if os.path.isfile('./home_seikaku.csv') == True:
        os.remove('./home_seikaku.csv')
    if os.path.isfile('./home_motimono.csv') == True:
        os.remove('./home_motimono.csv')
    if os.path.isfile('./home_terastal.csv') == True:
        os.remove('./home_terastal.csv')

    print("CSV更新")
    for pokenum in pdetail.keys():
        for p_detail_id in pdetail[pokenum].keys():
            name = ""
            if pokenum in exist_few_form_pokemon_no:
                name = get_pokemon_name_for_home(pokenum, p_detail_id)
            else:
                name = pokedex['poke'][int(pokenum) -1]

            with open('./home_waza.csv', 'a',encoding="utf-8") as waza_csv:
                for waza in pdetail[pokenum][p_detail_id]['temoti']['waza']:
                        writer = csv.writer(waza_csv, lineterminator="\n")
                        writer.writerow([name, jaconv.z2h(pokedex['waza'][waza['id']],kana=False,digit=True, ascii=True),waza['val']])

            with open('./home_tokusei.csv', 'a',encoding="utf-8") as tokusei_csv:
                for tokusei in pdetail[pokenum][p_detail_id]['temoti']['tokusei']:
                        writer = csv.writer(tokusei_csv, lineterminator="\n")
                        writer.writerow([name, jaconv.z2h(pokedex['tokusei'][tokusei['id']],kana=False,digit=True, ascii=True),tokusei['val']])

            with open('./home_seikaku.csv', 'a',encoding="utf-8") as seikaku_csv:
                for seikaku in pdetail[pokenum][p_detail_id]['temoti']['seikaku']:
                        writer = csv.writer(seikaku_csv, lineterminator="\n")
                        writer.writerow([name, jaconv.z2h(pokedex['seikaku'][seikaku['id']],kana=False,digit=True, ascii=True),seikaku['val']])

            with open('./home_motimono.csv', 'a',encoding="utf-8") as motimono_csv:
                for motimono in pdetail[pokenum][p_detail_id]['temoti']['motimono']:
                        writer = csv.writer(motimono_csv, lineterminator="\n")
                        writer.writerow([name, jaconv.z2h(pokedex['itemname'][motimono['id']],kana=False,digit=True, ascii=True),motimono['val']])

            with open('./home_terastal.csv', 'a',encoding="utf-8") as terastal_csv:
                for terastal in pdetail[pokenum][p_detail_id]['temoti']['terastal']:
                        writer = csv.writer(terastal_csv, lineterminator="\n")
                        writer.writerow([name, pokedex['pokeType'][int(terastal['id'])],terastal['val']])
    print("CSV更新完了")
