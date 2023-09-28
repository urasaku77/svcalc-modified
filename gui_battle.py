from kivy.event import EventDispatcher
from kivy.properties import ListProperty, ObjectProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

import pandas as pd
import webbrowser

from pokedata.const import Types
from pokedata.pokemon import Pokemon
from pokedata.exception import exist_few_form_pokemon_no, changeble_form_in_battle, get_parameter_for_poketetsu
from gui import WazaButton, IconButton,dummy

#選出された自分ポケモン表示パネル
class PlayerChosenPokemonPanel(BoxLayout):
    name = ListProperty(["","",""])
    waza_list = ListProperty([["","","",""],["","","",""],["","","",""]])
    waza_check_list = ListProperty([[0,0,0,0],[0,0,0,0],[0,0,0,0]])

    def __init__(self, **kw):
        super(PlayerChosenPokemonPanel, self).__init__(**kw)
        self.func_for_click_icon = dummy
        self.__buttons: list[IconButton] = []
        label = Label(text="自分の選出")
        self.add_widget(label)
        for i in range(3):
            btn = IconButton(no=i,size_hint=(1, 1))
            btn.bind(on_release=lambda x: self.on_click_icon(x.no))
            self.__buttons.append(btn)
            self.add_widget(btn)

    def set_pokemon(self, pokemon: Pokemon):
        if pokemon is None or pokemon.name in self.name:
            return
        for chosen_num in range(3):
            if self.name[chosen_num] == "":
                self.__buttons[chosen_num].icon = pokemon.icon
                self.__buttons[chosen_num].text = pokemon.name
                self.name[chosen_num] = pokemon.name
                for i in range(4):
                    self.waza_list[chosen_num][i] = pokemon.waza_list[i].name if pokemon.waza_list[i] is not None else ""
                self.waza_check_list[chosen_num] = [0,0,0,0]
                break

    def set_func_for_click_icon(self,func):
        self.func_for_click_icon = func

    def on_click_icon(self, chosen_num:int):
        self.name[chosen_num] = ""
        self.__buttons[chosen_num].icon = "image/other/blank.png"
        self.__buttons[chosen_num].text = ""
        self.waza_list[chosen_num] = ["","","",""]
        self.waza_check_list[chosen_num] = [0,0,0,0]
        self.func_for_click_icon()

    def change_waza_check(self, poke_index:int, waza_index:int):
        self.waza_check_list[poke_index][waza_index] = 1 if self.waza_check_list[poke_index][waza_index] != 1 else 0

    def get_waza_check(self, poke_name:str) -> list[int]:
        for chosen_num in range(3):
            if self.name[chosen_num] == poke_name:
                return self.waza_check_list[chosen_num]
        return [0,0,0,0]

#選出された相手ポケモン表示パネル
class OpponentChosenPokemonPanel(BoxLayout):

    no = ListProperty(["","",""])
    name = ListProperty(["","",""])
    icon = ListProperty(["image/other/blank.png","image/other/blank.png","image/other/blank.png"])

    def __init__(self, **kw):
        super(OpponentChosenPokemonPanel, self).__init__(**kw)
        self.func_for_change = dummy
        self.__buttons: list[IconButton] = []
        for i in range(3):
            btn = IconButton(no=i,size_hint=(1, 1))
            btn.bind(on_release=lambda x: self.on_click_icon(x.no))
            self.__buttons.append(btn)
            self.add_widget(btn)
        label = Label(text="相手の選出")
        self.add_widget(label)

    def set_pokemon(self, pokemon: Pokemon):
        if pokemon is None or pokemon.no in self.no:
            return
        for chosen_num in range(3):
            if self.name[chosen_num] == "":
                self.no[chosen_num] = pokemon.no
                self.name[chosen_num] = pokemon.name
                self.__buttons[chosen_num].icon = pokemon.icon
                self.__buttons[chosen_num].text = pokemon.name
                break

    def set_func_for_click_icon(self,func):
        self.func_for_click_icon = func

    def on_click_icon(self, chosen_num:int):
        self.no[chosen_num] = ""
        self.name[chosen_num] = ""
        self.__buttons[chosen_num].icon = "image/other/blank.png"
        self.__buttons[chosen_num].text = ""

# カウンターパネル
class CounterPanel(BoxLayout):

    def __init__(self, **kw):
        super(CounterPanel, self).__init__(**kw)
        self.count: int = 0

        # マイナスボタン
        self.minus_button = Button(text="-", on_press=self.click_minus_button)
        # PP
        self.count_text = Label(text=str(self.count))
        # プラスボタン
        self.plus_button = Button(text="+", on_press=self.click_plus_button)

        self.add_widget(self.minus_button)
        self.add_widget(self.count_text)
        self.add_widget(self.plus_button)
        self.spacing = 5

    # クリアボタンが押された時
    def clear(self, *args):
        self.count = 0
        self.count_text.text = str(self.count)

    # マイナスボタンが押された時
    def click_minus_button(self, *args):
        if self.count > 0:
            self.count = self.count - 1
            self.count_text.text = str(self.count)

    # プラスボタンが押された時
    def click_plus_button(self, *args):
        if self.count < 64:
            self.count = self.count + 1
            self.count_text.text = str(self.count)

