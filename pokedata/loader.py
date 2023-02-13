import csv
import re

with open('custom/default.csv', encoding='sjis') as csv_file:
    default_data = [x for x in csv.reader(csv_file)]
    del default_data[0]


def get_default_data(name: str) -> list[str]:
    lst = [x for x in default_data if x[0] == name]
    return lst[0] if len(lst) else []


def get_party_data(file_path: str = 'default') -> list[list[str]]:
    file = file_path
    if file_path == 'default':
        with open('party/setting.txt', 'r') as txt:
            file = txt.read()
            txt.close()
    with open(file, encoding='sjis') as pt_csv:
        data = [x for x in csv.reader(pt_csv)]
        data = data[1:7]
        return data

def get_home_data(name:str, file_path: str):
    if "イルカマン" in name:
        name = "イルカマン"
    data_list:list[list[str]] = []
    with open(file_path, encoding="utf-8") as csv_file:
        data = [x for x in csv.reader(csv_file)]
        for i in range(len(data)):
            if data[i][0] == name:
                data_list.append([data[i][1],data[i][2]])
    return data_list

if __name__ == '__main__':

    evs = "HA252 S4"
    results = re.findall("([HABCDS]+).*?([0-9]+)", evs, re.S)
    for result in results:
        print(result)
        for key in result[0]:
            print(key)