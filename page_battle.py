from kivy.app import App
from kivy.properties import ListProperty, ObjectProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy_gui.popup import PartyInputPopup, SpeedCheckPopup

from typing import Optional
import atexit
import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2
import dataclasses
from PIL import Image as Picture
import glob

from pokedata.pokemon import Pokemon
from pokedata.const import Weathers, Fields
from battle.battle import Battle
from battle.DB_battle import DB_battle
from recog.image_recognition import ImageRecognition

class PageBattleWidget(BoxLayout):
    cameraPreview = ObjectProperty()
    cameraId = NumericProperty(1)
    partyPanels = ListProperty()
    activePokemonPanels = ListProperty()
    wazaListPanels = ListProperty()
    wazaRateList = ListProperty(["","","","","","","","","",""])
    playerChosenPokemonPanel = ObjectProperty
    opponentChosenPokemonPanels = ListProperty()
    trainerInfoPanels = ListProperty()
    pokemonInfoPanels = ListProperty()
    homeInfoPanels = ListProperty()
    timerLabel = ObjectProperty()
    weather=ObjectProperty(Weathers.なし)
    field=ObjectProperty(Fields.なし)

    def __init__(self, **kwargs):
        super(PageBattleWidget, self).__init__(**kwargs)
        self.cameraPreview = self.CameraPreview(size=(1280,720))
        self.active_pokemons: list[Optional[Pokemon]] = [None, None]
        self.party_popup: PartyInputPopup = PartyInputPopup(title="パーティ入力")
        self.party_popup.bind(
            on_popup_close=lambda _: self.submit_party())
        self.party: list[list[Optional[Pokemon]]] = [
            [None for _ in range(6)], [None for _ in range(6)]
        ]
        self.battle_status = False
        self.result = 2

    def load_party(self):
        from pokedata.loader import get_party_data
        for i, data in enumerate(get_party_data()):
            pokemon: Pokemon = Pokemon.by_name(data[0])
            pokemon.set_load_data(data, True)
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

    def select_player_chosen_pokemon(self, chosen_num: int):
        pokemon = self.active_pokemons[0]
        if pokemon is not None:
            self.playerChosenPokemonPanel.set_pokemon(chosen_num,pokemon)

    def select_opponent_chosen_pokemon(self, chosen_num: int):
        pokemon = self.active_pokemons[1]
        if pokemon is not None:
            self.opponentChosenPokemonPanels[chosen_num].set_pokemon(pokemon)
            self.opponentChosenPokemonPanels[chosen_num].set_func_for_terastype(self.change_opponent_chosen_terastype)

    def set_camera(self):
        self.cameraId = int(self.ids["camera_id"].text)
        self.cameraPreview.start(self.cameraId)
        Clock.schedule_interval(self.cameraPreview.update, 1.0 / 60)
        Clock.schedule_interval(self.start_battle, 1.0 / 60)

    def start_battle(self, dt):
        if not self.cameraPreview.imgRecog.img_flag:
            Clock.unschedule(self.start_battle)
            return
        if not self.battle_status and self.cameraPreview.imgRecog.is_exist_image("recog/recogImg/situation/aitewomiru.jpg",0.8,"aitewomiru"):
            self.timerLabel.start()
            self.battle_status = True

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
            self.party[player_id][i] = None
            self.refresh_party_icons()

    def set_party_pokemon(self, player_id: int, index: int, pokemon: Optional[Pokemon]):
        party = self.party[player_id]
        party[index] = pokemon
        self.refresh_party_icons()

    def set_active_pokemon(self, player_id: int, pokemon: Pokemon):
        pokemon.on_stage()
        if self.active_pokemons[player_id] is not None:
            self.active_pokemons[player_id].statechanged_handler = None
        self.active_pokemons[player_id] = pokemon
        self.active_pokemons[player_id].statechanged_handler = self.pokemon_state_changed
        self.activePokemonPanels[player_id].pokemon = pokemon
        self.wazaListPanels[player_id].set_pokemon(pokemon)
        self.pokemonInfoPanels[player_id].set_pokemon(pokemon)
        if player_id == 1:
            for homeInfoPanel in self.homeInfoPanels:
                homeInfoPanel.set_home_data(pokemon.name)
            for i in range(10):
                self.wazaRateList[i] = str(pokemon.waza_rate_list[i])
        self.calc_damage()

    def set_weather(self, value):
        for weather in Weathers:
            if weather.name == value:
                self.weather = weather
        self.calc_damage()

    def set_field(self, value):
        for field in Fields:
            if field.name == value:
                self.field = field
        self.calc_damage()

    def calc_damage(self):
        pokemon1 = self.active_pokemons[0]
        pokemon2 = self.active_pokemons[1]

        if pokemon1 is not None and pokemon2 is not None:
            from pokedata.calc import DamageCalc
            # ダメージ計算１
            results = DamageCalc.get_all_damages(pokemon1, pokemon2, self.weather, self.field)
            self.wazaListPanels[0].set_damage_calc_results(results)
            # ダメージ計算２
            results = DamageCalc.get_all_damages(pokemon2, pokemon1, self.weather, self.field)
            self.wazaListPanels[1].set_damage_calc_results(results)

    def pokemon_state_changed(self):
        self.calc_damage()
        if self.activePokemonPanels[0] is not None: self.activePokemonPanels[0].change_ranks()
        if self.activePokemonPanels[1] is not None: self.activePokemonPanels[1].change_ranks()

    def set_opponent_waza(self, waza_index: int):
        waza_name = self.wazaListPanels[1].wazapanel_list[waza_index].waza_button.text
        for pokemon_index in range(len(self.opponentChosenPokemonPanels)):
            if self.opponentChosenPokemonPanels[pokemon_index].name != "" and self.opponentChosenPokemonPanels[pokemon_index].name == self.active_pokemons[1].name:
                self.opponentChosenPokemonPanels[pokemon_index].register_chosen_waza(waza_name)

    def change_opponent_chosen_terastype(self, name:str, terastype):
        for i in range(6):
            if self.party[1][i] is not None and self.party[1][i].name == name:
                self.party[1][i].terastype = terastype
                self.party[1][i].battle_terastype = terastype
                if self.active_pokemons[1] is not None and self.active_pokemons[1].name == name:
                    self.activePokemonPanels[1].on_select_terastype(terastype.name)

    def change_result(self, checkbox, result: int):
        if checkbox.active is False:
            self.result = 2
        else:
            self.result = result

    def set_speed_check(self):
        if self.active_pokemons[0] is not None and self.active_pokemons[1] is not None:
            self.speed_check: SpeedCheckPopup = SpeedCheckPopup(title="素早さ比較")
            self.speed_check.set_pokemon(self.active_pokemons)
            self.speed_check.open()

    def recognize_before_battle(self):
        if self.cameraPreview.imgRecog.is_exist_image("recog/recogImg/situation/sensyutu.jpg",0.8,"sensyutu") or self.cameraPreview.imgRecog.is_exist_image("recog/recogImg/situation/sensyutu2.jpg",0.8,"sensyutu"):
            self.recognize_oppo_party()
            self.recognize_player_banme()
            self.recognize_oppo_tn()

    def recognize_oppo_party(self):
        pokemonImages = glob.glob("recog/recogImg/pokemon/**/*")
        coordsList = ["opoPoke1", "opoPoke2", "opoPoke3", "opoPoke4", "opoPoke5", "opoPoke6"]

        for coord in range(len(coordsList)):
            oppo = self.cameraPreview.imgRecog.is_exist_image_max(pokemonImages, 0.7, coordsList[coord])
            if oppo != "":
                oppo_shaped = self.cameraPreview.imgRecog.shape_poke_num(oppo)
                oppo_pokemon = Pokemon.by_pid(oppo_shaped, True)
                self.set_party_pokemon(1, coord, oppo_pokemon)

    def recognize_player_banme(self):
        if self.cameraPreview.imgRecog.is_banme():
            return
        for banme in range(3):
            banmeResult =self.cameraPreview.imgRecog.recognize_chosen_num(banme)
            if banmeResult != -1 and self.party[0][banmeResult] is not None:
                self.playerChosenPokemonPanel.set_pokemon(banme, self.party[0][banmeResult])

    def recognize_oppo_tn(self):
        oppo_tn = self.cameraPreview.imgRecog.recognize_oppo_tn() or ""
        self.trainerInfoPanels[1].set_name(oppo_tn)

    def init_battle(self):
        self.battle_status = False
        self.result = 2
        self.trainerInfoPanels[0].clear(True)
        self.trainerInfoPanels[1].clear(False)
        self.party[1] = [None for _ in range(6)]
        self.refresh_party_icons()
        for chosen_num in range(len(self.opponentChosenPokemonPanels)):
            self.opponentChosenPokemonPanels[chosen_num].on_click_icon()
        for chosen_num in range(3):
            self.playerChosenPokemonPanel.on_click_icon(chosen_num)

    def record_battle(self):
        time = 20*60 - ( int(self.timerLabel.minutes) + int(self.timerLabel.seconds)*60 )
        self.trainerInfoPanels[0].update()
        self.trainerInfoPanels[1].update()

        battle = Battle.set_battle(self.trainerInfoPanels, self.party, self.playerChosenPokemonPanel, self.opponentChosenPokemonPanels, time, self.result)
        battle_data = dataclasses.astuple(battle)
        DB_battle.register_battle(battle_data)
        self.timerLabel.reset()
        self.init_battle()

    # カメラに接続
    class CameraPreview(Image):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.display_dummy_image()
            self.imgRecog=ImageRecognition()

        def start(self, camera_id: int):
            self.capture = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.capture.set(cv2.CAP_PROP_FPS, 60)

        # インターバルで実行する描画メソッド
        def update(self, dt):
            ret, self.frame = self.capture.read()
            if self.frame is not None:
                # Kivy Textureに変換
                buf = cv2.flip(self.frame, 0).tobytes()
                texture = Texture.create(size=(self.frame.shape[1], self.frame.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                # インスタンスのtextureを変更
                self.texture = texture
                self.imgRecog.set_image(cv2.resize(self.frame, None, None, 1.5, 1.5))
            else:
                Clock.unschedule(self.update)
                self.display_dummy_image()
                self.imgRecog.img_flag=False

        def display_dummy_image(self):
            image = Picture.open("image/top.jpg")
            texture = Texture.create(size=image.size)
            texture.blit_buffer(image.tobytes())
            texture.flip_vertical()
            self.texture = texture

class MainApp(App):
    pass

# 終了時処理
def cleanup():
    print("cleanup")

if __name__ == '__main__':
    atexit.register(cleanup)
    MainApp().run()
