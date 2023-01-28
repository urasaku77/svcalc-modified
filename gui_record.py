from kivy.event import EventDispatcher
from kivy.properties import ListProperty, ObjectProperty, StringProperty, NumericProperty, BooleanProperty

from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from pokedata.const import 変化, Types
from pokedata.pokemon import Pokemon

from gui import WazaButton

#選出されたポケモン表示パネル
class ChosenPokemonPanel(BoxLayout, EventDispatcher):

    __events__ = ("on_click_icon", )

    chosenWazaListPanel = ObjectProperty()
    pokemon = ObjectProperty(None, allownone=True)
    chosen_num = NumericProperty(-1)
    evs_combobox = ObjectProperty()
    teras_button = ObjectProperty()
    icon = ObjectProperty()
    formchange_icon = ObjectProperty()


    def __init__(self, **kw):
        from kivy_gui.popup import TypeSelectPopupContent
        super(ChosenPokemonPanel, self).__init__(**kw)
        self.popup = Popup(
            title="テラスタイプ選択",
            content=TypeSelectPopupContent(selected=self.on_select_terastype),
            size_hint=(0.8, 0.6))

    @property
    def battle_terastype_icon(self):
        if self.pokemon is None:
            return Types.なし.icon
        return self.pokemon.battle_terastype.icon

    def set_pokemon(self, player_id: int, pokemon: Pokemon):
        self.pokemon: Pokemon = pokemon
        if player_id == 0:
            for i in range(4):
                waza = pokemon.waza_list[i].name if pokemon.waza_list[i] is not None else ""
                self.register_chosen_waza(waza)

    def on_click_icon(self, *args):
        self.pokemon = None
        self.teras_button.icon = Types.なし.icon
        self.chosenWazaListPanel.clear_all_chosen_waza()

    def form_change(self):
        pokemon: Pokemon = self.pokemon
        if pokemon is not None:
            pokemon.form_change()
            self.evs_combobox.text = pokemon.marked_status_text
            self.icon.icon = pokemon.icon
            self.icon.formchange_icon = pokemon.next_form_icon    

    def on_select_doryoku_preset(self, value):
        self.pokemon.set_doryoku_preset(value)
        self.evs_combobox.text = self.pokemon.marked_status_text

    def select_terastype(self, *_args):
        self.popup.open()

    def on_select_terastype(self, value):
        if self.pokemon is not None:
            terastype = Types[value]
            self.pokemon.battle_terastype = terastype
            self.teras_button.icon = terastype.icon
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

    # 中央ボタンが押された時
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
    
class TrainerInfoPanel(BoxLayout):
    name = StringProperty()
    rank = StringProperty()
    memo = StringProperty()

    def __init__(self, **kwargs):
        super(TrainerInfoPanel, self).__init__(**kwargs)
        self.name = ""
        self.rank = ""
        self.memo = ""