# 20分タイマー部品一式
class TimerLabel(BoxLayout):
    minutes = StringProperty()
    seconds = StringProperty()
    state = StringProperty()
    running = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(TimerLabel, self).__init__(**kwargs)
        self.minutes = "20"
        self.seconds = "00"
        self.state = "開始"

    def start(self):
        if not self.running:
            self.running = True
            self.state = "停止"
            Clock.schedule_interval(self.update, 1)

    def stop(self):
        if self.running:
            self.running = False
            self.state = "開始"
            Clock.unschedule(self.update)

    def restart(self):
        self.reset()
        self.start()

    def update(self, *kwargs):
        if int(self.minutes) == 0 and int(self.seconds) == 0:
            self.stop()
        elif int(self.seconds) != 0:
            self.seconds = str(int(self.seconds) - 1).zfill(2)
        elif int(self.seconds) == 0:
            self.seconds = "59"
            self.minutes = str(int(self.minutes) - 1).zfill(2)

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def reset(self):
        self.stop()
        self.minutes = "20"
        self.seconds = "00"

#ポケモン基本情報表示パネル
class PokemonInfoPanel(BoxLayout):
    pid =  StringProperty("0")
    name = StringProperty("")
    type1 = StringProperty("")
    type1_img = StringProperty(Types.なし.icon)
    type2 = StringProperty("")
    type2_img = StringProperty(Types.なし.icon)
    h = StringProperty("")
    a = StringProperty("")
    b = StringProperty("")
    c = StringProperty("")
    d = StringProperty("")
    s = StringProperty("")
    weight = StringProperty("")
    ketaguri = StringProperty("")

    def __init__(self, **kwargs):
        super(PokemonInfoPanel, self).__init__(**kwargs)

    def set_pokemon(self, pokemon: Pokemon):
        self.pid = str(pokemon.pid)
        self.name = pokemon.name
        self.type1 = pokemon.type[0].name
        self.type1_img = pokemon.type[0].icon
        self.type2 = pokemon.type[1].name if len(pokemon.type) > 1 else ""
        self.type2_img = pokemon.type[1].icon if self.type2 != "" else Types.なし.icon
        self.h = str(pokemon.syuzoku.H)
        self.a = str(pokemon.syuzoku.A)
        self.b = str(pokemon.syuzoku.B)
        self.c = str(pokemon.syuzoku.C)
        self.d = str(pokemon.syuzoku.D)
        self.s = str(pokemon.syuzoku.S)
        self.weight = str(pokemon.weight)
        if pokemon.weight < 10:
            self.ketaguri = str(20)
        elif pokemon.weight < 25:
            self.ketaguri = str(40)
        elif pokemon.weight < 50:
            self.ketaguri = str(60)
        elif pokemon.weight < 100:
            self.ketaguri = str(80)
        elif pokemon.weight < 200:
            self.ketaguri = str(100)
        else:
            self.ketaguri = str(120)

    def init_pokemon(self):
        self.pid = "0"
        self.name = ""
        self.type1 = ""
        self.type1_img = Types.なし.icon
        self.type2 = ""
        self.type2_img = Types.なし.icon
        self.h = ""
        self.a = ""
        self.b = ""
        self.c = ""
        self.d = ""
        self.s = ""
        self.weight = ""
        self.ketaguri = ""

    def open_poketetsu(self):
        if self.pid != "0":
            parameter = ""
            no = self.pid.split("-")[0]
            form = self.pid.split("-")[1]
            if no in exist_few_form_pokemon_no or changeble_form_in_battle:
                parameter = get_parameter_for_poketetsu(no,form)
            url = "https://yakkun.com/sv/zukan/n" + no + parameter
            webbrowser.open(url)

# ポケモンHOME情報表示パネル
class HomeInfoPanel(BoxLayout):
    title_name = StringProperty("")
    data_list = ListProperty([])

    def __init__(self, **kw):
        super(HomeInfoPanel, self).__init__(**kw)
        self.orientation = "vertical"
        label_title = Label(text="HOME情報", markup=True)
        self.add_widget(label_title)

    def set_home_data(self,name:str):
        file_path = ""
        match self.title_name:
            case "もちもの":
                file_path = "./home/home_motimono.csv"
            case "とくせい":
                file_path = "./home/home_tokusei.csv"
            case "せいかく":
                file_path = "./home/home_seikaku.csv"
            case "テラスタイプ":
                file_path = "./home/home_terastal.csv"

        from pokedata.loader import get_home_data
        data_list = get_home_data(name, file_path)
        self.clear_widgets()
        label_title = Label(text='[u][b]' + self.title_name + '[/b][/u]', markup=True)
        self.add_widget(label_title)
        for i in range(len(data_list)):
            bl = BoxLayout()
            label_rank = Label(text=str(i+1))
            label_name = Label(text=data_list[i][0])
            label_rate = Label(text=data_list[i][1])
            bl.add_widget(label_rank)
            bl.add_widget(label_name)
            bl.add_widget(label_rate)
            self.add_widget(bl)

    def init_data(self):
        self.clear_widgets()
        self.__init__()