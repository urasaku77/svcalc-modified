import copy
import dataclasses
import sys
import tkinter
from tkinter import E, N, S, W, messagebox, ttk

from ttkthemes.themed_tk import ThemedTk

from component.frames.common import (
    ActivePokemonFrame,
    ChosenFrame,
    InfoFrame,
    PartyFrame,
    WazaDamageListFrame,
)
from component.frames.whole import (
    CompareButton,
    CountersFrame,
    DoubleFrame,
    FieldFrame,
    HomeFrame,
    RecordFrame,
    TimerFrame,
    WeatherFrame,
)
from component.parts.button import MyButton
from component.parts.dialog import (
    BoxDialog,
    FormSelect,
    PartyInputDialog,
    SimilarParty,
    SpeedComparing,
    TypeSelectDialog,
    WeightComparing,
)
from database.battle import Battle, DB_battle
from mypgl import analytics, record
from party.party import PartyEditor
from pokedata.const import Types
from pokedata.pokemon import Pokemon
from pokedata.stats import StatsKey
from recog.capture import Capture
from recog.recog import CaptureSetting, ModeSetting, get_recog_value
from stats.search import get_similar_party


class MainApp(ThemedTk):
    def __init__(self, **kwargs):
        super().__init__(theme="arc", **kwargs)
        self.title("SV Auto Damage Calculator")
        if sys.platform == "win32":
            self.iconbitmap(default="image/favicon.ico")
        self.geometry("950x915")

        self.capture = Capture()
        self.websocket = False
        self.monitor = False

        self.party_frames: list[PartyFrame] = []
        self.chosen_frames: list[ChosenFrame] = []
        self._info_frames: list[InfoFrame] = []
        self.active_poke_frames: list[ActivePokemonFrame] = []
        self._waza_damage_frames: list[WazaDamageListFrame] = []

        # メインフレーム
        main_frame = tkinter.Frame(self, bg="gray97")
        self.bind("<Configure>", self.on_change_transport)
        main_frame.grid(row=0, column=0, sticky=N + E + W + S)

        menu = tkinter.Menu(self)
        self.config(menu=menu)
        menu.add_cascade(label="キャプチャ設定", command=self.capture_setting)
        menu.add_cascade(label="モード切替", command=self.mode_setting)
        menu.add_cascade(label="パーティ編集", command=self.edit_party_csv)
        menu.add_cascade(label="ボックス編集", command=self.open_box)
        menu.add_cascade(label="対戦履歴", command=self.open_records)
        menu.add_cascade(label="対戦分析", command=self.open_analytics)

        for i, side in enumerate(["自分側", "相手側"]):
            sticky = N + W + S if side == "自分側" else N + E + S
            # パーティ＆選出フレーム
            top_frame = ttk.Frame(master=main_frame, width=500, height=60, padding=5)
            top_frame.grid(row=0, column=i * 3, rowspan=2, columnspan=3, sticky=sticky)
            top_frame.grid_propagate(False)
            # パーティ表示フレーム
            party_frame = PartyFrame(
                master=top_frame,
                player=i,
                width=350,
                height=60,
                text=side + "パーティ",
            )
            party_frame.pack(fill="both", expand=0, side="left")
            self.party_frames.append(party_frame)

            # 選出表示フレーム
            chosen_frame = ChosenFrame(
                master=top_frame, player=i, width=180, height=60, text=side + "選出"
            )
            chosen_frame.pack(fill="both", expand=0, side="left")
            self.chosen_frames.append(chosen_frame)

            # 選択ポケモン基本情報表示フレーム
            info_frame = InfoFrame(
                master=main_frame,
                player=i,
                width=475,
                height=80,
                text=side + "基本情報",
            )
            info_frame.grid(row=2, column=i * 3, columnspan=3, sticky=sticky)
            info_frame.grid_propagate(False)
            self._info_frames.append(info_frame)

            # 選択ポケモン表示フレーム
            poke_frame = ActivePokemonFrame(
                master=main_frame,
                player=i,
                width=475,
                height=213,
                text=side + "ポケモン",
            )
            poke_frame.grid(row=3, column=i * 3, columnspan=3, sticky=sticky)
            poke_frame.grid_propagate(False)
            self.active_poke_frames.append(poke_frame)

        # 技・ダメージ表示フレーム(自分)
        waza_frame_my = WazaDamageListFrame(
            master=main_frame, index=0, width=475, height=60, text="自分わざ情報"
        )
        waza_frame_my.grid(row=4, column=0, columnspan=3, sticky=N + W + S)
        waza_frame_my.grid_propagate(False)
        self._waza_damage_frames.append(waza_frame_my)

        # 技・ダメージ表示フレーム(相手)
        waza_frame_your = WazaDamageListFrame(
            master=main_frame, index=1, width=475, height=313, text="相手わざ情報"
        )
        waza_frame_your.grid(row=4, column=3, rowspan=2, columnspan=3, sticky=N + E + S)
        waza_frame_your.grid_propagate(False)
        self._waza_damage_frames.append(waza_frame_your)

        # HOME情報フレーム
        self.home_frame = HomeFrame(
            master=main_frame, width=475, height=258, text="HOME情報"
        )
        self.home_frame.grid(row=6, column=3, rowspan=4, columnspan=3, sticky=N + E + S)
        self.home_frame.grid_propagate(False)

        # ツールフレーム（タイマー・カウンター・ダブル・共通）
        tool_frame = ttk.Frame(main_frame, padding=4)
        tool_frame.grid(row=5, column=0, rowspan=3, sticky=N + W + S)
        tool_frame.grid_propagate(False)

        # タイマーフレーム
        self.timer_frame = TimerFrame(master=tool_frame, text="タイマー")
        self.timer_frame.pack(fill="both", expand=0, side="left")

        # カウンターフレーム
        self.counter_frame = CountersFrame(
            master=tool_frame,
            num=2 if get_recog_value("rule") == 1 else 1,
            text="カウンター",
        )
        self.counter_frame.pack(fill="both", expand=0, side="left")

        if get_recog_value("rule") == 2:
            # ダブルフレーム
            self.double_frame = DoubleFrame(tool_frame)
            self.double_frame.pack(fill="both", expand=0, side="left")

        # 共通フレーム（天気・フィールド）
        common_frame = ttk.Frame(tool_frame)
        common_frame.pack(fill="both", expand=0, side="left")

        # 天候フレーム
        self.weather_frame = WeatherFrame(master=common_frame, text="天候", padding=6)
        self.weather_frame.pack(fill="x", expand=0)

        # フィールドフレーム
        self.field_frame = FieldFrame(master=common_frame, text="フィールド", padding=6)
        self.field_frame.pack(fill="x", expand=0)

        # 比較ボタンフレーム（素早さ・重さ）
        compare_frame = ttk.Frame(common_frame)
        compare_frame.pack(fill="both", expand=0)

        # 素早さ比較ボタン
        self.speed_button = CompareButton(
            master=compare_frame,
            text="S比較",
            width=6,
            padding=5,
            command=self.speed_comparing,
        )
        self.speed_button.pack(fill="both", expand=0, side="left")

        # 重さ比較ボタン
        self.weight_button = CompareButton(
            master=compare_frame,
            text="重さ比較",
            width=8,
            padding=5,
            command=self.weight_comparing,
        )
        self.weight_button.pack(fill="both", expand=0, side="left")

        # 対戦記録フレーム
        self.record_frame = RecordFrame(
            master=main_frame, width=474, height=157, text="対戦記録"
        )
        self.record_frame.grid(row=8, column=0, columnspan=3, sticky=N + W + S)
        self.record_frame.grid_propagate(False)

        # 最終メニューフレーム
        last_menu_frame = ttk.Frame(master=main_frame, padding=4)
        last_menu_frame.grid(row=9, column=0, columnspan=3, sticky=N + W)

        # 制御フレーム
        control_frame = ttk.LabelFrame(master=last_menu_frame, text="制御", padding=5)
        control_frame.pack(fill="both", expand=0, side="left")

        # Websocket接続ボタン
        self.websocket_var = tkinter.StringVar()
        self.websocket_var.set("Websocket接続")

        self.websocket_button = MyButton(
            control_frame,
            textvariable=self.websocket_var,
            command=self.connect_websocket,
        )
        self.websocket_button.pack(fill="both", expand=0, side="left")

        # キャプチャ監視ボタン
        self.monitor_var = tkinter.StringVar()
        self.monitor_var.set("監視開始")
        self.monitor_button = MyButton(
            control_frame,
            textvariable=self.monitor_var,
            command=self.image_recognize,
            state=tkinter.DISABLED,
        )
        self.monitor_button.pack(fill="both", expand=0, side="left")

        # 手動キャプチャボタン
        self.shot_button = MyButton(
            control_frame,
            text="選出取得",
            command=self.manual_capture,
            state=tkinter.DISABLED,
        )
        self.shot_button.pack(fill="both", expand=0, side="left")

        # 検索フレーム
        search_frame = ttk.LabelFrame(
            master=last_menu_frame, text="類似パーティ", padding=5
        )
        search_frame.pack(fill="both", expand=0, side="left")

        # 類似パーティ検索ボタン
        self.search_button = MyButton(
            search_frame,
            text="構築記事",
            command=self.search_similar_party,
        )
        self.search_button.pack(fill="both", expand=0, side="left")

        # 対戦履歴から検索ボタン
        self.search_button = MyButton(
            search_frame,
            text="対戦履歴",
            command=self.search_record,
        )
        self.search_button.pack(fill="both", expand=0, side="left")

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
            self.party_frames[i].set_stage(stage)
            self.chosen_frames[i].set_stage(stage)
            self.active_poke_frames[i].set_stage(stage)
            self.active_poke_frames[i]._status_frame.set_stage(stage)
            self._waza_damage_frames[i].set_stage(stage)
            self.weather_frame.set_stage(stage)
            self.field_frame.set_stage(stage)
            self.speed_button.set_stage(stage)
            self.weight_button.set_stage(stage)
            self.record_frame.set_stage(stage)
        if get_recog_value("rule") == 2:
            self.double_frame.set_stage(stage)

    # パーティCSV編集
    def edit_party_csv(self):
        dialog = PartyEditor()
        dialog.open(location=(self.winfo_x(), self.winfo_y()))
        self.withdraw()
        self.wait_window(dialog)
        return self.deiconify()

    # パーティセット
    def set_party(self, player: int, party: list[Pokemon]):
        self.party_frames[player].set_party(party)

    # 選出登録
    def set_chosen(self, player: int, pokemon: Pokemon, index: int):
        self.chosen_frames[player].set_chosen(pokemon, index)

    # 選出基本情報表示
    def set_info(self, player: int, pokemon: Pokemon):
        self._info_frames[player].set_info(pokemon)

    # ポケモン選択
    def set_active_pokemon(self, player: int, pokemon: Pokemon):
        change_flag = self.active_poke_frames[player]._pokemon.no == pokemon.no
        self.active_poke_frames[player].set_pokemon(pokemon)
        self._waza_damage_frames[player].set_waza_info(pokemon.waza_list)
        if player == 1:
            self._waza_damage_frames[player].set_waza_rate(pokemon.waza_rate_list)
            if not change_flag:
                self.home_frame.set_home_data(pokemon.name)

    def after_appear(self, pokemon: Pokemon, player: int):
        if pokemon.name in ["カバルドン", "バンギラス"]:
            self.weather_frame.change_weather_from_ability("砂嵐")
        elif pokemon.name in ["コライドン", "グラードン", "コータス", "キュウコン"]:
            self.weather_frame.change_weather_from_ability("晴れ")
        elif pokemon.name in ["カイオーガ", "ペリッパー", "ニョロトノ"]:
            self.weather_frame.change_weather_from_ability("雨")
        elif pokemon.name in ["アローラキュウコン", "ユキノオー"]:
            self.weather_frame.change_weather_from_ability("雪")
        elif pokemon.name in ["ミライドン", "バチンウニ"]:
            self.field_frame.change_field_from_ability("エレキ")
        elif pokemon.name in ["ゴリランダー", "バチンキー"]:
            self.field_frame.change_field_from_ability("グラス")
        elif pokemon.name in ["ミライドン", "バチンウニ"]:
            self.field_frame.change_field_from_ability("エレキ")
        elif pokemon.name in ["イエッサン♂", "イエッサン♀"]:
            self.field_frame.change_field_from_ability("サイコ")
        elif pokemon.name == "メタモン":
            after_ditto = (
                copy.deepcopy(self.active_poke_frames[1]._pokemon)
                if player == 0
                else copy.deepcopy(self.active_poke_frames[0]._pokemon)
            )
            after_ditto.syuzoku.__setitem__(StatsKey.H, 48)
            after_ditto.doryoku.__setitem__(StatsKey.H, 252)
            self.active_poke_frames[player].set_pokemon(after_ditto)
            if player == 1:
                self._waza_damage_frames[player].set_waza_info(
                    self.active_poke_frames[0]._pokemon.waza_list
                )

    # ダメージ計算
    def set_calc_results(self, player: int, results):
        self._waza_damage_frames[player].set_damages(results)

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

    # 素早さ比較
    def speed_comparing(self):
        pokemons = self.speed_button.get_active_pokemons()
        if pokemons[0].no != -1 and pokemons[1].no != -1:
            dialog = SpeedComparing()
            dialog.set_pokemon(pokemons)
            dialog.open(location=(self.winfo_x(), self.winfo_y()))
            self.wait_window(dialog)

    # 重さ比較
    def weight_comparing(self):
        pokemons = self.weight_button.get_active_pokemons()
        if pokemons[0].no != -1 and pokemons[1].no != -1:
            dialog = WeightComparing()
            dialog.set_pokemon(pokemons)
            dialog.open(location=(self.winfo_x(), self.winfo_y()))
            self.wait_window(dialog)

    # 対戦登録
    def record_battle(self):
        battle = Battle.set_battle(
            self.record_frame, self.party_frames, self.chosen_frames
        )
        battle_data = dataclasses.astuple(battle)
        DB_battle.register_battle(battle_data)
        self.record_frame.clear()
        ret = messagebox.askyesno(
            "確認",
            "データを登録しました\n次の対戦へ移りますか？）",
        )
        if ret is False:
            return
        self.image_recognize()

    # 対戦記録情報クリア
    def clear_battle(self):
        self.party_frames[1].on_push_clear_button()
        self.chosen_frames[0].on_push_clear_button()
        self.chosen_frames[1].on_push_clear_button()
        self.timer_frame.reset_button_clicked()
        self.counter_frame.clear_all_counters()
        self.weather_frame.reset_weather()
        self.field_frame.reset_field()

    # キャプチャ設定画面
    def capture_setting(self):
        dialog = CaptureSetting()
        dialog.open(location=(self.winfo_x(), self.winfo_y()))
        self.wait_window(dialog)

    # モード切替画面
    def mode_setting(self):
        dialog = ModeSetting()
        dialog.open(location=(self.winfo_x(), self.winfo_y()))
        self.wait_window(dialog)

    # Websocket処理
    def connect_websocket(self):
        if not self.websocket:
            value = self.capture.connect_websocket()
            if value:
                self.websocket_var.set("Websocket切断")
                self.monitor_button["state"] = tkinter.NORMAL
                self.shot_button["state"] = tkinter.NORMAL
                self.websocket = True

                if get_recog_value("capture_monitor_auto"):
                    self.image_recognize()

        else:
            value = self.capture.disconnect_websocket()
            if value:
                self.websocket_var.set("Websocket接続")
                self.monitor_button["state"] = tkinter.DISABLED
                self.shot_button["state"] = tkinter.DISABLED
                self.websocket = False

    # 画像認識処理
    def image_recognize(self):
        if self.monitor:
            self.stop_image_recognize()
        else:
            self.party_frames[0].on_push_load_button()
            self.after(2000, self.loop_image_recognize)

    # 画像認識ループ開始
    def loop_image_recognize(self):
        global after_id
        result = self.capture.image_recognize()
        match result:
            case tuple():
                self.party_frames[1].set_party_from_capture(result[0])
                self.record_frame.tn.insert(0, result[1])

                if get_recog_value("similar_party_auto"):
                    self.search_similar_party(isOpen=False)
                if get_recog_value("search_record_auto"):
                    self.search_record(isOpen=False)
            case list():
                if result != [-1, -1, -1]:
                    self.chosen_frames[0].set_chosen_from_capture(result)
            case bool():
                if result:
                    # タイマーをリセットしてスタート
                    self.timer_frame.reset_button_clicked()
                    self.timer_frame.start_button_clicked()
                    # 選出一体目を自動登録
                    self.party_frames[0].set_first_chosen_to_active()
                    self.stop_image_recognize()
                    return
            case int():
                if result != -1:
                    self.record_frame.rank.insert(0, result)
            case _:
                pass
        after_id = self.after(1000, self.loop_image_recognize)
        self.monitor = True
        self.monitor_var.set("監視停止")
        self.websocket_button["state"] = tkinter.DISABLED
        self.shot_button["state"] = tkinter.DISABLED

    # 画像認識ループ停止
    def stop_image_recognize(self):
        if self.monitor:
            self.after_cancel(after_id)
            self.monitor = False
            self.monitor_var.set("監視開始")
            self.websocket_button["state"] = tkinter.NORMAL
            self.shot_button["state"] = tkinter.NORMAL

    # 手動キャプチャ
    def manual_capture(self):
        result = self.capture.recognize_chosen_capture()
        if result is not None:
            self.party_frames[1].set_party_from_capture(result[0])
            self.record_frame.tn.insert(0, result[1])

    # 類似パーティ検索
    def search_similar_party(self, isOpen: bool = True):
        current_party = [pokemon.pid for pokemon in self.party_frames[1].pokemon_list]
        party_list = get_similar_party(self.party_frames[1].pokemon_list)
        if isOpen or party_list:
            dialog = SimilarParty(current_party=current_party, party_list=party_list)
            dialog.open(location=(self.winfo_x(), self.winfo_y()))

    # 対戦履歴から検索
    def search_record(self, isOpen: bool = True):
        current_party = [pokemon.pid for pokemon in self.party_frames[1].pokemon_list]
        dialog = record.ListRecord()
        if (
            isOpen
            or len(dialog.full_frame.get_battle_data(current_party)) > 0
            or len(dialog.part_frame.get_battle_data(current_party)) > 0
        ):
            dialog.full_frame.get_battle_data(current_party)
            dialog.part_frame.get_battle_data(current_party)
            dialog.open()

    # フォーム選択画面
    def form_select(self, no: int):
        dialog = FormSelect()
        dialog.set_pokemon(no)
        dialog.open(location=(self.winfo_x(), self.winfo_y()))
        self.wait_window(dialog)
        return dialog.form_num

    # 個体管理画面
    def open_box(self):
        dialog = BoxDialog()
        dialog.open(location=(self.winfo_x(), self.winfo_y()))

    # 対戦履歴画面
    def open_records(self):
        dialog = record.Record()
        dialog.open()

    # 対戦分析画面
    def open_analytics(self):
        dialog = analytics.Analytics()
        dialog.open()

    def on_change_transport(self, event):
        # ウィンドウが最大化されたかどうかをチェック
        if self.winfo_width() >= 1200:
            self.attributes("-transparentcolor", "gray97")
        else:
            self.attributes("-transparentcolor", "")
