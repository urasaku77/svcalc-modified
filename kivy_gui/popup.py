from typing import Optional
from kivy.clock import Clock
from kivy.properties import ObjectProperty, ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from gui import PokeNameComboEdit, PartyIconPanel, IconButton
from pokedata.const import Types
from pokedata.pokemon import Pokemon
from data.db import DB

class InputPopup(Popup):
    pass


# パーティ入力用ポップアップ
class PartyInputPopup(InputPopup):

    __events__ = ("on_popup_close",)

    def __init__(self, **kwargs) -> None:
        super(PartyInputPopup, self).__init__(**kwargs)
        self.__party: list[Optional[Pokemon]] = []
        self.content: PartyInputPopupContent = PartyInputPopupContent()
        self.content.bind(on_complete=lambda _: self.dispatch("on_popup_close"))
        self.bind(on_open=lambda _: self.content.on_open(self.party))

    def on_popup_close(self, *args):
        pass

    @property
    def party(self):
        return self.__party

    @party.setter
    def party(self, value):
        self.__party = value


# パーティ入力用ポップアップコンテンツ
class PartyInputPopupContent(BoxLayout):

    __events__ = ("on_complete",)

    def __init__(self, **kwargs):
        super(PartyInputPopupContent, self).__init__(**kwargs)
        self.party: list[Optional[Pokemon]] = []

    def on_open(self, party: list[Optional[Pokemon]]):
        self.party = party
        for i, pokemon in enumerate(self.party):
            self.party_panel.buttons[i].pokemon_name = "" if pokemon is None else pokemon.name
        self.party_panel.select(0)
        self.on_select_party(0)
        self.pokename_input.focus = True

    # ポケモン名が入力された時
    def on_input_name(self, name: str):
        idx = self.party_panel.selected_index
        pokemon: Pokemon = Pokemon.by_name(name, default=True)
        self.party[idx] = pokemon
        self.party_panel.buttons[idx].pokemon_name = pokemon.name

        next_idx = min(idx+1, 5)
        self.pokename_input.text = ""
        self.party_panel.select(next_idx)
        self.on_select_party(next_idx)
        Clock.schedule_once(
            lambda _: self.set_focus_to_textinput(idx), 0.1)

    # パーティパネルのトグルボタンが選択された時
    def on_select_party(self, index):
        if self.party[index] is not None:
            self.pokename_input.hint_text = self.party[index].name
        else:
            self.pokename_input.hint_text = str(index+1) + "匹目のポケモン名を入力"

    @property
    def pokename_input(self) -> PokeNameComboEdit:
        return self.ids["_input"]

    @property
    def party_panel(self) -> PartyIconPanel:
        return self.ids["_party"]

    def set_focus_to_textinput(self, idx: int):
        self.pokename_input.focus = True

    def on_complete(self, *args):
        pass


# タイプ選択ポップアップ用コンテンツ
class TypeSelectPopupContent(GridLayout):
    selected = ObjectProperty(None)

    def __init__(self, **kw):
        super(TypeSelectPopupContent, self).__init__(**kw)
        self.cols = 4
        self.spacing = [5]
        for types in Types:
            self.add_widget(IconButton(
                icon=types.icon,
                size_hint_y=None, height=40,
                button_text=types.name,
                on_press=lambda btn: self.selected(btn.text)))


# パーティCSV選択ポップアップ
class PartyChooserPopup(Popup):
    __events__ = ("on_submit",)


# パーティCSV選択ポップアップコンテンツ
class PartyChooserPopupContent(BoxLayout):
    __events__ = ("on_submit", )

    def __init__(self, **kw):
        super(PartyChooserPopupContent, self).__init__(**kw)
        self.__filename: str = ""

    @property
    def filename(self) -> str:
        return self.__filename

    def submit(self, filename: str):
        self.__filename = filename
        self.dispatch("on_submit")

    def on_submit(self, *args):
        pass

