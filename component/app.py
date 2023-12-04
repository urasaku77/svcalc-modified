import dataclasses
import tkinter
from tkinter import ttk, N, E, W, S, LEFT, Menu
from ttkthemes.themed_tk import ThemedTk
from battle.DB_battle import DB_battle
from battle.battle import Battle
from component.button import MyButton
from component.combobox import MyCombobox
from component.const import FIELD_COMBOBOX_VALUES, WEATHER_COMBOBOX_VALUES
from component.dialog import CaputureSetting, SpeedComparing, TypeSelectDialog, PartyInputDialog, RankSelectDialog
from component.frame import ActivePokemonFrame, ChosenFrame, CountersFrame, HomeFrame, InfoFrame, RecordFrame, TimerFrame, WazaDamageListFrame, PartyFrame
from pokedata.const import Types
from pokedata.pokemon import Pokemon
from pokedata.stats import Stats


class MainApp(ThemedTk):

    def __init__(self, *args, **kwargs):
        super().__init__(theme="arc", *args, **kwargs)
        self.title('SV Tool')
        self.iconbitmap(default='image/favicon.ico')

        self._party_frames: list[PartyFrame] = []
        self._chosen_frames: list[ChosenFrame] = []
        self._info_frames: list[InfoFrame] = []
        self._active_poke_frames: list[ActivePokemonFrame] = []
        self._waza_damage_frames: list[WazaDamageListFrame] = []

        # メインフレーム
        main_frame = ttk.Frame(self, padding=10)
        main_frame.grid(row=0, column=0, sticky=N+E+W+S)

        # テスト用ボタン
        # button = MyButton(
        #     main_frame, size=(60, 10), text="TEST", command=self.test)
        # button.grid(row=0, column=0, columnspan=2)

        menu = tkinter.Menu(self) 
        self.config(menu=menu) 
        menu.add_cascade(label='キャプチャ設定', command=self.capture_setting) 
        menu.add_cascade(label='モード切替') 

        for i, side in enumerate(["自分側", "相手側"]):
            # パーティ表示フレーム
            party_frame = PartyFrame(
                master=main_frame,
                player=i,
                width=350,
                height=60,
                text=side + "パーティ")
            party_frame.grid(row=1, column=i*3, columnspan=2, sticky=N+E+W+S)
            party_frame.grid_propagate(False)
            self._party_frames.append(party_frame)
            
            # 選出表示フレーム
            chosen_frame = ChosenFrame(
                master=main_frame,
                player=i,
                width=180,
                height=60,
                text=side + "選出")
            chosen_frame.grid(row=1, column=i*3+2, sticky=N+E+W+S)
            chosen_frame.grid_propagate(False)
            self._chosen_frames.append(chosen_frame)
            
            # 選択ポケモン基本情報表示フレーム
            info_frame = InfoFrame(
                master=main_frame,
                player=i,
                width=530,
                height=100,
                text=side + "基本情報")
            info_frame.grid(row=2, column=i*3, columnspan=3, sticky=N+E+W+S)
            info_frame.grid_propagate(False)
            self._info_frames.append(info_frame)

            # 選択ポケモン表示フレーム
            poke_frame = ActivePokemonFrame(
                master=main_frame,
                player=i,
                width=530,
                height=150,
                text=side + "ポケモン")
            poke_frame.grid(row=3, column=i*3, columnspan=3, sticky=N+E+W+S)
            poke_frame.grid_propagate(False)
            self._active_poke_frames.append(poke_frame)

        # 技・ダメージ表示フレーム
        waza_frame_my = WazaDamageListFrame(
            master=main_frame,
            index=0,
            width=530,
            height=100,
            text="自分わざ情報")
        waza_frame_my.grid(row=4, column=0, columnspan=3, sticky=N+E+W+S)
        waza_frame_my.grid_propagate(False)
        self._waza_damage_frames.append(waza_frame_my)

        # 技・ダメージ表示フレーム
        waza_frame_your = WazaDamageListFrame(
            master=main_frame,
            index=1,
            width=530,
            height=320,
            text="相手わざ情報")
        waza_frame_your.grid(row=4, column=3, rowspan=2, columnspan=3, sticky=N+E+W+S)
        waza_frame_your.grid_propagate(False)
        self._waza_damage_frames.append(waza_frame_your)

        # HOME情報フレーム
        self.home_frame = HomeFrame(
            master=main_frame,
            width=530,
            text="HOME情報")
        self.home_frame.grid(row=6, column=3, rowspan=4, columnspan=3, sticky=N+E+W+S)
        self.home_frame.grid_propagate(False)

        # ツールフレーム（タイマー・カウンター・共通）
        tool_frame = ttk.Frame(main_frame, padding=5)
        tool_frame.grid(row=5, column=0, rowspan=3, columnspan=3, sticky=N+E+W)
        
        # タイマーフレーム
        self.timer_frame = TimerFrame(
            master=tool_frame,
            text="タイマー")
        self.timer_frame.pack(fill = 'both', expand=0, side='left')

        # カウンターフレーム
        self.counter_frame = CountersFrame(
            master=tool_frame,
            text="カウンター")
        self.counter_frame.pack(fill = 'both', expand=0, side='left')

        # 共通フレーム（天気・フィールド）
        common_frame = ttk.Frame(tool_frame)
        common_frame.pack(fill = 'both', expand=0, side='left')
        
        # 天候フレーム
        self.weather_frame = ttk.LabelFrame(common_frame, text="天候", width=150, height=55, padding=6)
        self._weather_combobox = MyCombobox(self.weather_frame, width=17, height=30, values=WEATHER_COMBOBOX_VALUES)
        self._weather_combobox.bind("<<ComboboxSelected>>", self.change_weather)
        self._weather_combobox.pack()
        self.weather_frame.pack(fill = 'x', expand=0)

        # フィールドフレーム
        self.field_frame = ttk.LabelFrame(common_frame, text="フィールド", width=150, height=55, padding=6)
        self._field_combobox = MyCombobox(self.field_frame, width=17, height=30, values=FIELD_COMBOBOX_VALUES)
        self._field_combobox.bind("<<ComboboxSelected>>", self.change_field)
        self._field_combobox.pack()
        self.field_frame.pack(fill = 'x', expand=0)
        
        # 素早さ比較ボタン
        self.speed_button = MyButton(common_frame, text="素早さ比較", width=6, padding=5, command=self.speed_comparing)
        self.speed_button.pack(fill = 'both', expand=0)

        # 対戦記録フレーム
        self.record_frame = RecordFrame(
            master=main_frame,
            width=530,
            height=220,
            text="対戦記録"
        )
        self.record_frame.grid(row=8, column=0, rowspan=2, columnspan=3, sticky=N+E+W+S)
        self.record_frame.grid_propagate(False)

        # グリッド間ウェイト
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.columnconfigure(3, weight=1)
        main_frame.columnconfigure(4, weight=1)
        main_frame.columnconfigure(5, weight=1)

        self.columnconfigure(0, weight=True)
        self.rowconfigure(0, weight=True)

        self._stage = None

    # 各フレームにStageクラスを配置
    def set_stage(self, stage):
        self._stage = stage
        self.home_frame.set_stage(stage)
        for i in range(2):
            self._party_frames[i].set_stage(stage)
            self._chosen_frames[i].set_stage(stage)
            self._active_poke_frames[i].set_stage(stage)
            self._waza_damage_frames[i].set_stage(stage)
            self.record_frame.set_stage(stage)

    # パーティセット
    def set_party(self, player: int, party: list[Pokemon]):
        self._party_frames[player].set_party(party)
    
    # 選出登録
    def set_chosen(self, player: int, pokemon: Pokemon, index: int):
        self._chosen_frames[player].set_chosen(pokemon, index)

    # 選出基本情報表示
    def set_info(self, player: int, pokemon: Pokemon):
        self._info_frames[player].set_info(pokemon)

    # ポケモン選択
    def set_active_pokemon(self, player: int, pokemon: Pokemon):
        self._active_poke_frames[player].set_pokemon(pokemon)
        self._waza_damage_frames[player].set_waza_info(pokemon.waza_list)
        if player == 1:
            self._waza_damage_frames[player].set_waza_rate(pokemon.waza_rate_list)
            self.home_frame.set_home_data(pokemon.name)

    # ダメージ計算
    def set_calc_results(self, player: int, results):
        self._waza_damage_frames[player].set_damages(results)

    def test(self, *_args):
        self.edit_rank(0, Stats(2))
    
    # 天気変更
    def change_weather(self, *args):
        self._stage.change_weather(self._weather_combobox.get())

    # フィールド変更
    def change_field(self, *args):
        self._stage.change_field(self._field_combobox.get())

    # ランク変更
    def edit_rank(self, player: int, rank: Stats) -> Stats:
        loc_x = self.winfo_x() + self._waza_damage_frames[player].winfo_x()
        loc_y = self.winfo_y() + self._waza_damage_frames[player].winfo_y()
        dialog = RankSelectDialog()
        dialog.set_rank(rank)
        dialog.open(location=(loc_x, loc_y))
        self.wait_window(dialog)
        return dialog.rank

    # タイプ選択
    def select_type(self, player: int) -> Types:
        dialog = TypeSelectDialog()
        dialog.open(location=(self.winfo_x(), self.winfo_y()))
        self.wait_window(dialog)
        return dialog.selected_type

    # パーティ編集
    def edit_party(self, party) -> list[Pokemon]:
        dialog = PartyInputDialog()
        dialog.party = party
        dialog.open(location=(self.winfo_x(), self.winfo_y()))
        self.wait_window(dialog)
        return dialog.party
    
    # 素早さ比較画面
    def speed_comparing(self):
        pokemons: list[Pokemon] = self._stage.get_active_pokemons()
        if pokemons[0].no != -1 and pokemons[1].no != -1:
            dialog = SpeedComparing()
            dialog.set_pokemon(pokemons)
            dialog.open(location=(self.winfo_x(), self.winfo_y()))
            self.wait_window(dialog)

    # 対戦登録
    def record_battle(self):
        battle = Battle.set_battle(self.record_frame, self._party_frames, self._chosen_frames)
        battle_data = dataclasses.astuple(battle)
        DB_battle.register_battle(battle_data)

    # 対戦記録情報クリア
    def clear_battle(self):
        self._party_frames[1].on_push_clear_button()
        self._chosen_frames[0].on_push_clear_button()
        self._chosen_frames[1].on_push_clear_button()
        self.timer_frame.reset_button_clicked()
        self.counter_frame.clear_all_counters()

    # キャプチャ設定画面
    def capture_setting(self):
        dialog = CaputureSetting()
        dialog.open(location=(self.winfo_x(), self.winfo_y()))
        self.wait_window(dialog)