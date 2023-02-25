from kivy.event import EventDispatcher
from kivy.properties import ListProperty, ObjectProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

import pandas as pd

from pokedata.const import Types
from pokedata.pokemon import Pokemon
from gui import WazaButton, IconToggleButton,dummy

#選出された自分ポケモン表示パネル
class PlayerChosenPokemonPanel(BoxLayout):
    name = ListProperty(["","",""])
    doryoku = ListProperty(["","",""])
    item = ListProperty(["","",""])
    ability = ListProperty(["","",""])
    terastype = ObjectProperty([Types.なし,Types.なし,Types.なし])
    waza_list = ListProperty([["","","",""],["","","",""],["","","",""]])

    def __init__(self, **kw):
        super(PlayerChosenPokemonPanel, self).__init__(**kw)
        self.__buttons: list[IconToggleButton] = []
        label = Label(text="選出")
        self.orientation = "vertical"
        self.add_widget(label)
        for i in range(3):
            btn = IconToggleButton(no=i,size_hint=(1, 1), group="party")
            btn.bind(on_release=lambda x: self.on_click_icon(x.no))
            self.__buttons.append(btn)
            self.add_widget(btn)

    def set_pokemon(self, pokemon: Pokemon):
        if pokemon is None or pokemon.name in self.name:
            return
        for chosen_num in range(3):
            if self.name[chosen_num] == "":
                self.__buttons[chosen_num].icon = pokemon.icon
                self.name[chosen_num] = pokemon.name
                self.doryoku[chosen_num] = pokemon.doryoku.to_string
                self.item[chosen_num] = pokemon.item
                self.ability[chosen_num] = pokemon.ability
                self.terastype[chosen_num] = pokemon.terastype
                for i in range(4):
                    self.waza_list[chosen_num][i] = pokemon.waza_list[i].name if pokemon.waza_list[i] is not None else ""
                break

    def on_click_icon(self, chosen_num:int):
        self.__buttons[chosen_num].icon = "image/blank.png"
        self.name[chosen_num] = ""
        self.item[chosen_num] = ""
        self.ability[chosen_num] = ""
        self.terastype[chosen_num] = Types.なし
        self.doryoku[chosen_num] = ""
        self.waza_list[chosen_num] = ["","","",""]

#選出された相手ポケモン表示パネル
class OpponentChosenPokemonPanel(BoxLayout, EventDispatcher):

    __events__ = ("on_click_icon", )

    chosenWazaListPanel = ObjectProperty()
    num = StringProperty("")
    name = StringProperty("")
    memo = StringProperty("")
    items = ListProperty([])
    item = StringProperty("")
    abilities = ListProperty([])
    ability = StringProperty("")
    terastype = ObjectProperty(Types.なし)
    terastype_icon = ObjectProperty(Types.なし.icon)
    icon = StringProperty("image/blank.png")

    def __init__(self, **kw):
        from kivy_gui.popup import TypeSelectPopupContent
        super(OpponentChosenPokemonPanel, self).__init__(**kw)
        self.func_for_terastype = dummy
        self.popup = Popup(
            title="テラスタイプ選択",
            content=TypeSelectPopupContent(selected=self.on_select_terastype),
            size_hint=(0.8, 0.6))

    def set_func_for_terastype(self,func):
        self.func_for_terastype = func

    def set_pokemon(self, pokemon: Pokemon):
        self.name = pokemon.name
        self.icon = pokemon.icon
        self.items = pd.read_csv("battle/item.csv",encoding="utf_8",sep=',',index_col=0).index.tolist()
        self.abilities = pokemon.abilities

    def on_click_icon(self, *args):
        self.name = ""
        self.icon = "image/blank.png"
        self.items = []
        self.item = ""
        self.abilities = []
        self.ability = ""
        self.ids["memo"].text = ""
        self.terastype = Types.なし
        self.terastype_icon = Types.なし.icon
        self.chosenWazaListPanel.clear_all_chosen_waza()

    def select_terastype(self, *_args):
        self.popup.open()

    def on_select_terastype(self, value):
        if self.name != "":
            terastype = Types[value]
            self.terastype = terastype
            self.terastype_icon = terastype.icon
            self.func_for_terastype(self.name, self.terastype)
            self.popup.dismiss()

    def register_chosen_waza(self, waza: str):
        self.chosenWazaListPanel.register_chosen_waza(waza)

# 技パネル一式
class ChosenWazaListPanel(BoxLayout):

    def __init__(self, **kw):
        super(ChosenWazaListPanel, self).__init__(**kw)
        self.orientation = "vertical"
        self.wazapanel_list: list[ChosenWazaPanel] = []

        for i in range(4):
            wazapanel = ChosenWazaPanel(index=i)
            self.add_widget(wazapanel)
            self.wazapanel_list.append(wazapanel)

    def register_chosen_waza(self, waza: str):
        waza_list: list[str] = []
        for index in range(len(self.wazapanel_list)):
            waza_list.append(self.wazapanel_list[index].waza)
        if not waza in waza_list and "" in waza_list:
            self.wazapanel_list[waza_list.index("")].waza = waza
            self.wazapanel_list[waza_list.index("")].waza_button.text = waza

    def clear_all_chosen_waza(self):
        for waza in self.wazapanel_list:
            waza.waza = ""
            waza.waza_button.text = ""
            waza.pp = 0
            waza.pp_text.text = str(0)

# 技＋クリアボタン＋PP周り
class ChosenWazaPanel(BoxLayout):

    index = NumericProperty(-1)

    def __init__(self, **kw):
        super(ChosenWazaPanel, self).__init__(**kw)
        self.waza: str = ""
        self.pp: int = 0

        # クリアボタン
        self.center_button = Button(size_hint_x=None, width=30, on_press=self.click_center_button)
        # 技名ボタン
        self.waza_button: WazaButton = WazaButton()
        self.waza_button.bind(on_confirm=lambda x: self.on_select_waza(x.text))
        # マイナスボタン
        self.minus_button = Button(text="-", size_hint_x=None, width=20, on_press=self.click_minus_button)
        # PP
        self.pp_text = Label(text=str(self.pp), size_hint_x=None, width=10)
        # プラスボタン
        self.plus_button = Button(text="+", size_hint_x=None, width=20, on_press=self.click_plus_button)

        self.add_widget(self.center_button)
        self.add_widget(self.waza_button)
        self.add_widget(self.minus_button)
        self.add_widget(self.pp_text)
        self.add_widget(self.plus_button)
        self.spacing = 5

    # 技名コンボボックスが決定された時
    def on_select_waza(self, value: str) -> None:
        if value is not None:
            self.waza = value
            self.waza_button.text = self.waza

    # クリアボタンが押された時
    def click_center_button(self, *args):
        self.waza = ""
        self.waza_button.text = ""
        self.pp = 0
        self.pp_text.text = str(self.pp)

    # マイナスボタンが押された時
    def click_minus_button(self, *args):
        if self.pp > 0:
            self.pp = self.pp - 1
            self.pp_text.text = str(self.pp)

    # プラスボタンが押された時
    def click_plus_button(self, *args):
        if self.pp < 64:
            self.pp = self.pp + 1
            self.pp_text.text = str(self.pp)

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
            case "せいかく":
                pass
            case "もちもの":
                file_path = "./home/home_motimono.csv"
            case "とくせい":
                file_path = "./home/home_tokusei.csv"
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