import json
import tkinter
import webbrowser
from tkinter import E, N, S, W, ttk
from tkinter.font import Font

from component import images
from component.button import MyButton, TypeButton
from component.combobox import AutoCompleteCombobox, ModifiedEntry
from component.label import MyLabel
from data.db import DB
from pokedata.const import Types
from pokedata.pokemon import Pokemon


# パーティ入力ダイアログ
class PartyInputDialog(tkinter.Toplevel):
    def __init__(self, title: str = "", width: int = 400, height: int = 300):
        super().__init__()
        self.title("パーティ入力")

        self._selected = tkinter.IntVar()
        self._radio_buttons = []
        self._labels = []
        _blank = Pokemon()
        self._party: list[Pokemon] = [_blank, _blank, _blank, _blank, _blank, _blank]

        # ウィジェットの配置
        main_frame = ttk.Frame(self, padding=10)
        main_frame.grid(row=0, column=0, sticky=N + E + W + S)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._labelframe = ttk.LabelFrame(main_frame, text="ポケモン名を入力")
        self._labelframe.grid(row=0, column=0, columnspan=6)

        self._name_input: AutoCompleteCombobox = AutoCompleteCombobox.pokemons(
            self._labelframe
        )
        self._name_input.bind("<<submit>>", self.on_input_name)
        self._name_input.grid(row=0, column=0)

        for i in range(6):
            radio = ttk.Radiobutton(
                main_frame,
                value=i,
                variable=self._selected,
                command=self.on_push_radiobutton,
            )
            radio.grid(row=1, column=i)
            self._radio_buttons.append(radio)

            label = MyLabel(main_frame, size=(40, 40), relief=tkinter.RAISED, padding=0)
            label.grid(row=2, column=i)
            self._labels.append(label)

        self._close_button = ttk.Button(
            main_frame, text="決定", command=lambda: self.destroy()
        )
        self._close_button.bind("<Return>", lambda _: self.destroy())
        self._close_button.grid(row=3, column=0, columnspan=6)

    @property
    def party(self) -> list[Pokemon]:
        return self._party

    @party.setter
    def party(self, value: list[Pokemon]):
        self._party = value
        for i in range(6):
            if value[i].is_empty is False:
                self.set_pokemon_icon(pid=value[i].pid, index=i)

    @property
    def selected_index(self) -> int:
        return self._selected.get()

    def open(self, location=tuple[int, int]):
        self.grab_set()
        self.select(0)
        self._name_input.focus_set()
        self.geometry("+{0}+{1}".format(location[0], location[1]))

    def select(self, index: int):
        pokemon = self._party[index]
        if pokemon.is_empty:
            self._name_input.set("")
        else:
            self._name_input.set(pokemon.name)

    def set_pokemon_icon(self, pid: str, index: int):
        self._labels[index].set_image(images.get_pokemon_icon(pid=pid, size=(40, 40)))

    def on_input_name(self, *args):
        pokemon_name = self._name_input.get()
        pokemon: Pokemon = Pokemon.by_name(pokemon_name, default=True)
        index: int = self.selected_index

        self._party[index] = pokemon
        self.set_pokemon_icon(pid=pokemon.pid, index=index)

        if index < 5:
            self._selected.set(index + 1)
            self.select(index + 1)
        else:
            self._close_button.focus_set()

    def on_push_radiobutton(self, *args):
        self.select(self.selected_index)


