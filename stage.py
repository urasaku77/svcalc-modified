import json

from component.app import MainApp
from pokedata.calc import DamageCalc
from pokedata.const import Ailments, Fields, Types, Walls, Weathers
from pokedata.nature import get_default_doryoku
from pokedata.pokemon import Pokemon
from pokedata.stats import Stats
from pokedata.waza import WazaBase


class Stage:
    def __init__(self, app: MainApp):
        self._app = app
        self._party: list[list[Pokemon], list[Pokemon]] = [
            [Pokemon()] * 6,
            [Pokemon()] * 6,
        ]
        self._chosen: list[list[Pokemon], list[Pokemon]] = [
            [Pokemon()] * 3,
            [Pokemon()] * 3,
        ]
        self._active_pokemon: list[Pokemon] = [Pokemon()] * 2
        self._weather: Weathers = Weathers.なし
        self._field: Fields = Fields.なし
        self._app.set_stage(self)

        try:
            with open("recog/setting.json", "r") as json_file:
                self.setting_data = json.load(json_file)
        except FileNotFoundError:
            self.setting_data = {"doryoku_reset_auto": False}

    def get_party(self, index: int) -> list[Pokemon]:
        return self._party[index]

    def set_party(self, index: int, party: list[Pokemon]):
        self._party[index] = party

    def get_active_pokemons(self):
        return self._active_pokemon

    def set_active_pokemon_from_index(self, player: int, index: int):
        if not self._party[player][index].form_selected:
            form = self._app.form_select(self._party[player][index].no)
            if form != -1:
                self._party[player][index] = Pokemon.by_pid(
                    str(self._party[player][index].no) + "-" + str(form), True
                )

        if self._party[player][index].form_selected:
            self.pokemon = self._party[player][index]
            self.pokemon.on_stage()
            if self.pokemon.is_empty is False:
                self.set_active_pokemon(player, self.pokemon)
                self.calc_damage()

    def set_active_pokemon(self, player: int, pokemon: Pokemon):
        # self._active_pokemon[player].statechanged_handler = None
        self._active_pokemon[player] = pokemon
        # self._active_pokemon[player].statechanged_handler = self.on_activepokemon_statechanged
        self._app.set_active_pokemon(player=player, pokemon=pokemon)

        # JSONファイルから設定値を読み取り
        try:
            with open("recog/setting.json", "r") as json_file:
                self.setting_data = json.load(json_file)
        except FileNotFoundError:
            self.setting_data = {"active_chosen_auto": False}

        if self.setting_data["active_chosen_auto"] and player == 1:
            self.set_chosen(1)

    def on_activepokemon_statechanged(self):
        pass

    # 表示ポケモンへの各種値セット
    def set_value_to_active_pokemon(
        self,
        player: int,
        seikaku: str = None,
        doryoku_text: str = None,
        doryoku_number: Stats = None,
        kotai: Stats = None,
        rank: Stats = None,
        item: str = None,
        ability: str = None,
        ability_value: str = None,
        wall: Walls = None,
        terastype: Types = None,
        waza: tuple[int, str] = None,
        waza_effect: int = None,
        critical: bool = False,
        ailment: Ailments = Ailments.なし,
        charging: bool = False,
        is_same: bool = False,
    ):
        pokemon = self._active_pokemon[player]
        if seikaku is not None:
            if is_same and pokemon.seikaku == seikaku:
                pokemon.seikaku = "まじめ"
            else:
                pokemon.seikaku = seikaku
            if player == 1 and self.setting_data["doryoku_reset_auto"]:
                pokemon.doryoku.init_values(0)
                pokemon.doryoku.set_values_from_stats(
                    get_default_doryoku(seikaku, pokemon.syuzoku)
                )
                self._app.set_active_pokemon(player, pokemon)
        if doryoku_text is not None:
            pokemon.doryoku.init_values(0)
            pokemon.doryoku.set_values_from_string(doryoku_text)
            self._app.set_active_pokemon(player, pokemon)
        if doryoku_number is not None:
            pokemon.doryoku.init_values(0)
            pokemon.doryoku.set_values_from_stats(doryoku_number)
            self._app.set_active_pokemon(player, pokemon)
        if kotai is not None:
            pokemon.kotai.set_values_from_stats(kotai)
            self._app.set_active_pokemon(player, pokemon)
        if rank is not None:
            pokemon.rank.set_values_from_stats(rank)
            self._app.set_active_pokemon(player, pokemon)
        if item is not None:
            if is_same and pokemon.item == item:
                pokemon.item = ""
            else:
                pokemon.item = item
        if ability is not None:
            if is_same and pokemon.ability == ability:
                pokemon.ability = ""
            else:
                pokemon.ability = ability
        if ability_value is not None:
            pokemon.ability_value = ability_value
        if wall is not None:
            pokemon.wall = wall
        if terastype is not None:
            if is_same and pokemon.battle_terastype == terastype:
                pokemon.battle_terastype = Types.なし
            else:
                pokemon.battle_terastype = terastype
        if waza is not None:
            pokemon.set_waza(waza_name=waza[1], index=waza[0])
            self._app.set_active_pokemon(player, pokemon)
        if waza_effect is not None:
            wazabase = pokemon.waza_list[waza_effect]
            self.set_waza_effect(player, wazabase)
        if ailment is not None:
            pokemon.ailment = ailment
            self._app.set_active_pokemon(player, pokemon)
        if critical is not None:
            for w in pokemon.waza_list:
                if w is not None:
                    w.critical = critical
        if charging is not None:
            pokemon.charging = charging
            self._app.set_active_pokemon(player, pokemon)

        self.calc_damage()

    # 天気の変更
    def change_weather(self, weather: str):
        for w in Weathers:
            if w.name == weather:
                self._weather = w
        self.calc_damage()

    # フィールドの変更
    def change_field(self, field: str):
        for f in Fields:
            if f.name == field:
                self._field = f
        self.calc_damage()

    # 戦闘時テラスタイプ変更
    def select_terastype(self, player: int):
        pokemon = self._active_pokemon[player]
        if pokemon.is_empty:
            return
        # テラスタイプの設定がある場合
        if pokemon.terastype != Types.なし:
            if pokemon.battle_terastype == Types.なし:
                pokemon.battle_terastype = pokemon.terastype
            else:
                pokemon.battle_terastype = Types.なし
        # テラスタイプの設定がない場合、ダイアログ表示で選択する
        else:
            types: Types = self._app.select_type(player=player)
            if types is None:
                return
            pokemon.battle_terastype = types
        # 表示の更新、ダメージ計算の再実行
        self._app.set_active_pokemon(player, pokemon)
        self.calc_damage()

    # 技追加効果の分岐処理
    def set_waza_effect(self, player: int, wazabase: WazaBase):
        non_player = 0 if player == 1 else 1
        if wazabase is not None:
            if wazabase.has_value_list:
                wazabase.set_next_value()
            if wazabase.is_self_buff or wazabase.is_self_debuff:
                self._active_pokemon[player].rank.add_ranks_from_string(
                    wazabase.value,
                    self._active_pokemon[player].ability == "あまのじゃく",
                )
            elif wazabase.is_opponent_buff or wazabase.is_opponent_debuff:
                self._active_pokemon[non_player].rank.add_ranks_from_string(
                    wazabase.value,
                    self._active_pokemon[player].ability == "あまのじゃく",
                )
            for i in range(2):
                self._app.set_active_pokemon(i, self._active_pokemon[i])

    # ダメージ計算
    def calc_damage(self):
        pokemon1 = self._active_pokemon[0]
        pokemon2 = self._active_pokemon[1]
        if pokemon1.is_empty or pokemon2.is_empty:
            return
        calc_result = DamageCalc.get_all_damages(
            pokemon1, pokemon2, self._weather, self._field
        )
        self._app.set_calc_results(0, calc_result)

        calc_result = DamageCalc.get_all_damages(
            pokemon2, pokemon1, self._weather, self._field
        )
        self._app.set_calc_results(1, calc_result)

    # パーティ編集
    def edit_party(self, player: int):
        party = self._app.edit_party(party=self._party[player])
        self._party[player] = party
        self._app.set_party(player=player, party=party)

    # パーティの読み込み
    def load_party(self, player: int, party: list[Pokemon] = []):
        from pokedata.loader import get_party_data

        if len(party) == 0:
            for i, data in enumerate(get_party_data()):
                pokemon: Pokemon = Pokemon.by_name(data[0])
                pokemon.set_load_data(data, True)
                party.append(pokemon)
        self._party[player] = party
        self._app.set_party(player=player, party=party)

    # パーティのクリア
    def clear_party(self, player: int):
        party = [Pokemon()] * 6
        self._party[player] = party
        self._app.set_party(player=player, party=party)

    # 選出の登録
    def set_chosen(self, player: int, index: list[int] = []):
        if len(index) == 0:
            index_list = [i for i, p in enumerate(self._chosen[player]) if p.is_empty]
            if (
                len(index_list) != 0
                and len(
                    list(
                        filter(
                            lambda p: p.name == self._active_pokemon[player].name,
                            self._chosen[player],
                        )
                    )
                )
                == 0
            ):
                self._app.set_chosen(
                    player, self._active_pokemon[player], index_list[0]
                )
                self._chosen[player][index_list[0]] = self._active_pokemon[player]
        else:
            for i in range(len(index)):
                pokemon = self._party[player][index[i]] if index[i] != -1 else Pokemon()
                self._app.set_chosen(player, pokemon, i)
                self._chosen[player][i] = pokemon

    # 選出の削除
    def delete_chosen(self, player: int, index: int):
        self._chosen[player][index] = Pokemon()
        self._app.set_chosen(player, Pokemon, index)

    # 選出のクリア
    def clear_chosen(self, player: int):
        for i in range(3):
            self.delete_chosen(player, i)

    # 自分一番手のポケモンを探す
    def search_first_chosen(self):
        if self._chosen[0][0].no != -1:
            for i, pokemon in enumerate(self._party[0]):
                if self._chosen[0][0].no == pokemon.no:
                    return i
        return -1

    # バトルの記録
    def record_battle(self):
        self._app.record_battle()

    # バトルのクリア
    def clear_battle(self):
        self._app.clear_battle()

    # 画像認識ループ制御
    def loop_image_recognize(self):
        self._app.image_recognize()

    # 選出の基本情報表示
    def set_info(self, player: int):
        if self._active_pokemon[player].form != -1:
            self._app.set_info(player, self._active_pokemon[player])

    @property
    def weather(self) -> Weathers:
        return self._weather

    @weather.setter
    def weather(self, value):
        self._weather = value

    @property
    def field(self) -> Fields:
        return self._field

    @field.setter
    def field(self, value):
        self._field = value

    def test(self):
        self._active_pokemon[0] = pokemon_1 = Pokemon.by_name(
            "サーフゴー", default=True
        )
        self._active_pokemon[1] = pokemon_2 = Pokemon.by_name(
            "セグレイブ", default=True
        )
        self._app.set_active_pokemon(0, pokemon_1)
        self._app.set_active_pokemon(1, pokemon_2)
        self.calc_damage()
