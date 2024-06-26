import csv
import re

from pokedata.exception import base_names


def get_party_csv() -> str:
    with open("party/setting.txt", "r") as txt:
        file = txt.read()
        txt.close()
    return "party/csv/" + file


def get_party_data(file_path: str = "default") -> list[list[str]]:
    file = file_path
    if file_path == "default":
        file = get_party_csv()
    with open(file, encoding="sjis") as pt_csv:
        data = [x for x in csv.reader(pt_csv)]
        data = data[1:7]
        return data


def get_home_data(name: str, file_path: str):
    for base_name in base_names:
        if base_name in name:
            name = base_name
    data_list: list[list[str]] = []
    with open(file_path, encoding="utf-8") as csv_file:
        data = [x for x in csv.reader(csv_file)]
        for i in range(len(data)):
            if data[i][0] == name:
                data_list.append([data[i][1], data[i][2]])
    return data_list


if __name__ == "__main__":
    evs = "HA252 S4"
    results = re.findall("([HABCDS]+).*?([0-9]+)", evs, re.S)
    for result in results:
        print(result)
        for key in result[0]:
            print(key)