# 素早さ比較ポップアップ
class SpeedCheckPopup(Popup):
    players_pokemon = ObjectProperty()
    opponent_pokemon = ObjectProperty()
    syuzokus = ListProperty([0, 0])
    kotais = ListProperty([31, 31])
    doryokus = ListProperty([252, 252])
    seikakus = ListProperty([1.0, 1.0])
    ranks = ListProperty([6, 6])
    abilities = ListProperty([1.0, 1.0])
    items = ListProperty([1.0, 1.0])
    winds = ListProperty([1.0, 1.0])
    binds = ListProperty([1.0, 1.0])
    results = ListProperty([0, 0])
    compare = StringProperty("=")

    player_scarf = ObjectProperty(False)
    player_seikaku_up = ObjectProperty(False)
    player_seikaku_down = ObjectProperty(False)
    rank = ["-6", "-5", "-4", "-3", "-2", "-1", "0", "1", "2", "3", "4", "5", "6"]

    def set_pokemon(self, active_pokemons: list[Optional[Pokemon]]):
        self.players_pokemon = active_pokemons[0]
        self.opponent_pokemon= active_pokemons[1]

        self.syuzokus[0] = self.players_pokemon.syuzoku.S
        self.syuzokus[1] = self.opponent_pokemon.syuzoku.S

        self.kotais[0] = self.players_pokemon.kotai.S
        self.ids["player_kotai"].text = str(self.players_pokemon.kotai.S)
        self.doryokus[0] = self.players_pokemon.doryoku.S
        self.ids["player_doryoku"].text = str(self.players_pokemon.doryoku.S)
        self.ranks = [self.rank.index(str(self.players_pokemon.rank.S)), self.rank.index(str(self.opponent_pokemon.rank.S))]
        self.ids["player_rank"].text = str(self.rank[self.ranks[0]])
        self.ids["opponent_rank"].text = str(self.rank[self.ranks[1]])

        self.set_player_status()
        self.calc_speed()

    def set_player_status(self):
        if self.players_pokemon.seikaku in ["おくびょう","せっかち","やんちゃ","ようき",]:
            self.player_seikaku_up = True
            self.seikakus[0] = 1.1
        if self.players_pokemon.seikaku in ["ゆうかん","のんき","れいせい","なまいき",]:
            self.player_seikaku_down = True
            self.seikakus[0] = 0.9
        if self.players_pokemon.item == "こだわりスカーフ":
            self.player_scarf = True
            self.items[0] = 1.5

    def set_kotai(self, player: int, value: str):
        if value.isdecimal():
            self.kotais[player] = int(value)
            if player == 0:
                self.ids["player_kotai"].text = value
            else:
                self.ids["opponent_kotai"].text = value
        else:
            self.kotais[player] = 0
        self.calc_speed()

    def set_doryoku(self, player: int, value: str):
        if value.isdecimal():
            self.doryokus[player] = int(value)
            if player == 0:
                self.ids["player_doryoku"].text = value
            else:
                self.ids["opponent_doryoku"].text = value
        else:
            self.doryokus[player] = 0
        self.calc_speed()

    def set_seikaku(self, player: int, value: float):
        if self.seikakus[player] == value:
            self.seikakus[player] = 1.0
        else:
            self.seikakus[player] = value
        self.calc_speed()

    def set_rank(self, player: int, is_up: bool):
        if not is_up and self.ranks[player] > 0:
            self.ranks[player] = self.ranks[player] - 1
        elif is_up and self.ranks[player] < 12:
            self.ranks[player] = self.ranks[player] + 1
        self.calc_speed()

    def set_ability(self, player: int, value: float):
        if self.abilities[player] == value:
            self.abilities[player] = 1.0
        else:
            self.abilities[player] = value
        self.calc_speed()

    def set_item(self, player: int, value: float):
        if self.items[player] == value:
            self.items[player] = 1.0
        else:
            self.items[player] = value
        self.calc_speed()

    def set_wind(self, player: int):
        self.winds[player] = 1.0 if self.winds[player] != 1.0 else 2.0
        print(self.winds[player])
        self.calc_speed()

    def set_bind(self, player: int):
        self.binds[player] = 1.0 if self.binds[player] != 1.0 else 0.5
        print(self.binds[player])
        self.calc_speed()

    def calc_speed(self):
        base = [( ( self.syuzokus[0] * 2 + self.kotais[0] + self.doryokus[0] / 4 ) * 50 / 100 +5 ) * self.seikakus[0] * self.abilities[0] * self.items[0] * self.winds[0] * self.binds[0], ( ( self.syuzokus[1] * 2 + self.kotais[1] + self.doryokus[1] / 4 ) * 50 / 100 +5 ) * self.seikakus[1] * self.abilities[1] * self.items[1] * self.winds[1] * self.binds[1]]

        for i in range(2):
            match self.rank[self.ranks[i]]:
                case "0":
                    self.results[i] = int(base[i])
                case "1":
                    self.results[i] = int(base[i] * 1.5)
                case "-1":
                    self.results[i] = int(base[i] * 2 / 3)
                case "2":
                    self.results[i] = int(base[i] * 2)
                case "-2":
                    self.results[i] = int(base[i] / 2)
                case "3":
                    self.results[i] = int(base[i] * 2.5)
                case "-3":
                    self.results[i] = int(base[i] * 2 / 5)
                case "4":
                    self.results[i] = int(base[i] * 3)
                case "-4":
                    self.results[i] = int(base[i] / 3)
                case "5":
                    self.results[i] = int(base[i] * 3.5)
                case "-5":
                    self.results[i] = int(base[i] * 2 / 7)
                case "6":
                    self.results[i] = int(base[i] * 4)
                case "-6":
                    self.results[i] = int(base[i] / 4)

        if self.results[0] < self.results[1]:
            self.compare = "<"
        elif self.results[0] > self.results[1]:
            self.compare = ">"
        else:
            self.compare = "="

