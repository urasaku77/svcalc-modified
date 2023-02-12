from kivy.properties import ListProperty, ObjectProperty, StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy_gui.popup import PartyRegisterPopup, PartyRegisterPopupContent
from kivy.uix.label import Label

import pandas as pd

from pokedata.const import Types
from pokedata.pokemon import Pokemon
from pokedata.nature import Stats,StatsKey, get_seikaku_hosei, get_seikaku_list
from gui import WazaButton, dummy

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
            self.icon = self.pokemon.icon

            self.name = self.pokemon.name
            self.item = self.pokemon.item if self.pokemon.item != "なし" else ""
            self.choose_character(self.pokemon.seikaku)
            self.ability = self.pokemon.ability
            self.abilities = self.pokemon.abilities
            self.terastype = self.pokemon.terastype
            self.terastype_icon = self.terastype.icon
            self.terastype_name = self.terastype.name

            self.statusListPanel.set_kotai(self.pokemon.kotai)
            self.statusListPanel.set_doryoku(self.pokemon.doryoku)

            self.ids["info"].text = "H"+str(value.syuzoku.H)+"-A"+str(value.syuzoku.A)+"-B"+str(value.syuzoku.B)+"-C"+str(value.syuzoku.C)+"-D"+str(value.syuzoku.D)+"-S"+str(value.syuzoku.S)
            
            for i in range(4):
                if self.pokemon.waza_list[i] is not None:
                    self.register_chosen_waza(self.pokemon.waza_list[i].name)
                else:
                    self.register_chosen_waza("")
            self.statusListPanel.set_syuzoku(value)
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

    def choose_character(self, value):
        self.character = value
        self.statusListPanel.change_character(value)

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
        self.ids["info"].text = ""

    def set_csv_row(self):
        waza_list = self.wazaListLabel.get_all_waza()
        all_kotai = self.statusListPanel.get_all_kotai()
        all_doryoku = self.statusListPanel.get_all_doryoku()

        if self.pokemon is None:
            return ""
        else:
            return [self.name, all_kotai, all_doryoku, self.character, self.item, self.ability, self.terastype_name if self.terastype_name != Types.なし.name else "", waza_list[0], waza_list[1], waza_list[2], waza_list[3]]

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
    
    def get_all_waza(self):
        waza_list = []
        for waza in self.wazapanel_list:
            waza_list.append(waza.waza)
        return waza_list

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

