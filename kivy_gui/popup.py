from typing import Optional
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from gui import PokeNameComboEdit, PartyIconPanel, IconButton
from pokedata.const import Types
from pokedata.pokemon import Pokemon


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
