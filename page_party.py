from kivy.properties import ListProperty, StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy_gui.popup import CsvChooserPopup

from pokedata.pokemon import Pokemon

import glob
import csv

class PagePartyWidget(BoxLayout):
    partyPokemonPanels = ListProperty()
    title=StringProperty("")
    num=StringProperty("")
    sub_num=StringProperty("")
    memo=StringProperty("")
    using=StringProperty("")
    set_default = BooleanProperty(True)

    def __init__(self, **kwargs):
        super(PagePartyWidget, self).__init__(**kwargs)
        self.get_using_csv()

    def open_csv(self):
        self.set_chooser_popup = CsvChooserPopup(selected=self.select_csv,title="CSV選択")
        self.set_chooser_popup.open()

    def select_csv(self, csv:str):
        file = csv.split('party\\csv\\')[1]
        self.ids["num"].text = file.split("-")[0]
        self.ids["sub_num"].text = file.split("-")[1].split("_")[0]
        self.ids["title"].text = file.split("-")[1].split("_")[1].split(".")[0]
        memo_file= "party\\" + file.replace("csv","txt")
        with open(memo_file, 'r') as txt:
            self.memo = txt.read()
            txt.close()
        self.ids["memo"].text = self.memo
        self.load_party(csv)
        self.set_chooser_popup.dismiss()

    def load_party(self, path:str):
        from pokedata.loader import get_party_data
        for i, data in enumerate(get_party_data(file_path=path)):
            pokemon: Pokemon = Pokemon.by_name(data[0])
            pokemon.set_load_data(data, True)
            self.partyPokemonPanels[i].on_select_pokemon(pokemon)

    def clear_party(self):
        for partyPokemonPanel in self.partyPokemonPanels:
            partyPokemonPanel.on_select_pokemon(None)

    def save_csv(self):
        self.title = self.ids["title"].text
        self.num = self.ids["num"].text
        self.sub_num = self.ids["sub_num"].text

        if self.title == "":
            return
        file_list = sorted(glob.glob("party/csv/*"))
        last_file = file_list[len(file_list)-1]
        if self.num == "":
            self.num = str(int(last_file.replace('party/csv\\', '')[0])+1)
            self.sub_num = "0"
        elif self.sub_num == "":
            same_num_list= [file for file in file_list if file.startswith('party/csv\\'+self.num+"-")]
            last_same_num_file=sorted(same_num_list)[len(same_num_list)-1]
            self.sub_num = str(int(last_same_num_file.split("-")[1][0])+1)

        filepath = "party\\csv\\"+self.num + "-" + self.sub_num + "_" + self.title + ".csv"
        with open(filepath, 'w') as party_csv:
            writer = csv.writer(party_csv, lineterminator="\n")
            writer.writerow(["名前", "個体値", "努力値", "性格", "持ち物", "特性", "テラス", "技", "技", "技", "技"])
            for partyPokemonPanel in self.partyPokemonPanels:
                row = partyPokemonPanel.set_csv_row()
                writer.writerow(row)

        self.memo = self.ids["memo"].text
        with open("party\\"+self.num + "-" + self.sub_num + "_" + self.title + ".txt", 'w') as txt:
            txt.write(self.memo)
            txt.close()

        if self.set_default:
            self.change_csv(filepath,popup=False)

    def get_using_csv(self):
        with open('party/setting.txt', 'r') as txt:
            self.using = txt.read().split('party\\csv\\')[1]
            txt.close()

    def change_using_csv(self):
        self.change_chooser_popup = CsvChooserPopup(selected=self.change_csv,title="CSV選択")
        self.change_chooser_popup.open()

    def change_csv(self, value:str, popup:bool=True):
        with open('party/setting.txt', 'w') as txt:
            txt.write(value)
            self.using = value.split('party\\csv\\')[1]
            self.ids["using"].text= self.using
            txt.close()
        if popup:
            self.change_chooser_popup.dismiss()