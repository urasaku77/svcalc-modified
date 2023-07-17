from kivy.app import App
from kivy.properties import ListProperty, ObjectProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy_gui.popup import PartyInputPopup, SpeedCheckPopup, FormSelectPopupContent

from typing import Optional
import atexit
import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2
import dataclasses
from PIL import Image as Picture
import glob

from gui import *
from pokedata.pokemon import Pokemon
from pokedata.const import *
from battle.battle import Battle
from battle.DB_battle import DB_battle
from recog.image_recognition import ImageRecognition
from home.home import unrecognizable_pokemon

class PageBattleWidget(BoxLayout):
    cameraPreview = ObjectProperty()
    cameraId = NumericProperty(1)
    partyPanels = ListProperty()
    activePokemonPanels = ListProperty()
    wazaListPanels = ListProperty()
    wazaRateList = ListProperty(["","","","","","","","","",""])
    playerChosenPokemonPanel = ObjectProperty
    opponentChosenPokemonPanels = ListProperty()
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
        self.formSelect = Popup(
            title="フォーム選択",
            content=FormSelectPopupContent(selected=self.set_opponent_pokemon_form),
            size_hint=(0.8, 0.6))


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

    def select_player_chosen_pokemon(self):
        pokemon = self.active_pokemons[0]
        if pokemon is not None:
            self.playerChosenPokemonPanel.set_pokemon(pokemon)
            self.playerChosenPokemonPanel.set_func_for_click_icon(self.refresh_waza_check)

    def select_opponent_chosen_pokemon(self):
        pokemon = self.active_pokemons[1]
        if pokemon is None or str(pokemon.no) in [self.opponentChosenPokemonPanels[0].no, self.opponentChosenPokemonPanels[1].no, self.opponentChosenPokemonPanels[2].no]:
            return
        for chosen_num in range(3):
            if self.opponentChosenPokemonPanels[chosen_num].name == "":
                self.opponentChosenPokemonPanels[chosen_num].set_pokemon(pokemon)
                self.opponentChosenPokemonPanels[chosen_num].set_func_for_change(self.change_opponent_chosen_terastype, 0)
                self.opponentChosenPokemonPanels[chosen_num].set_func_for_change(self.change_opponent_chosen_item, 1)
                self.opponentChosenPokemonPanels[chosen_num].set_func_for_change(self.change_opponent_chosen_ability, 2)
                break

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
            self.timerLabel.stop()
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
        if self.activePokemonPanels[player_id].pokemon is not None and pokemon.name == self.activePokemonPanels[player_id].pokemon.name:
            return
        if player_id == 1 and pokemon.form == -1:
            self.formSelect.content.set_pokemons(pokemon.no)
            self.formSelect.open()
            return
        pokemon.on_stage()
        wall = Walls.なし
        if self.active_pokemons[player_id] is not None:
            self.active_pokemons[player_id].statechanged_handler = None
            wall = self.active_pokemons[player_id].wall
        self.active_pokemons[player_id] = pokemon
        self.active_pokemons[player_id].wall = wall
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
        if player_id == 0:
            self.refresh_waza_check()
            self.activePokemonPanels[player_id].set_func_for_click_icon(self.select_player_chosen_pokemon)
        else:
            self.activePokemonPanels[player_id].set_func_for_click_icon(self.select_opponent_chosen_pokemon)

    def set_opponent_pokemon_form(self, name: str):
        pokemon = Pokemon(DB.get_pokemon_data_by_name(name))
        pokemon.set_default_data()
        for i in range(len(self.party)):
            if self.party[1][i].no == pokemon.no:
                self.set_party_pokemon(1, i, pokemon)
                break
        self.set_active_pokemon(1, pokemon)
        self.formSelect.dismiss()

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
        if self.pokemonInfoPanels[0] is not None and self.active_pokemons[0] is not None: self.pokemonInfoPanels[0].set_pokemon(self.active_pokemons[0])
        if self.pokemonInfoPanels[1] is not None and self.active_pokemons[1] is not None: self.pokemonInfoPanels[1].set_pokemon(self.active_pokemons[1])
        if self.activePokemonPanels[0] is not None: self.activePokemonPanels[0].change_ranks()
        if self.activePokemonPanels[1] is not None: self.activePokemonPanels[1].change_ranks()

    def refresh_waza_check(self):
        if self.active_pokemons[0] is None:
            return
        waza_check_list = self.playerChosenPokemonPanel.get_waza_check(self.active_pokemons[0].name)
        for waza_check in range(len(waza_check_list)):
            id = "waza_check_" + str(waza_check)
            if waza_check_list[waza_check] == 1:
                self.ids[id].text = "使用"
            else:
                self.ids[id].text = ""

    def set_player_waza(self, waza_index: int):
        for pokemon_index in range(3):
            if self.playerChosenPokemonPanel.name[pokemon_index] != "" and self.playerChosenPokemonPanel.name[pokemon_index] == self.active_pokemons[0].name:
                self.playerChosenPokemonPanel.change_waza_check(pokemon_index, waza_index)
                self.refresh_waza_check()

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

    def change_opponent_chosen_item(self, name:str, item):
        for i in range(6):
            if self.party[1][i] is not None and self.party[1][i].name == name:
                self.party[1][i].item = item
                if self.active_pokemons[1] is not None and self.active_pokemons[1].name == name:
                    self.activePokemonPanels[1].pokemon.item = item
                    self.activePokemonPanels[1].ids["item"].text = item

    def change_opponent_chosen_ability(self, name:str, ability):
        for i in range(6):
            if self.party[1][i] is not None and self.party[1][i].name == name:
                self.party[1][i].ability = ability
                if self.active_pokemons[1] is not None and self.active_pokemons[1].name == name:
                    self.activePokemonPanels[1].set_ability(ability)

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
                if oppo_pokemon.base_name in unrecognizable_pokemon:
                    tentative_oppo_pokemon = Pokemon()
                    tentative_oppo_pokemon.no = oppo_pokemon.no
                    oppo_pokemon = tentative_oppo_pokemon
                self.set_party_pokemon(1, coord, oppo_pokemon)

    def recognize_player_banme(self):
        if self.cameraPreview.imgRecog.is_banme():
            return
        for banme in range(3):
            banmeResult =self.cameraPreview.imgRecog.recognize_chosen_num(banme)
            if banmeResult != -1 and self.party[0][banmeResult] is not None:
                self.playerChosenPokemonPanel.set_pokemon(self.party[0][banmeResult])

    def recognize_oppo_tn(self):
        self.ids["tn"].text = self.cameraPreview.imgRecog.recognize_oppo_tn() or ""

    def init_active_pokemon(self):
        for activePokemonPanel in self.activePokemonPanels:
            activePokemonPanel.init_pokemon()
        for wazaListPanel in self.wazaListPanels:
            wazaListPanel.initWazaPanels()
        self.wazaRateList = ["","","","","","","","","",""]
        for pokemonInfoPanel in self.pokemonInfoPanels:
            pokemonInfoPanel.init_pokemon()
        for homeInfoPanel in self.homeInfoPanels:
            homeInfoPanel.init_data()
        self.active_pokemons: list[Optional[Pokemon]] = [None, None]

    def init_battle(self):
        self.battle_status = False
        self.ids["tn"].text = ""
        self.ids["rank"].text = ""
        self.ids["trainer_memo"].text = ""
        self.ids["battle_memo"].text = ""
        self.ids["weather"].text = "なし"
        self.ids["field"].text = "なし"
        self.ids["evaluation"].text = "なし"
        self.ids["favorite"].active = False
        self.party[1] = [None for _ in range(6)]
        self.refresh_party_icons()
        for chosen_num in range(len(self.opponentChosenPokemonPanels)):
            self.opponentChosenPokemonPanels[chosen_num].on_click_icon()
        for chosen_num in range(3):
            self.playerChosenPokemonPanel.on_click_icon(chosen_num)
        self.init_active_pokemon()

    def record_battle(self, result: int):
        if self.party[0][0] is None or self.party[1][0] is None:
            return
        time = 20*60 - ( int(self.timerLabel.minutes) + int(self.timerLabel.seconds)*60 )
        favorite = 1 if self.ids["favorite"].active is True else 0
        evaluation = int(self.ids["evaluation"].text) if self.ids["evaluation"].text != "なし" else 0

        battle = Battle.set_battle(self.ids["tn"].text, self.ids["rank"].text, self.ids["trainer_memo"].text, self.ids["battle_memo"].text, self.party, self.playerChosenPokemonPanel, self.opponentChosenPokemonPanels, time, result, evaluation, favorite)
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
