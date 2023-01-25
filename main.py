import atexit
from typing import Optional

from kivy.app import App
from kivy.properties import ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.uix.image import Image

from kivy_gui.popup import PartyInputPopup
from pokedata.pokemon import Pokemon
from data.db import DB

from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path

import cv2

Window.size = (2400, 1200)
resource_add_path("font")
LabelBase.register(DEFAULT_FONT, "NotoSansJP-Medium.otf")


class RootWidget(BoxLayout):
    partyPanels = ListProperty()
    activePokemonPanels = ListProperty()
    choosePokemonPanels = ListProperty()
    wazaListPanels = ListProperty()
    opponentWazaListPanels = ListProperty()
    chosenPokemonPanels = ListProperty()
    status = StringProperty("")

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.active_pokemons: list[Optional[Pokemon]] = [None, None]
        self.chosen_pokemons: list[list[Optional[Pokemon]]] = [
            [None for _ in range(3)], [None for _ in range(3)]
        ]
        self.party_popup: PartyInputPopup = PartyInputPopup(title="パーティ入力")
        self.party_popup.bind(
            on_popup_close=lambda _: self.submit_party())
        self.party: list[list[Optional[Pokemon]]] = [
            [None for _ in range(6)], [None for _ in range(6)]
        ]

    def load_party(self):
        from pokedata.loader import get_party_data
        for i, data in enumerate(get_party_data()):
            pokemon: Pokemon = Pokemon.by_name(data[0])
            pokemon.set_load_data(data)
            self.set_party_pokemon(pokemon=pokemon, player_id=0, index=i)

    def edit_party(self, player_id: int):
        self.party_popup.party = self.party[player_id]
        self.party_popup.open()

    def submit_party(self):
        self.refresh_party_icons()
        self.party_popup.dismiss()

    def select_party_pokemon(self, player_id: int, index: int):
        pokemon = self.party[player_id][index]
        if pokemon is not None:
            self.set_active_pokemon(player_id, pokemon)
    
    def select_chosen_pokemon(self, player_id: int, chosen_num: int):
        pokemon = self.active_pokemons[player_id]
        if pokemon is not None:
            self.set_chosen_pokemon(player_id, chosen_num, pokemon)


    # パーティパネルのアイコンを再表示する
    def refresh_party_icons(self):
        for i in range(0, 2):
            pnl = self.partyPanels[i]
            for p in range(0, 6):
                pokemon = self.party[i][p]
                icon = pokemon.icon if pokemon is not None else None
                pnl.set_pokemon_icon(p, icon)

    def clear_party(self, player_id: int):
        for i in range(6):
            # データ処理
            self.party[player_id][i] = None
            # GUi処理
            self.refresh_party_icons()

    def set_party_pokemon(self, player_id: int, index: int, pokemon: Optional[Pokemon]):
        # データ処理
        party = self.party[player_id]
        party[index] = pokemon
        # GUi処理
        self.refresh_party_icons()

    def set_active_pokemon(self, player_id: int, pokemon: Pokemon):
        # データ処理
        pokemon.on_stage()
        if self.active_pokemons[player_id] is not None:
            self.active_pokemons[player_id].statechanged_handler = None
        self.active_pokemons[player_id] = pokemon
        self.active_pokemons[player_id].statechanged_handler = self.pokemon_state_changed
        # GUI処理
        self.activePokemonPanels[player_id].pokemon = pokemon
        self.wazaListPanels[player_id].set_pokemon(pokemon)
        self.calc_damage()
    
    def set_chosen_pokemon(self, player_id:int, chosen_num: int, pokemon: Pokemon):
        chosen_pokemons = self.chosen_pokemons[player_id]
        # データ処理
        pokemon.on_stage()
        if chosen_pokemons[chosen_num] is not None:
            chosen_pokemons[chosen_num].statechanged_handler = None
        chosen_pokemons[chosen_num] = pokemon
        chosen_pokemons[chosen_num].statechanged_handler = self.pokemon_state_changed
        # GUI処理
        self.chosenPokemonPanels[player_id][chosen_num].pokemon = pokemon

    def calc_damage(self):
        pokemon1 = self.active_pokemons[0]
        pokemon2 = self.active_pokemons[1]

        if pokemon1 is not None and pokemon2 is not None:
            from pokedata.calc import DamageCalc
            # ダメージ計算１
            results = DamageCalc.get_all_damages(pokemon1, pokemon2)
            self.wazaListPanels[0].set_damage_calc_results(results)
            # ダメージ計算２
            results = DamageCalc.get_all_damages(pokemon2, pokemon1)
            self.wazaListPanels[1].set_damage_calc_results(results)

    def pokemon_state_changed(self):
        self.calc_damage()

# カメラに接続
class CameraPreview(Image):
    def __init__(self, **kwargs):
        super(CameraPreview, self).__init__(**kwargs)
        self.capture = cv2.VideoCapture(1)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        Clock.schedule_interval(self.update, 1.0 / 60)

    # インターバルで実行する描画メソッド
    def update(self, dt):
        # フレームを読み込み
        ret, self.frame = self.capture.read()
        # Kivy Textureに変換
        buf = cv2.flip(self.frame, 0).tostring()
        texture = Texture.create(size=(self.frame.shape[1], self.frame.shape[0]), colorfmt='bgr') 
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # インスタンスのtextureを変更
        self.texture = texture


class MainApp(App):
    pass


# 終了時処理
def cleanup():
    print("cleanup")


if __name__ == '__main__':
    atexit.register(cleanup)
    MainApp().run()
