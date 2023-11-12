from tkinter import ttk, N, E, W, S
from ttkthemes.themed_tk import ThemedTk
from component.dialog import TypeSelectDialog, PartyInputDialog, RankSelectDialog
from component.frame import ActivePokemonFrame, ChosenFrame, WazaDamageListFrame, PartyFrame
from pokedata.const import Types
from pokedata.pokemon import Pokemon
from pokedata.stats import Stats


class MainApp(ThemedTk):

    def __init__(self, *args, **kwargs):
        super().__init__(theme="arc", *args, **kwargs)
        self.title('SV Tool')

        self._party_frames: list[PartyFrame] = []
        self._chosen_frames: list[ChosenFrame] = []
        self._active_poke_frames: list[ActivePokemonFrame] = []
        self._waza_damage_frames: list[WazaDamageListFrame] = []

        # メインフレーム
        main_frame = ttk.Frame(self, padding=10)
        main_frame.grid(row=0, column=0, sticky=N+E+W+S)

        # テスト用ボタン
        # button = MyButton(
        #     main_frame, size=(60, 10), text="TEST", command=self.test)
        # button.grid(row=0, column=0, columnspan=2)

        for i, side in enumerate(["自分側", "相手側"]):
            # パーティ表示フレーム
            chosen_frame = PartyFrame(
                master=main_frame,
                player=i,
                width=350,
                height=60,
                text=side + "パーティ")
            chosen_frame.grid(row=1, column=i*2, sticky=N+E+W+S)
            chosen_frame.grid_propagate(False)
            self._party_frames.append(chosen_frame)
            
            # 選出表示フレーム
            chosen_frame = ChosenFrame(
                master=main_frame,
                player=i,
                width=180,
                height=60,
                text=side + "選出")
            chosen_frame.grid(row=1, column=i*2+1, sticky=N+E+W+S)
            chosen_frame.grid_propagate(False)
            self._chosen_frames.append(chosen_frame)

            # 選択ポケモン表示フレーム
            poke_frame = ActivePokemonFrame(
                master=main_frame,
                player=i,
                width=350,
                height=150,
                text=side + "ポケモン")
            poke_frame.grid(row=2, column=i*2, columnspan=2, sticky=N+E+W+S)
            poke_frame.grid_propagate(False)
            self._active_poke_frames.append(poke_frame)

            # 技・ダメージ表示フレーム
            waza_frame = WazaDamageListFrame(
                master=main_frame,
                index=i,
                width=350,
                height=300,
                text=side + "わざ情報")
            waza_frame.grid(row=3, column=i*2, columnspan=2, sticky=N+E+W+S)
            waza_frame.grid_propagate(False)
            self._waza_damage_frames.append(waza_frame)

        # グリッド間ウェイト
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        self.columnconfigure(0, weight=True)
        self.rowconfigure(0, weight=True)

        self._stage = None

    def set_stage(self, stage):
        self._stage = stage
        for i in range(2):
            self._party_frames[i].set_stage(stage)
            self._chosen_frames[i].set_stage(stage)
            self._active_poke_frames[i].set_stage(stage)
            self._waza_damage_frames[i].set_stage(stage)

    def set_party(self, player: int, party: list[Pokemon]):
        self._party_frames[player].set_party(party)
    
    def set_chosen(self, player: int, pokemon: Pokemon, index: int):
        self._chosen_frames[player].set_chosen(pokemon, index)

    def set_active_pokemon(self, player: int, pokemon):
        self._active_poke_frames[player].set_pokemon(pokemon)
        self._waza_damage_frames[player].set_waza_info(pokemon.waza_list)

    def set_calc_results(self, player: int, results):
        self._waza_damage_frames[player].set_damages(results)

    def test(self, *_args):
        self.edit_rank(0, Stats(2))

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
