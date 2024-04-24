import json
from functools import reduce

from selenium import webdriver
from selenium.webdriver.common.by import By

# Pokemonクラスを読み込むとバッチファイルからうまく起動しないため省略している


def get_similar_party(pids: list) -> list:
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
                    if ranking["pid"] == str(pid.no).zfill(4) + "-" + str(
                        pid.form
                    ).zfill(2):
                        all_urls.append(ranking["party"])
    results = reduce(set.intersection, map(set, all_urls))

    all_party = []
    if len(undefines) == 0:
        print(f"見つかった個数：{len(list(results))}個")
        for result in list(results):
            if get_party_members(result) is not None:
                all_party.append(get_party_members(result))
    else:
        result_undefines = (set(undefines[0]) | set(undefines[1])) & results
        print(f"見つかった個数：{len(list(result_undefines))}個")
        for result_undefine in list(result_undefines):
            if get_party_members(result_undefine) is not None:
                all_party.append(get_party_members(result_undefine))

    return all_party


def get_party_members(url: str):
    party_member = []
    with open("home/party_members.json", encoding="utf-8") as party_members_json:
        party_members_list = list(json.load(party_members_json))
        party_member = [
            party_members
            for party_members in party_members_list
            if party_members["url"] == url
        ]
    if len(party_member) != 0:
        return party_member[0]


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
                        "party": self.search_latest_party_per_pokemon(
                            ranking_list[i], 200 if i < 30 else 50 if i < 100 else 10
                        ),
                    }
                )
        print("読み込み完了")
        with open("home/ranking.json", "w", encoding="utf-8") as ranking_json:
            json.dump(party_list, ranking_json, indent=2)
        print("書き込み完了")

    def search_latest_party_per_pokemon(self, pid: str, num: int):
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
                "//a[@class='icon-text is-hidden-mobile link-team-article']",
            )
            urls = []
            number = num if len(party_classes) > num else len(party_classes)
            for i in range(number):
                url = party_classes[i].get_attribute("href")
                urls.append(url)
            return urls
        except:
            return urls

    def search_party_members(self):
        season = 1
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")

        driver = webdriver.Chrome(options=options)

        with open("home/season.txt", encoding="utf-8") as ranking_txt:
            season = ranking_txt.read()

        try:
            ranking_list = []
            page_flag = True
            num = 0
            while page_flag:
                num = num + 1
                print(num)
                driver.get(
                    f"https://sv.pokedb.tokyo/trainer/list?season={str(int(season) - 1)}&rule=0&name=&party=1&page={num}"
                )

                trainer_classes = driver.find_elements(
                    By.XPATH,
                    "//div[@class='trainer-team is-flex']",
                )

                for i in range(len(trainer_classes)):
                    icon_classes = trainer_classes[i].find_elements(
                        By.XPATH,
                        ".//div[@class='team-pokemon']",
                    )
                    urls = []
                    print(f"{i+1}/{len(trainer_classes)}実行中")
                    for j in range(len(icon_classes)):
                        icon = (
                            icon_classes[j]
                            .find_element(
                                By.TAG_NAME,
                                "a",
                            )
                            .get_attribute("href")
                        )
                        no = icon.split("show/")[1].split("-")[0]
                        form = (
                            icon.split(f"{no}-")[1].split("?season")[0].lstrip("0")
                            if icon.split(f"{no}-")[1].split("?season")[0].lstrip("0")
                            != ""
                            else 0
                        )
                        urls.append(f"{no.lstrip('0')}-{form}")
                    ranking_list.append(
                        {
                            "url": trainer_classes[i]
                            .find_element(
                                By.XPATH,
                                ".//a[@class='icon-text is-hidden-mobile is-flex is-flex-direction-column is-align-items-center is-justify-content-center link-team-article']",
                            )
                            .get_attribute("href"),
                            "icons": urls,
                        }
                    )

                if (
                    len(
                        driver.find_elements(
                            By.CLASS_NAME,
                            "pagination-next",
                        )
                    )
                    == 0
                ):
                    page_flag = False
            with open(
                "home/party_members.json", "w", encoding="utf-8"
            ) as party_members_json:
                json.dump(ranking_list, party_members_json, indent=2)

        except Exception as e:
            print(e)


if __name__ == "__main__":
    search = Search()
    search.search_party_members()
    search.search_latest_party()
