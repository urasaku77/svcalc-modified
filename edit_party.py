from kivy.app import App
from kivy.properties import ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy_gui.popup import PartyInputPopup, SpeedCheckPopup

import glob
import csv

class EditPartyWidget(BoxLayout):
    partyPokemonPanels = ListProperty()
    title=StringProperty("")
    num=StringProperty("")
    sub_num=StringProperty("")
    using_csv=StringProperty("")

    def __init__(self, **kwargs):
        super(EditPartyWidget, self).__init__(**kwargs)
    
    def open_csv(self):
        pass

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
        
        filepath = "party/csv/"+self.num + "-" + self.sub_num + "_" + self.title + ".csv"
        with open(filepath, 'w') as party_csv:
            writer = csv.writer(party_csv, lineterminator="\n")
            writer.writerow(["名前", "個体値", "努力値", "性格", "持ち物", "特性", "テラス", "技", "技", "技", "技"])
            for partyPokemonPanel in self.partyPokemonPanels:
                row = partyPokemonPanel.set_csv_row()
                writer.writerow(row)
        

    def change_using_csv(self):
        pass