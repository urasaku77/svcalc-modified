import csv
import re

with open('custom/default.csv', encoding='sjis') as csv_file:
    default_data = [x for x in csv.reader(csv_file)]
    del default_data[0]


def get_default_data(name: str) -> list[str]:
    lst = [x for x in default_data if x[0] == name]
    return lst[0] if len(lst) else []


def get_party_data(file_path: str = 'custom/party.csv') -> list[list[str]]:
    with open(file_path, encoding='sjis') as pt_csv:
        data = [x for x in csv.reader(pt_csv)]
        data = data[1:7]
        return data


if __name__ == '__main__':

    evs = "HA252 S4"
    results = re.findall("([HABCDS]+).*?([0-9]+)", evs, re.S)
    for result in results:
        print(result)
        for key in result[0]:
            print(key)