# パーティ登録用ポップアップ
class PartyRegisterPopup(Popup):

    def __init__(self, **kwargs) -> None:
        super(PartyRegisterPopup, self).__init__(**kwargs)
        self.bind(on_open=lambda _: self.content.on_open())

# パーティ登録用ポップアップコンテンツ
class PartyRegisterPopupContent(BoxLayout):

    selected = ObjectProperty(None)

    def __init__(self, **kwargs) -> None:
        super(PartyRegisterPopupContent, self).__init__(**kwargs)

    def on_open(self):
        if self.pokename_input.text == "":
            self.pokename_input.focus = True

    @property
    def pokename_input(self) -> PokeNameComboEdit:
        return self.ids["_input"]

    # ポケモン名が入力された時
    def on_input_name(self, name: str):
        pokemon: Pokemon = Pokemon.by_name(name, default=True)
        self.selected(pokemon)

    def clear(self):
        self.selected(None)
        self.pokename_input.text = ""

# 編集パーティCSV選択用ポップアップ
class CsvChooserPopup(InputPopup):
    selected = ObjectProperty(None)

    def __init__(self, **kwargs) -> None:
        super(CsvChooserPopup, self).__init__(**kwargs)

    def select(self, csv:str):
        self.selected(csv)

# フォルム選択用ポップアップ
class FormSelectPopupContent(GridLayout):
    no = StringProperty("")
    selected = ObjectProperty(None)

    def __init__(self, **kw):
        super(FormSelectPopupContent, self).__init__(**kw)

    def set_pokemons(self, num):
        self.clear_widgets()
        self.no = str(num)
        self.pokemon_names = DB.get_pokemons_name_by_no(self.no)
        self.cols = 1
        self.spacing = [5]
        for i in range(len(self.pokemon_names)):
            print(self.pokemon_names[i])
            btn = IconButton(
                icon="image/pokeicon/" + self.no + "-" + str(i) + ".png",
                size_hint_y=None, height=60,
                button_text=str(self.pokemon_names[i]))
            btn.bind(on_press=lambda btn: self.selected(btn.text))
            self.add_widget(btn)