# タイプ指定ダイアログ
class TypeSelectDialog(tkinter.Toplevel):
    def __init__(self, title: str = "タイプ選択", width: int = 400, height: int = 300):
        super().__init__()
        self.title(title)
        self._selected_type = None

        for idx, t in enumerate(Types):
            button = TypeButton(
                self, type_=t, command=lambda x=t: self.on_push_button(x)
            )
            button.grid(column=(idx % 4), row=(idx // 4), sticky=E + W)

    @property
    def selected_type(self):
        return self._selected_type

    def open(self, location=tuple[int, int]):
        self.grab_set()
        self.focus_set()
        self.geometry("+{0}+{1}".format(location[0], location[1]))

    def on_push_button(self, t: Types):
        self._selected_type = t
        self.destroy()


# 素早さ比較画面
class SpeedComparing(tkinter.Toplevel):
    def on_validate_2(self, P, V):
        if P.isdigit() or P == "":
            return len(P) <= 2
        else:
            return False

    def on_validate_3(self, P, V):
        if P.isdigit() or P == "":
            return len(P) <= 3
        else:
            return False

    def __init__(self, title: str = "素早さ比較", width: int = 600, height: int = 500):
        super().__init__()
        self.title(title)
        self.pokemons: list[Pokemon] = [Pokemon(), Pokemon()]
        self.tailwind = [1.0, 1.0]
        self.paralysis = [1.0, 1.0]

        self.name_var: list[tkinter.StringVar] = [
            tkinter.StringVar(),
            tkinter.StringVar(),
        ]
        self.compare_mark: tkinter.StringVar = tkinter.StringVar()
        self.speed_var: list[tkinter.StringVar] = [
            tkinter.StringVar(),
            tkinter.StringVar(),
        ]
        self.base_stat_var: list[tkinter.IntVar] = [tkinter.IntVar(), tkinter.IntVar()]
        self.nature_var: list[tkinter.StringVar] = [
            tkinter.StringVar(value="1.0"),
            tkinter.StringVar(value="1.0"),
        ]
        self.rank_var: list[tkinter.IntVar] = [
            tkinter.IntVar(value=0),
            tkinter.IntVar(value=0),
        ]
        self.ability_var: list[tkinter.StringVar] = [
            tkinter.StringVar(value="1.0"),
            tkinter.StringVar(value="1.0"),
        ]
        self.item_var: list[tkinter.StringVar] = [
            tkinter.StringVar(value="1.0"),
            tkinter.StringVar(value="1.0"),
        ]
        self.tailwind_var: list[tkinter.BooleanVar] = [
            tkinter.BooleanVar(value=False),
            tkinter.BooleanVar(value=False),
        ]
        self.paralysis_var: list[tkinter.BooleanVar] = [
            tkinter.BooleanVar(value=False),
            tkinter.BooleanVar(value=False),
        ]

        base_stat_label = tkinter.Label(self, text="種族値")
        base_stat_label.grid(row=3, column=1)
        iv_label = tkinter.Label(self, text="個体値")
        iv_label.grid(row=4, column=1)
        ev_label = tkinter.Label(self, text="努力値")
        ev_label.grid(row=5, column=1)
        nature_label = tkinter.Label(self, text="性格")
        nature_label.grid(row=6, column=1)
        rank_label = tkinter.Label(self, text="ランク")
        rank_label.grid(row=7, column=1)
        ability_label = tkinter.Label(self, text="特性")
        ability_label.grid(row=8, column=1)
        item_label = tkinter.Label(self, text="道具")
        item_label.grid(row=9, column=1)
        tailwind_label = tkinter.Label(self, text="おいかぜ")
        tailwind_label.grid(row=10, column=1)
        paralysis_label = tkinter.Label(self, text="まひ")
        paralysis_label.grid(row=11, column=1)

        self.validate_cmd_2 = self.register(self.on_validate_2)
        self.validate_cmd_3 = self.register(self.on_validate_3)

        self.pokemon_icon: list[MyLabel] = [MyLabel(self), MyLabel(self)]
        self.name_label = [
            tkinter.Label(self, textvariable=self.name_var[i]) for i in range(2)
        ]

        self.compare = tkinter.Label(
            self, textvariable=self.compare_mark, font=Font(weight="bold", size=16)
        )
        self.compare.grid(row=2, column=1, pady=5)
        self.speed_label = [
            tkinter.Label(
                self, textvariable=self.speed_var[i], font=Font(weight="bold", size=32)
            )
            for i in range(2)
        ]

        # 種族値
        self.base_stat = [
            tkinter.Label(self, textvariable=self.base_stat_var[i]) for i in range(2)
        ]

        # 個体値
        self.iv_box = [ttk.Frame(self, padding=10), ttk.Frame(self, padding=10)]
        self.iv_entry = [
            ModifiedEntry(
                self.iv_box[i],
                validate="key",
                width=4,
                validatecommand=(self.validate_cmd_2, "%P", "%V"),
            )
            for i in range(2)
        ]
        self.iv_max = [
            MyButton(
                self.iv_box[i],
                text="31",
                command=lambda index=i: self.change_iv(True, index),
            )
            for i in range(2)
        ]
        self.iv_min = [
            MyButton(
                self.iv_box[i],
                text="0",
                command=lambda index=i: self.change_iv(False, index),
            )
            for i in range(2)
        ]
        self.iv_entry[0].bind("<<TextModified>>", self.calc_speed)
        self.iv_entry[1].bind("<<TextModified>>", self.calc_speed)

        # 努力値
        self.ev_box = [ttk.Frame(self, padding=10), ttk.Frame(self, padding=10)]
        self.ev_entry = [
            ModifiedEntry(
                self.ev_box[i],
                validate="key",
                width=4,
                validatecommand=(self.validate_cmd_3, "%P", "%V"),
            )
            for i in range(2)
        ]
        self.ev_max = [
            MyButton(
                self.ev_box[i],
                text="252",
                command=lambda index=i: self.change_ev(True, index),
            )
            for i in range(2)
        ]
        self.ev_min = [
            MyButton(
                self.ev_box[i],
                text="0",
                command=lambda index=i: self.change_ev(False, index),
            )
            for i in range(2)
        ]
        self.ev_entry[0].bind("<<TextModified>>", self.calc_speed)
        self.ev_entry[1].bind("<<TextModified>>", self.calc_speed)

        # 性格
        self.nature_box = [ttk.Frame(self), ttk.Frame(self)]
        self.nature_radio1 = [
            tkinter.Radiobutton(
                self.nature_box[i],
                text="0.9",
                variable=self.nature_var[i],
                value="0.9",
                command=self.calc_speed,
            )
            for i in range(2)
        ]
        self.nature_radio2 = [
            tkinter.Radiobutton(
                self.nature_box[i],
                text="1.0",
                variable=self.nature_var[i],
                value="1.0",
                command=self.calc_speed,
            )
            for i in range(2)
        ]
        self.nature_radio3 = [
            tkinter.Radiobutton(
                self.nature_box[i],
                text="1.1",
                variable=self.nature_var[i],
                value="1.1",
                command=self.calc_speed,
            )
            for i in range(2)
        ]

        # ランク
        self.rank_box = [ttk.Frame(self, padding=10), ttk.Frame(self, padding=10)]
        self.rank_minus = [
            MyButton(
                self.rank_box[i],
                text="-1",
                command=lambda index=i: self.change_rank(False, index),
            )
            for i in range(2)
        ]
        self.rank = [
            tkinter.Label(self.rank_box[i], textvariable=self.rank_var[i])
            for i in range(2)
        ]
        self.rank_plus = [
            MyButton(
                self.rank_box[i],
                text="+1",
                command=lambda index=i: self.change_rank(True, index),
            )
            for i in range(2)
        ]

        # 特性
        self.ability_box = [ttk.Frame(self), ttk.Frame(self)]
        self.ability_radio1 = [
            tkinter.Radiobutton(
                self.ability_box[i],
                text="0.5",
                variable=self.ability_var[i],
                value="0.5",
                command=self.calc_speed,
            )
            for i in range(2)
        ]
        self.ability_radio2 = [
            tkinter.Radiobutton(
                self.ability_box[i],
                text="1.0",
                variable=self.ability_var[i],
                value="1.0",
                command=self.calc_speed,
            )
            for i in range(2)
        ]
        self.ability_radio3 = [
            tkinter.Radiobutton(
                self.ability_box[i],
                text="1.5",
                variable=self.ability_var[i],
                value="1.5",
                command=self.calc_speed,
            )
            for i in range(2)
        ]
        self.ability_radio4 = [
            tkinter.Radiobutton(
                self.ability_box[i],
                text="2.0",
                variable=self.ability_var[i],
                value="2.0",
                command=self.calc_speed,
            )
            for i in range(2)
        ]

        # 道具
        self.item_box = [ttk.Frame(self), ttk.Frame(self)]
        self.item_radio1 = [
            tkinter.Radiobutton(
                self.item_box[i],
                text="0.5",
                variable=self.item_var[i],
                value="0.5",
                command=self.calc_speed,
            )
            for i in range(2)
        ]
        self.item_radio2 = [
            tkinter.Radiobutton(
                self.item_box[i],
                text="1.0",
                variable=self.item_var[i],
                value="1.0",
                command=self.calc_speed,
            )
            for i in range(2)
        ]
        self.item_radio3 = [
            tkinter.Radiobutton(
                self.item_box[i],
                text="1.5",
                variable=self.item_var[i],
                value="1.5",
                command=self.calc_speed,
            )
            for i in range(2)
        ]
        self.item_radio4 = [
            tkinter.Radiobutton(
                self.item_box[i],
                text="2.0",
                variable=self.item_var[i],
                value="2.0",
                command=self.calc_speed,
            )
            for i in range(2)
        ]

        # おいかぜ
        self.tailwind_checkbox = [
            tkinter.Checkbutton(
                self, variable=self.tailwind_var[i], command=self.change_tailwind
            )
            for i in range(2)
        ]

        # まひ
        self.paralysis_checkbox = [
            tkinter.Checkbutton(
                self, variable=self.paralysis_var[i], command=self.change_paralysis
            )
            for i in range(2)
        ]

        self.all_components: list[list] = [
            self.pokemon_icon,
            self.name_label,
            self.speed_label,
            self.base_stat,
            self.iv_box,
            self.ev_box,
            self.nature_box,
            self.rank_box,
            self.ability_box,
            self.item_box,
            self.tailwind_checkbox,
            self.paralysis_checkbox,
        ]

        self.all_sub_components: list[list] = [
            self.iv_entry,
            self.iv_min,
            self.iv_max,
            self.ev_entry,
            self.ev_min,
            self.ev_max,
            self.nature_radio1,
            self.nature_radio2,
            self.nature_radio3,
            self.rank_minus,
            self.rank,
            self.rank_plus,
            self.ability_radio1,
            self.ability_radio2,
            self.ability_radio3,
            self.ability_radio4,
            self.item_radio1,
            self.item_radio2,
            self.item_radio3,
            self.item_radio4,
        ]

        for i in range(2):
            for j in range(len(self.all_sub_components)):
                self.all_sub_components[j][i].pack(side="left")

        for i in range(2):
            for j in range(len(self.all_components)):
                self.all_components[j][i].grid(row=j, column=i * 2, pady=5)

    def set_pokemon(self, pokemons: list[Pokemon]):
        self.pokemons = pokemons
        for i in range(2):
            self.pokemon_icon[i].set_pokemon_icon(pokemons[i].pid, [60, 60])
            self.name_var[i].set(pokemons[i].name)
            self.base_stat_var[i].set(pokemons[i].syuzoku.S)
            self.iv_entry[i].delete(0, tkinter.END)
            self.iv_entry[i].insert(0, pokemons[i].kotai.S)
            self.ev_entry[i].delete(0, tkinter.END)
            self.ev_entry[i].insert(0, pokemons[i].doryoku.S)
            self.rank_var[i].set(pokemons[i].rank.S)
            if pokemons[i].seikaku in ["おくびょう", "せっかち", "やんちゃ", "ようき"]:
                self.nature_var[i].set("1.1")
            elif pokemons[i].seikaku in ["ゆうかん", "のんき", "れいせい", "なまいき"]:
                self.nature_var[i].set("0.9")
            if pokemons[i].item == "こだわりスカーフ":
                self.item_var[i].set("1.5")
        self.calc_speed()

    def change_rank(self, up: bool, player: int):
        rank = self.rank_var[player].get()
        if up and rank < 6:
            rank += 1
        elif not up and rank > -6:
            rank -= 1
        self.rank_var[player].set(rank)
        self.calc_speed()

    def change_iv(self, up: bool, player: int):
        self.iv_entry[player].delete(0, tkinter.END)
        if up:
            self.iv_entry[player].insert(0, "31")
        else:
            self.iv_entry[player].insert(0, "0")
        self.calc_speed()

    def change_ev(self, up: bool, player: int):
        self.ev_entry[player].delete(0, tkinter.END)
        if up:
            self.ev_entry[player].insert(0, "252")
        else:
            self.ev_entry[player].insert(0, "0")
        self.calc_speed()

    def change_tailwind(self):
        for i in range(2):
            if self.tailwind_var[i].get():
                self.tailwind[i] = 2.0
            else:
                self.tailwind[i] = 1.0
        self.calc_speed(self)

    def change_paralysis(self):
        for i in range(2):
            if self.paralysis_var[i].get():
                self.paralysis[i] = 0.5
            else:
                self.paralysis[i] = 1.0
        self.calc_speed(self)

    def calc_speed(self, *args):
        rank = [
            (
                (self.rank_var[i].get() + 2) / 2
                if self.rank_var[i].get() >= 0
                else 2 / (abs(self.rank_var[i].get()) + 2)
            )
            for i in range(2)
        ]
        base = [
            (
                (
                    self.base_stat_var[i].get() * 2
                    + int(self.iv_entry[i].get())
                    + int(self.ev_entry[i].get()) / 4
                )
                * 50
                / 100
                + 5
            )
            * float(self.nature_var[i].get())
            * float(self.ability_var[i].get())
            * float(self.item_var[i].get())
            * self.tailwind[i]
            * self.paralysis[i]
            * rank[i]
            for i in range(2)
        ]

        if int(base[0]) < int(base[1]):
            self.compare_mark.set("<")
            self.speed_label[0]["fg"] = "blue"
            self.speed_label[1]["fg"] = "red"
        elif int(base[0]) > int(base[1]):
            self.compare_mark.set(">")
            self.speed_label[0]["fg"] = "red"
            self.speed_label[1]["fg"] = "blue"
        else:
            self.compare_mark.set("=")
            self.speed_label[0]["fg"] = "black"
            self.speed_label[1]["fg"] = "black"

        for i in range(2):
            self.speed_var[i].set(int(base[i]))

    def open(self, location=tuple[int, int]):
        self.grab_set()
        self.focus_set()
        self.geometry("+{0}+{1}".format(location[0], location[1]))


# キャプチャ設定画面
class CaptureSetting(tkinter.Toplevel):
    def __init__(
        self, title: str = "キャプチャ設定", width: int = 400, height: int = 300
    ):
        super().__init__()
        self.title(title)
        self.path = "recog/capture.json"

        # JSONファイルから初期値を読み取り
        try:
            with open(self.path, "r") as json_file:
                self.initial_data = json.load(json_file)
        except FileNotFoundError:
            self.initial_data = {
                "source_name": "",
                "host_name": "",
                "port": "",
                "password": "",
            }

        # ラベルとエントリーの作成
        self.source_label = tkinter.Label(self, text="ソース名:")
        self.source_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.source_entry = tkinter.Entry(self)
        self.source_entry.insert(0, self.initial_data["source_name"])
        self.source_entry.grid(row=0, column=1, padx=10, pady=5)

        self.host_label = tkinter.Label(self, text="ホスト名:")
        self.host_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.host_entry = tkinter.Entry(self)
        self.host_entry.insert(0, self.initial_data["host_name"])
        self.host_entry.grid(row=1, column=1, padx=10, pady=5)

        self.port_label = tkinter.Label(self, text="ポート:")
        self.port_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.port_entry = tkinter.Entry(self)
        self.port_entry.insert(0, self.initial_data["port"])
        self.port_entry.grid(row=2, column=1, padx=10, pady=5)

        self.password_label = tkinter.Label(self, text="パスワード:")
        self.password_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.password_entry = tkinter.Entry(self)
        self.password_entry.insert(0, self.initial_data["password"])
        self.password_entry.grid(row=3, column=1, padx=10, pady=5)

        self.submit_button = MyButton(self, text="保存", command=self.submit_form)
        self.submit_button.grid(row=4, column=0, pady=10)
        self.cancel_button = MyButton(
            self, text="キャンセル", command=self.on_push_button
        )
        self.cancel_button.grid(row=4, column=1, pady=10)

    def open(self, location=tuple[int, int]):
        self.grab_set()
        self.focus_set()
        self.geometry("+{0}+{1}".format(location[0], location[1]))

    def submit_form(self):
        # 入力された値を取得
        self.source_name = self.source_entry.get()
        self.host_name = self.host_entry.get()
        self.port = self.port_entry.get()
        self.password = self.password_entry.get()

        # 入力された値をJSONファイルに保存
        data = {
            "source_name": self.source_name,
            "host_name": self.host_name,
            "port": self.port,
            "password": self.password,
        }

        with open(self.path, "w") as json_file:
            json.dump(data, json_file, indent=2)

        self.destroy()

    def on_push_button(self):
        self.destroy()


# モード切替画面
class ModeSetting(tkinter.Toplevel):
    def __init__(self, title: str = "モード切替", width: int = 400, height: int = 400):
        super().__init__()
        self.title(title)
        self.path = "recog/setting.json"

        # JSONファイルから初期値を読み取り
        try:
            with open(self.path, "r") as json_file:
                self.initial_data = json.load(json_file)
        except FileNotFoundError:
            self.initial_data = {
                "active_chosen_auto": True,
                "capture_monitor_auto": True,
                "doryoku_reset_auto": True,
                "similar_party_auto": False,
            }

        # チェックボックス1
        self.active_chosen_auto_var = tkinter.BooleanVar()
        self.active_chosen_auto_var.set(self.initial_data["active_chosen_auto"])
        self.active_chosen_auto_checkbox = tkinter.Checkbutton(
            self, text="相手選出自動登録モード", variable=self.active_chosen_auto_var
        )
        self.active_chosen_auto_checkbox.grid(row=0, column=0, columnspan=2, pady=5)

        # チェックボックス2
        self.capture_monitor_auto_var = tkinter.BooleanVar()
        self.capture_monitor_auto_var.set(self.initial_data["capture_monitor_auto"])
        self.capture_monitor_auto_checkbox = tkinter.Checkbutton(
            self,
            text="キャプチャ監視自動開始モード",
            variable=self.capture_monitor_auto_var,
        )
        self.capture_monitor_auto_checkbox.grid(row=1, column=0, columnspan=2, pady=5)

        # チェックボックス3
        self.doryoku_reset_auto_var = tkinter.BooleanVar()
        self.doryoku_reset_auto_var.set(self.initial_data["doryoku_reset_auto"])
        self.doryoku_reset_auto_checkbox = tkinter.Checkbutton(
            self,
            text="相手性格変更時自動努力値変更モード",
            variable=self.doryoku_reset_auto_var,
        )
        self.doryoku_reset_auto_checkbox.grid(row=2, column=0, columnspan=2, pady=5)

        # チェックボックス4
        self.similar_party_auto_var = tkinter.BooleanVar()
        self.similar_party_auto_var.set(self.initial_data["similar_party_auto"])
        self.similar_party_auto_checkbox = tkinter.Checkbutton(
            self,
            text="類似パーティ自動検索モード",
            variable=self.similar_party_auto_var,
        )
        self.similar_party_auto_checkbox.grid(row=3, column=0, columnspan=2, pady=5)

        self.submit_button = MyButton(self, text="保存", command=self.submit_form)
        self.submit_button.grid(row=4, column=0, pady=10)
        self.cancel_button = MyButton(
            self, text="キャンセル", command=self.on_push_button
        )
        self.cancel_button.grid(row=4, column=1, pady=10)

    def open(self, location=tuple[int, int]):
        self.grab_set()
        self.focus_set()
        self.geometry("+{0}+{1}".format(location[0], location[1]))

    def submit_form(self):
        # 入力された値をJSONファイルに保存
        data = {
            "active_chosen_auto": self.active_chosen_auto_var.get(),
            "capture_monitor_auto": self.capture_monitor_auto_var.get(),
            "doryoku_reset_auto": self.doryoku_reset_auto_var.get(),
            "similar_party_auto": self.similar_party_auto_var.get(),
        }

        with open(self.path, "w") as json_file:
            json.dump(data, json_file, indent=2)

        self.destroy()

    def on_push_button(self):
        self.destroy()


# フォーム選択画面
class FormSelect(tkinter.Toplevel):
    def __init__(
        self, title: str = "フォーム選択", width: int = 400, height: int = 300
    ):
        super().__init__()
        self.title(title)
        self.form_num = -1

    def set_pokemon(self, num: int):
        self.no = str(num)
        self.pokemon_names = DB.get_pokemons_name_by_no(self.no)

        for i in range(len(self.pokemon_names)):
            self.form_button = MyButton(
                self,
                text=self.pokemon_names[i],
                command=lambda index=i: self.on_push_button(index),
            )
            self.form_button.grid(row=1, column=i, pady=10)

    def open(self, location=tuple[int, int]):
        self.grab_set()
        self.focus_set()
        self.geometry("+{0}+{1}".format(location[0], location[1]))

    def on_push_button(self, index):
        self.form_num = index
        self.destroy()


# フォーム選択画面
class SimilarParty(tkinter.Toplevel):
    def __init__(
        self,
        title: str = "類似パーティ検索結果",
        width: int = 400,
        height: int = 300,
        current_party: list[str] = None,
        party_list: list[dict] = None,
    ):
        if current_party is None:
            current_party = []
        if party_list is None:
            party_list = []
        super().__init__()
        self.title(title)

        result_all_label = ttk.Label(
            self, text=f"検索結果：{len(party_list)}件", padding=10
        )
        result_all_label.pack(side="top")
        if len(party_list) != 0:
            result_perfect = [
                party_list[i]
                for i in range(len(party_list))
                if party_list[i]["icons"] == current_party
            ]
            result_part = list(filter(lambda x: x not in result_perfect, party_list))

            result_perfect_label = ttk.Label(
                self, text=f"並びまで完全一致：{len(result_perfect)}件", padding=10
            )
            result_perfect_label.pack(side="top")
            if len(result_perfect) != 0:
                for i in range(len(result_perfect)):
                    icons_frame = ttk.Frame(self, padding=10)
                    for j in range(6):
                        icon = MyLabel(
                            icons_frame,
                        )
                        icon.set_pokemon_icon(
                            result_perfect[i]["icons"][j], size=(30, 30)
                        )
                        icon.pack(side="left", padx=20, pady=10)
                    link_button = MyButton(
                        icons_frame,
                        text="構築記事",
                        command=lambda url=result_perfect[i]["url"]: webbrowser.open(
                            url
                        ),
                    )
                    link_button.pack(side="left", padx=50)
                    icons_frame.pack(side="top")

            result_part_label = ttk.Label(
                self, text=f"6匹同じポケモン：{len(result_part)}件", padding=10
            )
            result_part_label.pack(side="top")
            if len(result_part) != 0:
                for i in range(len(result_part)):
                    icons_frame = ttk.Frame(self)
                    for j in range(6):
                        icon = MyLabel(
                            icons_frame,
                        )
                        icon.set_pokemon_icon(result_part[i]["icons"][j], size=(30, 30))
                        icon.pack(side="left", padx=20, pady=10)
                    link_button = MyButton(
                        icons_frame,
                        text="構築記事",
                        command=lambda url=result_part[i]["url"]: webbrowser.open(url),
                    )
                    link_button.pack(side="left", padx=50)
                    icons_frame.pack(side="top")

    def open(self, location=tuple[int, int]):
        self.grab_set()
        self.focus_set()
        self.geometry("+{0}+{1}".format(location[0], location[1]))


# 重さ比較画面
class WeightComparing(tkinter.Toplevel):
    def __init__(self, title: str = "重さ比較", width: int = 600, height: int = 500):
        super().__init__()
        self.title(title)
        self.pokemons: list[Pokemon] = [Pokemon(), Pokemon()]

        self.name_var: list[tkinter.StringVar] = [
            tkinter.StringVar(),
            tkinter.StringVar(),
        ]
        self.compare_mark: tkinter.StringVar = tkinter.StringVar()
        self.weight_var: list[tkinter.DoubleVar] = [
            tkinter.DoubleVar(),
            tkinter.DoubleVar(),
        ]
        self.power_var: list[tkinter.IntVar] = [
            tkinter.IntVar(),
            tkinter.IntVar(),
        ]

        self.pokemon_icon: list[MyLabel] = [MyLabel(self), MyLabel(self)]
        self.name_label = [
            tkinter.Label(self, textvariable=self.name_var[i]) for i in range(2)
        ]
        self.weight_label = [
            tkinter.Label(
                self, textvariable=self.weight_var[i], font=Font(weight="bold", size=32)
            )
            for i in range(2)
        ]

        self.power_label = [
            tkinter.Label(
                self, textvariable=self.power_var[i], font=Font(weight="bold", size=32)
            )
            for i in range(2)
        ]

        self.compare = tkinter.Label(
            self, textvariable=self.compare_mark, font=Font(weight="bold", size=16)
        )
        self.compare.grid(row=2, column=1, pady=5)

        self.power_name_label = tkinter.Label(
            self, text="威力", font=Font(weight="bold", size=16)
        )
        self.power_name_label.grid(row=3, column=1, pady=5)

        self.all_components: list[list] = [
            self.pokemon_icon,
            self.name_label,
        ]

        for i in range(2):
            for j in range(len(self.all_components)):
                self.all_components[j][i].grid(row=j, column=i * 2, pady=5)

        for i in range(2):
            self.weight_label[i].grid(row=2, column=i * 2, pady=5)
            self.power_label[i].grid(row=3, column=i * 2, pady=5)

    def set_pokemon(self, pokemons: list[Pokemon]):
        self.pokemons = pokemons
        for i in range(2):
            self.pokemon_icon[i].set_pokemon_icon(pokemons[i].pid, [60, 60])
            self.name_var[i].set(pokemons[i].name)
            self.weight_var[i].set(pokemons[i].weight)
        self.calc_weight()
        self.calc_power()

    def calc_weight(self, *args):
        if self.weight_var[0].get() < self.weight_var[1].get():
            self.compare_mark.set("<")
            self.weight_label[0]["fg"] = "blue"
            self.weight_label[1]["fg"] = "red"
        elif self.weight_var[0].get() > self.weight_var[1].get():
            self.compare_mark.set(">")
            self.weight_label[0]["fg"] = "red"
            self.weight_label[1]["fg"] = "blue"
        else:
            self.compare_mark.set("=")
            self.weight_label[0]["fg"] = "black"
            self.weight_label[1]["fg"] = "black"

    def calc_power(self, *args):
        power: list[float] = [
            self.weight_var[1].get() / self.weight_var[0].get(),
            self.weight_var[0].get() / self.weight_var[1].get(),
        ]

        for i in range(2):
            if power[i] < 0.2:
                self.power_var[i].set(120)
            elif power[i] < 0.25:
                self.power_var[i].set(100)
            elif power[i] < 0.3:
                self.power_var[i].set(80)
            elif power[i] < 0.5:
                self.power_var[i].set(60)
            else:
                self.power_var[i].set(40)

    def open(self, location=tuple[int, int]):
        self.grab_set()
        self.focus_set()
        self.geometry("+{0}+{1}".format(location[0], location[1]))
