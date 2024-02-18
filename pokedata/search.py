import json
import webbrowser
from functools import reduce

from selenium import webdriver
from selenium.webdriver.common.by import By


def get_similar_party(pids):
    all_urls = []
    undefines = []
    with open("home/ranking.json", encoding="utf-8") as ranking_json:
        rankings = list(json.load(ranking_json))
        for pid in pids:
            if 892 == pid.no:
                for ranking in rankings:
                    for ura in ["0892-00", "0892-01"]:
                        if ranking["pid"] == ura:
                            undefines.append(ranking["party"])
            else:
                for ranking in rankings:
                    if ranking["pid"] == str(pid.no).zfill(4) + "-0" + str(pid.form):
                        all_urls.append(ranking["party"])
    results = reduce(set.intersection, map(set, all_urls))

    if len(undefines) == 0:
        for result in list(results):
            webbrowser.open(result)
        print(f"見つかった個数：{len(list(results))}個")
    else:
        result_undefines = (set(undefines[0]) | set(undefines[1])) & results
        for result_undefine in list(result_undefines):
            webbrowser.open(result_undefine)
        print(f"見つかった個数：{len(list(result_undefines))}個")


class Search:
    def search_latest_party(self):
        print("構築記事一覧取得処理開始")
        party_list = []
        with open("home/ranking.txt", encoding="utf-8") as ranking_txt:
            ranking_list = [line.rstrip("\n") for line in ranking_txt]
            for i in range(len(ranking_list)):
                print(f"{i+1}/{len(ranking_list)}：{ranking_list[i]}")
                party_list.append(
                    {
                        "pid": ranking_list[i],
                        "party": self.get_latest_party_per_pokemon(
                            ranking_list[i], 200 if i < 30 else 50 if i < 100 else 10
                        ),
                    }
                )
        print("読み込み完了")
        with open("home/ranking.json", "w", encoding="utf-8") as ranking_json:
            json.dump(party_list, ranking_json, indent=2)
        print("書き込み完了")

    def get_latest_party_per_pokemon(self, pid: str, num: int):
        season = 1
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")

        driver = webdriver.Chrome(options=options)

        with open("home/season.txt", encoding="utf-8") as ranking_txt:
            season = ranking_txt.read()

        try:
            driver.get(
                f"https://sv.pokedb.tokyo/pokemon/show/{pid}?season={season}&rule=0"
            )

            party_classes = driver.find_elements(
                By.XPATH,
                "//a[@class='icon-text is-hidden-mobile is-flex is-flex-direction-column is-align-items-center is-justify-content-center link-team-article']",
            )
            urls = []
            number = num if len(party_classes) > num else len(party_classes)
            for i in range(number):
                url = party_classes[i].get_attribute("href")
                urls.append(url)
            return urls
        except:
            return urls


if __name__ == "__main__":
    search = Search()
    search.search_latest_party()
