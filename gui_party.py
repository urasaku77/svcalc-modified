from kivy.properties import ListProperty, ObjectProperty, StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy_gui.popup import PartyRegisterPopup, PartyRegisterPopupContent
from kivy.uix.label import Label

import pandas as pd

from pokedata.const import Types
from pokedata.pokemon import Pokemon
from pokedata.nature import get_seikaku_list
from gui import WazaButton

class PartyPokemonPanel(BoxLayout):

    num = StringProperty("")
    pokemon = ObjectProperty(None)

    name = StringProperty("")
    items = ListProperty([])
    item = StringProperty("")
    characters = ListProperty([])
    character = StringProperty("")
    abilities = ListProperty([])
    ability = StringProperty("")
    terastype = ObjectProperty(Types.なし)
    terastype_icon = ObjectProperty(Types.なし.icon)
    terastype_name = ObjectProperty(Types.なし.name)
    
    wazaListLabel = ObjectProperty()
    statusListPanel = ObjectProperty()

    icon = StringProperty("")
    
    def __init__(self, **kw):
        from kivy_gui.popup import TypeSelectPopupContent
        super(PartyPokemonPanel, self).__init__(**kw)
        self.items = pd.read_csv("battle/item.csv",encoding="utf_8",sep=',',index_col=0).index.tolist()
        self.characters = get_seikaku_list()
        self.pokemon_popup = PartyRegisterPopup(
            title="ポケモン選択",
            content=PartyRegisterPopupContent(selected=self.on_select_pokemon),
            size_hint=(None, None), size=(400, 120))
        self.terastype_popup = Popup(
            title="テラスタイプ選択",
            content=TypeSelectPopupContent(selected=self.on_select_terastype),
            size_hint=(0.8, 0.6))

    def on_click_icon(self, *args):
        self.pokemon_popup.open()
    
    def on_select_pokemon(self, value:Pokemon):
        self.clear_pokemon()
        if value is not None:
            self.pokemon = value
            self.name = self.pokemon.name
            self.icon = self.pokemon.icon
            self.abilities = self.pokemon.abilities
            for i in range(4):
                self.register_chosen_waza(self.pokemon.waza_list[i].name)
        self.pokemon_popup.dismiss()

    def select_terastype(self, *_args):
        self.terastype_popup.open()

    def on_select_terastype(self, value):
        if self.name != "":
            terastype = Types[value]
            self.terastype = terastype
            self.terastype_icon = terastype.icon
            self.terastype_name = terastype.name
            self.terastype_popup.dismiss()

    def register_chosen_waza(self, waza: str):
        self.wazaListLabel.register_chosen_waza(waza)
    
    def clear_pokemon(self):
        self.pokemon = ObjectProperty(None)
        self.name = ""
        self.icon = ""
        self.item = ""
        self.character = ""
        self.abilities = []
        self.ability = ""
        self.terastype = Types.なし
        self.terastype_icon = Types.なし.icon
        self.terastype_name = Types.なし.name
        self.wazaListLabel.clear_all_chosen_waza()

# 技コンボボックスリスト
class WazaListLabel(BoxLayout):

    def __init__(self, **kw):
        super(WazaListLabel, self).__init__(**kw)
        self.orientation = "vertical"
        self.wazapanel_list: list[WazaPanel] = []

        for i in range(4):
            wazapanel = WazaPanel(index=i)
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

# 技コンボボックス
class WazaPanel(BoxLayout):

    index = NumericProperty(-1)

    def __init__(self, **kw):
        super(WazaPanel, self).__init__(**kw)
        self.waza: str = ""

        # 技名ボタン
        self.waza_button: WazaButton = WazaButton()
        self.waza_button.bind(on_confirm=lambda x: self.on_select_waza(x.text))

        self.add_widget(self.waza_button)
        self.spacing = 5

    # 技名コンボボックスが決定された時
    def on_select_waza(self, value: str) -> None:
        if value is not None:
            self.waza = value
            self.waza_button.text = self.waza

class StatusListPanel(BoxLayout):

    def __init__(self, **kw):
        super(StatusListPanel, self).__init__(**kw)
        self.orientation = "vertical"
        bl=BoxLayout()
        title_label = Label(text="",size_hint_x=0.6)
        jisuu_label = Label(text="実数値",size_hint_x=0.5)
        kotai_label = Label(text="個体値",size_hint_x=2)
        doryoku_label = Label(text="努力値",size_hint_x=4)
        bl.add_widget(title_label)
        bl.add_widget(jisuu_label)
        bl.add_widget(kotai_label)
        bl.add_widget(doryoku_label)
        self.add_widget(bl)

        for i in range(6):
            statusPanel = StatusPanel(index=i)
            self.add_widget(statusPanel)        

class StatusPanel(BoxLayout):
    index=NumericProperty(-1)
    type=StringProperty("")

    kotai = StringProperty("31")
    doryoku = StringProperty("0")

    def __init__(self, **kw):
        super(StatusPanel, self).__init__(**kw)
        self.type_list=["HP","攻撃","防御","特攻","特防","素早さ"]
        self.type=self.type_list[self.index]

    def change_kotai(self, num: int=1, up:bool=True):
        kotai=int(self.kotai)
        if num !=1:
            self.kotai=str(num)
        elif up and kotai < 31:
            self.kotai=str(int(kotai) + 1)
        elif not up and kotai > 0:
            self.kotai=str(int(kotai) - 1)
    
    def change_doryoku(self, slider: bool=False, up:bool=True):
        doryoku=int(self.doryoku)
        if slider:
            self.doryoku=str(int(self.ids.slider.value))
        elif up and doryoku < 252:
            self.ids.slider.value = int(doryoku) + 4
            self.doryoku=str(self.ids.slider.value)
        elif not up and doryoku > 0:
            self.ids.slider.value = int(doryoku) - 4
            self.doryoku=str(self.ids.slider.value)