# 個体値・努力値調整パネルリスト
class StatusListPanel(BoxLayout):

    statusPanels = ListProperty()
    doryoku_total = NumericProperty(0)
    doryoku_list = ListProperty([0,0,0,0,0,0])

    def __init__(self, **kw):
        super(StatusListPanel, self).__init__(**kw)
        self.type_list=["H","A","B","C","D","S"]
        self.orientation = "vertical"
        bl=BoxLayout()
        title_label = Label(text="",size_hint_x=0.6)
        jisuu_label = Label(text="実数値",size_hint_x=0.5)
        kotai_label = Label(text="個体値",size_hint_x=2)
        doryoku_label = Label(text="努力値",size_hint_x=1)
        doryoku_total_label = Label(text="合計：0",size_hint_x=1)
        self.ids['doryoku_total'] =doryoku_total_label
        bl.add_widget(title_label)
        bl.add_widget(jisuu_label)
        bl.add_widget(kotai_label)
        bl.add_widget(doryoku_label)
        bl.add_widget(doryoku_total_label)
        self.add_widget(bl)

        for i in range(6):
            self.statusPanel = StatusPanel(index=i)
            self.statusPanel.set_func_for_doryoku(self.update_doryoku)
            self.statusPanels.append(self.statusPanel)
            self.add_widget(self.statusPanel)
    
    def set_syuzoku(self,pokemon:Pokemon):
        self.syuzoku_list = [pokemon.syuzoku.H, pokemon.syuzoku.A, pokemon.syuzoku.B, pokemon.syuzoku.C, pokemon.syuzoku.D, pokemon.syuzoku.S]
        for i in range(len(self.statusPanels)):
            self.statusPanels[i].syuzoku = self.syuzoku_list[i]
            self.statusPanels[i].calc_status()
    
    def set_kotai(self,kotai:Stats):
        self.kotai_list = [kotai.H, kotai.A, kotai.B, kotai.C, kotai.D, kotai.S]
        for i in range(len(self.statusPanels)):
            self.statusPanels[i].change_kotai(num=self.kotai_list[i])
            self.statusPanels[i].calc_status()
    
    def set_doryoku(self,doryoku:Stats):
        self.doryoku_list = [doryoku.H, doryoku.A, doryoku.B, doryoku.C, doryoku.D, doryoku.S]
        for i in range(len(self.statusPanels)):
            self.statusPanels[i].change_doryoku(num=self.doryoku_list[i])
            self.statusPanels[i].calc_status()
    
    def change_character(self, value:str):
        for i in range(len(self.statusPanels)):
            self.statusPanels[i].hosei = get_seikaku_hosei(value, StatsKey(i))
            self.statusPanels[i].calc_status()

    def update_doryoku(self, index:int, value: int):
        self.doryoku_list[index] = value
        self.doryoku_total = sum(self.doryoku_list)
        self.ids["doryoku_total"].text = "合計："+str(self.doryoku_total)

    def get_all_kotai(self):
        all_kotai = ""
        for i in range(len(self.statusPanels)):
            if self.statusPanels[i].kotai != "31":
                all_kotai += self.type_list[i] + str(self.statusPanels[i].kotai)
        return all_kotai

    def get_all_doryoku(self):
        all_doryoku = ""
        for i in range(len(self.statusPanels)):
            if self.statusPanels[i].doryoku != "0":
                all_doryoku += self.type_list[i] + str(self.statusPanels[i].doryoku)
        return all_doryoku

# 個体値・努力値調整パネル
class StatusPanel(BoxLayout):
    index=NumericProperty(-1)
    type=StringProperty("")
    hosei=NumericProperty(1.0)

    status=StringProperty("0")
    syuzoku = NumericProperty(0)
    kotai = StringProperty("31")
    doryoku = StringProperty("0")

    def __init__(self, **kw):
        super(StatusPanel, self).__init__(**kw)
        self.type_list=["HP","攻撃","防御","特攻","特防","素早さ"]
        self.type=self.type_list[self.index]
        self.func_for_doryoku = dummy

    def set_func_for_doryoku(self,func):
        self.func_for_doryoku = func

    def calc_status(self):
        if self.syuzoku == 0:
            return
        if self.index == 0:
            self.ids["status"].text = str(int(self.syuzoku + float(self.kotai)/2+float(self.doryoku)/8+60))
        else:
            self.ids["status"].text = str(int((self.syuzoku + float(self.kotai)/2+float(self.doryoku)/8+5)*self.hosei))

    def change_kotai(self, num: int=1, up:bool=True):
        kotai=int(self.kotai)
        if num !=1:
            self.kotai=str(num)
        elif up and kotai < 31:
            self.kotai=str(int(kotai) + 1)
        elif not up and kotai > 0:
            self.kotai=str(int(kotai) - 1)
    
    def change_doryoku(self, num: int=4, slider: bool=False, up:bool=True):
        doryoku=int(self.doryoku)
        if num !=4:
            self.doryoku=str(num)
            self.ids.slider.value = self.doryoku
        elif slider:
            self.doryoku=str(int(self.ids.slider.value))
        elif up and doryoku < 252:
            self.ids.slider.value = int(doryoku) + 4
            self.doryoku=str(self.ids.slider.value)
        elif not up and doryoku > 0:
            self.ids.slider.value = int(doryoku) - 4
            self.doryoku=str(self.ids.slider.value)
        self.func_for_doryoku(self.index, int(self.doryoku))
