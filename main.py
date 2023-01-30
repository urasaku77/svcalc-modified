from kivy.app import App
from kivy.properties import ListProperty, StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path
from kivy_gui.popup import PartyInputPopup
from pokedata.pokemon import Pokemon
from data.db import DB

from battle.battle import Battle
from battle.DB_battle import DB_battle

from typing import Optional
import atexit
import cv2
import datetime
import dataclasses

Window.size = (2400, 1200)
resource_add_path("font")
LabelBase.register(DEFAULT_FONT, "NotoSansJP-Medium.otf")


class RootWidget(BoxLayout):
    partyPanels = ListProperty()
    activePokemonPanels = ListProperty()
    wazaListPanels = ListProperty()
    chosenPokemonPanels = ListProperty()
    trainerInfoPanels = ListProperty()
    timerLabel = ObjectProperty()

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.active_pokemons: list[Optional[Pokemon]] = [None, None]
        self.party_popup: PartyInputPopup = PartyInputPopup(title="パーティ入力")
        self.party_popup.bind(
            on_popup_close=lambda _: self.submit_party())
        self.party: list[list[Optional[Pokemon]]] = [
            [None for _ in range(6)], [None for _ in range(6)]
        ]
        self.result = 2

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
            self.chosenPokemonPanels[player_id][chosen_num].set_pokemon(player_id, pokemon)
            


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

    def set_opponent_waza(self, waza_index: int):
        waza_name = self.wazaListPanels[1].wazapanel_list[waza_index].waza_button.text
        for pokemon_index in range(len(self.chosenPokemonPanels[1])):
            if self.chosenPokemonPanels[1][pokemon_index].name != "" and self.chosenPokemonPanels[1][pokemon_index].name == self.active_pokemons[1].name:
                self.chosenPokemonPanels[1][pokemon_index].register_chosen_waza(waza_name)
    
    def change_result(self, checkbox, result: int):
        if checkbox.active is False:
            self.result = 2
        else:
            self.result = result
    
    def init_battle(self):
        self.result = 2
        self.trainerInfoPanels[0].clear(True)
        self.trainerInfoPanels[1].clear(False)
        self.party[1] = [None for _ in range(6)]
        # self.active_pokemons = [None, None]
        self.refresh_party_icons()
        for player in range(len(self.chosenPokemonPanels)):
            for chosen_num in range(len(self.chosenPokemonPanels[player])):
                self.chosenPokemonPanels[player][chosen_num].on_click_icon()

    def record_battle(self):
        time = 20*60 - ( int(self.timerLabel.minutes) + int(self.timerLabel.seconds)*60 )
        self.trainerInfoPanels[0].update()
        self.trainerInfoPanels[1].update()

        battle = Battle(
            None, 
            str(datetime.datetime.now()), 
            time, 
            self.result,
            self.trainerInfoPanels[0].name, 
            self.trainerInfoPanels[1].name, 
            self.trainerInfoPanels[0].rank, 
            self.trainerInfoPanels[1].rank, 
            self.trainerInfoPanels[0].memo, 
            self.trainerInfoPanels[1].memo, 
            self.party[0][0].name if self.party[0][0] is not None else "", 
            self.party[0][1].name if self.party[0][1] is not None else "", 
            self.party[0][2].name if self.party[0][2] is not None else "", 
            self.party[0][3].name if self.party[0][3] is not None else "", 
            self.party[0][4].name if self.party[0][4] is not None else "", 
            self.party[0][5].name if self.party[0][5] is not None else "", 
            self.party[1][0].name if self.party[1][0] is not None else "", 
            self.party[1][1].name if self.party[1][1] is not None else "", 
            self.party[1][2].name if self.party[1][2] is not None else "", 
            self.party[1][3].name if self.party[1][3] is not None else "", 
            self.party[1][4].name if self.party[1][4] is not None else "", 
            self.party[1][5].name if self.party[1][5] is not None else "", 
            self.chosenPokemonPanels[0][0].name, 
            self.chosenPokemonPanels[0][0].doryoku, 
            self.chosenPokemonPanels[0][0].item, 
            self.chosenPokemonPanels[0][0].ability, 
            self.chosenPokemonPanels[0][0].terastype.name, 
            self.chosenPokemonPanels[0][0].chosenWazaListPanel.wazapanel_list[0].waza if self.chosenPokemonPanels[0][0].name != "" else "", 
            self.chosenPokemonPanels[0][0].chosenWazaListPanel.wazapanel_list[1].waza if self.chosenPokemonPanels[0][0].name != "" else "", 
            self.chosenPokemonPanels[0][0].chosenWazaListPanel.wazapanel_list[2].waza if self.chosenPokemonPanels[0][0].name != "" else "", 
            self.chosenPokemonPanels[0][0].chosenWazaListPanel.wazapanel_list[3].waza if self.chosenPokemonPanels[0][0].name != "" else "", 
            self.chosenPokemonPanels[0][1].name, 
            self.chosenPokemonPanels[0][1].doryoku, 
            self.chosenPokemonPanels[0][1].item, 
            self.chosenPokemonPanels[0][1].ability, 
            self.chosenPokemonPanels[0][1].terastype.name, 
            self.chosenPokemonPanels[0][1].chosenWazaListPanel.wazapanel_list[0].waza if self.chosenPokemonPanels[0][1].name != "" else "", 
            self.chosenPokemonPanels[0][1].chosenWazaListPanel.wazapanel_list[1].waza if self.chosenPokemonPanels[0][1].name != "" else "", 
            self.chosenPokemonPanels[0][1].chosenWazaListPanel.wazapanel_list[2].waza if self.chosenPokemonPanels[0][1].name != "" else "", 
            self.chosenPokemonPanels[0][1].chosenWazaListPanel.wazapanel_list[3].waza if self.chosenPokemonPanels[0][1].name != "" else "", 
            self.chosenPokemonPanels[0][2].name, 
            self.chosenPokemonPanels[0][2].doryoku, 
            self.chosenPokemonPanels[0][2].item, 
            self.chosenPokemonPanels[0][2].ability, 
            self.chosenPokemonPanels[0][2].terastype.name, 
            self.chosenPokemonPanels[0][2].chosenWazaListPanel.wazapanel_list[0].waza if self.chosenPokemonPanels[0][2].name != "" else "", 
            self.chosenPokemonPanels[0][2].chosenWazaListPanel.wazapanel_list[1].waza if self.chosenPokemonPanels[0][2].name != "" else "", 
            self.chosenPokemonPanels[0][2].chosenWazaListPanel.wazapanel_list[2].waza if self.chosenPokemonPanels[0][2].name != "" else "", 
            self.chosenPokemonPanels[0][2].chosenWazaListPanel.wazapanel_list[3].waza if self.chosenPokemonPanels[0][2].name != "" else "", 
            self.chosenPokemonPanels[1][0].name, 
            self.chosenPokemonPanels[1][0].doryoku, 
            self.chosenPokemonPanels[1][0].item, 
            self.chosenPokemonPanels[1][0].ability, 
            self.chosenPokemonPanels[1][0].terastype.name, 
            self.chosenPokemonPanels[1][0].chosenWazaListPanel.wazapanel_list[0].waza if self.chosenPokemonPanels[1][0].name != "" else "", 
            self.chosenPokemonPanels[1][0].chosenWazaListPanel.wazapanel_list[1].waza if self.chosenPokemonPanels[1][0].name != "" else "", 
            self.chosenPokemonPanels[1][0].chosenWazaListPanel.wazapanel_list[2].waza if self.chosenPokemonPanels[1][0].name != "" else "", 
            self.chosenPokemonPanels[1][0].chosenWazaListPanel.wazapanel_list[3].waza if self.chosenPokemonPanels[1][0].name != "" else "", 
            self.chosenPokemonPanels[1][1].name, 
            self.chosenPokemonPanels[1][1].doryoku, 
            self.chosenPokemonPanels[1][1].item, 
            self.chosenPokemonPanels[1][1].ability, 
            self.chosenPokemonPanels[1][1].terastype.name, 
            self.chosenPokemonPanels[1][1].chosenWazaListPanel.wazapanel_list[0].waza if self.chosenPokemonPanels[1][1].name != "" else "", 
            self.chosenPokemonPanels[1][1].chosenWazaListPanel.wazapanel_list[1].waza if self.chosenPokemonPanels[1][1].name != "" else "", 
            self.chosenPokemonPanels[1][1].chosenWazaListPanel.wazapanel_list[2].waza if self.chosenPokemonPanels[1][1].name != "" else "", 
            self.chosenPokemonPanels[1][1].chosenWazaListPanel.wazapanel_list[3].waza if self.chosenPokemonPanels[1][1].name != "" else "", 
            self.chosenPokemonPanels[1][2].name, 
            self.chosenPokemonPanels[1][2].doryoku, 
            self.chosenPokemonPanels[1][2].item, 
            self.chosenPokemonPanels[1][2].ability, 
            self.chosenPokemonPanels[1][2].terastype.name, 
            self.chosenPokemonPanels[1][2].chosenWazaListPanel.wazapanel_list[0].waza if self.chosenPokemonPanels[1][2].name != "" else "", 
            self.chosenPokemonPanels[1][2].chosenWazaListPanel.wazapanel_list[1].waza if self.chosenPokemonPanels[1][2].name != "" else "", 
            self.chosenPokemonPanels[1][2].chosenWazaListPanel.wazapanel_list[2].waza if self.chosenPokemonPanels[1][2].name != "" else "", 
            self.chosenPokemonPanels[1][2].chosenWazaListPanel.wazapanel_list[3].waza if self.chosenPokemonPanels[1][2].name != "" else ""
            )
        battle_data = dataclasses.astuple(battle)
        print(battle_data)
        DB_battle.register_battle(battle_data)

        self.init_battle()

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
