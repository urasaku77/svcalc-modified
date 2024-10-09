# coding: utf-8

import csv
import glob
import math
import os
import tkinter
from tkinter import E, N, S, W, filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from component.parts import images
from component.parts.button import MyButton, TypeButton
from component.parts.combobox import (
    AutoCompleteCombobox,
    ModifiedEntry,
    MyCombobox,
    WazaNameCombobox,
)
from component.parts.const import ALL_ITEM_COMBOBOX_VALUES
from component.parts.dialog import PokemonMemoLabelDialog, TypeSelectDialog
from component.parts.label import MyLabel
from database.pokemon import DB_pokemon
from pokedata.const import Types
from pokedata.nature import get_seikaku_hosei, get_seikaku_list
from pokedata.pokemon import Pokemon
from pokedata.stats import StatsKey


# パーティCSV編集用ダイアログ
class PartyEditor(tkinter.Toplevel):
    def __init__(self, title: str = "パーティ編集"):
        super().__init__()
        self.title(title)

        main_frame = ttk.Frame(self, padding=5)
        main_frame.grid(row=0, column=0, sticky=N + E + W + S)

        self.settings = PartySettings(main_frame, padding=5)
        self.settings.grid(row=0, column=0, columnspan=2, sticky=N + E + W + S)

        csv_button = ttk.Frame(main_frame)
        self.read_csv_button = MyButton(
            csv_button, text="CSV読み込み", command=self.select_csv
        )
        self.read_csv_button.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + W + E)

        self.write_csv_button = MyButton(
            csv_button, text="CSV書き込み", command=self.save_csv
        )
        self.write_csv_button.grid(
            row=1, column=0, padx=5, pady=5, sticky=N + S + W + E
        )

        self.make_table_button = MyButton(
            csv_button, text="星取表作成", command=self.make_table
        )
        self.make_table_button.grid(
            row=0, column=1, padx=5, pady=5, sticky=N + S + W + E
        )

        self.all_clear_button = MyButton(
            csv_button, text="全クリア", command=self.all_clear
        )
        self.all_clear_button.grid(
            row=1, column=1, padx=5, pady=5, sticky=N + S + W + E
        )

        csv_button.grid(
            row=0,
            column=2,
            columnspan=2,
            padx=5,
            pady=5,
            sticky=N + S + W,
        )

        self.using = UseParty(main_frame, text="使用するパーティ", padding=5)
        self.using.grid(row=0, column=3, columnspan=2, sticky=N + E + S + W)

        self.pokemons = PokemonEditors(main_frame, text="パーティ編集", padding=5)
        self.pokemons.grid(row=1, column=0, columnspan=5, sticky=N + E + W + S)

        self.select_csv(csv=self.using.using_var.get())

    def save_csv(self):
        ret = messagebox.askyesno(
            "確認",
            "表示されているデータをCSV書き込みますか？\n（既存のファイルの場合は上書きされます）",
        )
        if ret is False:
            return
        self.title = self.settings.title_entry.get()
        self.num = self.settings.num_entry.get()
        self.sub_num = self.settings.sub_num_entry.get()

        if self.title == "":
            return

        # 新規登録時の採番処理
        file_list = sorted(glob.glob("party/csv/*"))
        if self.num == "":
            messagebox.showinfo("警告", "番号を入力してください")
            return
        elif self.sub_num == "":
            same_num_list = [
                file
                for file in file_list
                if file.startswith("party/csv\\" + self.num + "-")
            ]
            last_same_num_file = (
                sorted(same_num_list)[len(same_num_list) - 1]
                if len(same_num_list) > 0
                else "1-0"
            )
            self.sub_num = str(int(last_same_num_file.split("-")[1][0]) + 1)

        # CSV書き込み処理
        filepath = (
            "party\\csv\\" + self.num + "-" + self.sub_num + "_" + self.title + ".csv"
        )
        with open(filepath, "w") as party_csv:
            writer = csv.writer(party_csv, lineterminator="\n")
            writer.writerow(
                [
                    "名前",
                    "個体値",
                    "努力値",
                    "性格",
                    "持ち物",
                    "特性",
                    "テラス",
                    "メモ",
                    "技",
                    "技",
                    "技",
                    "技",
                ]
            )
            for pokemon in self.pokemons.pokemon_panel_list:
                row = pokemon.set_csv_row()
                writer.writerow(row)

        # メモ書き込み処理
        self.memo = self.settings.memo.get("1.0", "end-1c")
        with open(
            "party\\txt\\" + self.num + "-" + self.sub_num + "_" + self.title + ".txt",
            "w",
        ) as txt:
            txt.write(self.memo)
            txt.close()

        # 使用するパーティ変更処理
        if self.settings.is_use_var.get():
            self.using.change_csv(value=filepath.split("party\\csv\\")[1])

    def select_csv(self, csv: str = ""):
        if csv == "":
            typ = [("", "*.csv")]
            current_directory = os.getcwd()
            fle = filedialog.askopenfilename(
                filetypes=typ,
                initialdir=os.path.join(current_directory, "party", "csv"),
            )
            if fle == "":
                return

            csv = fle.split("party/csv/")[1]

        self.settings.clear_setting()

        self.settings.num_entry.insert(0, csv.split("-")[0])
        self.settings.sub_num_entry.insert(0, csv.split("-")[1].split("_")[0])
        self.settings.title_entry.insert(
            0, csv.split("-")[1].split("_")[1].split(".")[0]
        )
        memo_file = "party\\txt\\" + csv.replace("csv", "txt")
        with open(memo_file, "r") as txt:
            self.memo = txt.read()
            txt.close()
        self.settings.memo.insert(tkinter.END, self.memo)
        self.settings.is_use_var.set(
            True
        ) if csv == self.using.using_var.get() else self.settings.is_use_var.set(False)

        from pokedata.loader import get_party_data

        for i, data in enumerate(get_party_data(file_path="party/csv/" + csv)):
            pokemon: Pokemon = Pokemon.by_name(data[0])
            pokemon.set_load_data(data, True)
            self.pokemons.pokemon_panel_list[i].set_pokemon(pokemon)
            self.pokemons.pokemon_panel_list[i].change_ev()

    def all_clear(self):
        ret = messagebox.askyesno(
            "確認", "表示されているデータをすべてクリアしますか？"
        )
        if ret is True:
            self.settings.clear_setting()
            for pokemon in self.pokemons.pokemon_panel_list:
                pokemon.clear_pokemon()

    def open(self, location=tuple[int, int]):
        self.grab_set()
        self.focus_set()
        self.geometry("+{0}+{1}".format(location[0], location[1]))

    def make_table(self):
        num = self.input_num()
        pids = []
        with open("stats/ranking.txt", encoding="utf-8") as ranking_txt:
            pids = [next(ranking_txt).strip() for _ in range(num)]

        pokemons = [Pokemon.by_pid(pids[i]).name for i in range(len(pids))]

        self.title = self.settings.title_entry.get()
        self.num = self.settings.num_entry.get()
        self.sub_num = self.settings.sub_num_entry.get()

        table_name = (
            f"{self.num}-{self.sub_num}_{self.title}"
            if f"{self.num}-{self.sub_num}_{self.title}" != ""
            else "undefined"
        )

        with open(f"party/table/{table_name}.csv", mode="w", newline="") as table_csv:
            pokemons.insert(0, "")
            writer = csv.writer(table_csv)
            writer.writerow(pokemons)
            for pokemon in self.pokemons.pokemon_panel_list:
                party = [""] * num
                party.insert(0, pokemon._pokemon_name_var.get())
                writer.writerow(party)

    def input_num(self):
        dialog = TableNumInputDialog()
        dialog.open(location=(self.winfo_x(), self.winfo_y()))
        self.wait_window(dialog)
        return dialog.no


class PartySettings(ttk.Frame):
    def on_validate_4(self, P, V):
        if P.isdigit() or P == "":
            return len(P) <= 4
        else:
            return False

    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)
        self.validate_cmd_4 = self.register(self.on_validate_4)

        self.edit_frame = ttk.LabelFrame(master=self, text="パーティ情報")
        self.edit_frame.pack(side="left")

        self.num_label = ttk.Label(self.edit_frame, text="番号")
        self.num_label.grid(row=0, column=0, sticky=N + S, padx=3)
        self.num_entry = ModifiedEntry(
            self.edit_frame,
            validate="key",
            width=8,
            validatecommand=(self.validate_cmd_4, "%P", "%V"),
        )
        self.num_entry.grid(row=0, column=1, sticky=E + W)

        self.sub_num_label = ttk.Label(self.edit_frame, text="連番")
        self.sub_num_label.grid(row=0, column=2, sticky=N + E + W + S, padx=3, pady=3)
        self.sub_num_entry = ModifiedEntry(
            self.edit_frame,
            validate="key",
            width=8,
            validatecommand=(self.validate_cmd_4, "%P", "%V"),
        )
        self.sub_num_entry.grid(row=0, column=3, sticky=E + W, padx=3, pady=3)

        self.is_use_var = tkinter.BooleanVar()
        self.is_use_check = tkinter.Checkbutton(
            self.edit_frame, variable=self.is_use_var, text="使用するパーティに設定"
        )
        self.is_use_check.grid(row=0, column=4, sticky=N + E + W + S, padx=3, pady=3)

        self.title_label = ttk.Label(self.edit_frame, text="タイトル")
        self.title_label.grid(row=1, column=0, sticky=N + E + W + S, padx=3, pady=3)
        self.title_entry = tkinter.Entry(self.edit_frame)
        self.title_entry.grid(
            row=1, column=1, columnspan=4, sticky=N + E + W + S, padx=3, pady=3
        )

        self.memo_label = ttk.Label(self.edit_frame, text="メモ")
        self.memo_label.grid(column=5, row=0, rowspan=2, sticky=N + E + W + S)
        self.memo = ScrolledText(self.edit_frame, height=3, width=60, padx=3, pady=3)
        self.memo.grid(column=6, row=0, columnspan=4, rowspan=2, sticky=N + E + W + S)

    def clear_setting(self):
        self.num_entry.delete(0, tkinter.END)
        self.sub_num_entry.delete(0, tkinter.END)
        self.is_use_var.set(False)
        self.title_entry.delete(0, tkinter.END)
        self.memo.delete("1.0", tkinter.END)


class UseParty(ttk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)
        self.grid_columnconfigure([0, 1, 2, 3], weight=1)
        self.grid_rowconfigure([0, 1], weight=1)

        self.using_var = tkinter.StringVar()
        self.using_var.set("test.csv")
        self.using_label = MyLabel(self, textvariable=self.using_var)
        self.using_label.grid(
            column=0, row=0, rowspan=2, columnspan=3, sticky=N + W + E + S
        )

        self.using_button = MyButton(self, text="変更", command=self.change_csv)
        self.using_button.grid(column=3, row=0, rowspan=2, sticky=E)

        self.get_using_csv()
        self.using_var.set(self.using_party)

    def get_using_csv(self):
        with open("party\\setting.txt", "r") as txt:
            self.using_party = txt.read()
            self.using_var.set(self.using_party)
            txt.close()

    def change_csv(self, value: str = ""):
        if value == "":
            typ = [("", "*.csv")]
            current_directory = os.getcwd()
            value = filedialog.askopenfilename(
                filetypes=typ,
                initialdir=os.path.join(current_directory, "party", "csv"),
            ).split("party/csv/")[1]

        with open("party\\setting.txt", "w") as txt:
            txt.write(value)
            self.using_var.set(value)
            txt.close()


class PokemonEditors(ttk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)
        self.pokemon_panel_list: list[PokemonEditor] = []

        for i in range(6):
            self.change_widget = ttk.Frame(self)
            self.up_button = ttk.Button(
                self.change_widget,
                command=lambda index=i: self.change_line(True, index),
                text="↑",
                width=3,
            )
            self.up_button.pack(side="left")
            self.pokemon_label = ttk.Label(self.change_widget, text=str(i + 1) + "体目")
            self.pokemon_label.pack(side="left")
            self.down_button = ttk.Button(
                self.change_widget,
                command=lambda index=i: self.change_line(False, index),
                text="↓",
                width=3,
            )
            self.down_button.pack(side="left")
            self.pokemon_panel = PokemonEditor(self, labelwidget=self.change_widget)
            c = i if i < 3 else i - 3
            r = 0 if i < 3 else 1
            self.pokemon_panel.grid(column=c, row=r, sticky=E, pady=3)
            self.pokemon_panel_list.append(self.pokemon_panel)

    def change_line(self, up: bool, num: int):
        if up and num != 0:
            pokemon1 = self.pokemon_panel_list[num - 1].pokemon
            pokemon2 = self.pokemon_panel_list[num].pokemon

            self.pokemon_panel_list[num - 1].set_pokemon(pokemon2)
            self.pokemon_panel_list[num].set_pokemon(pokemon1)

        elif not up and num != 5:
            pokemon1 = self.pokemon_panel_list[num].pokemon
            pokemon2 = self.pokemon_panel_list[num + 1].pokemon

            self.pokemon_panel_list[num].set_pokemon(pokemon2)
            self.pokemon_panel_list[num + 1].set_pokemon(pokemon1)


class PokemonEditor(ttk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)

        self.pokemon: Pokemon = Pokemon()
        self.syuzoku_list: list[tkinter.IntVar] = []
        self.jissu_list: list[tkinter.IntVar] = []
        self.waza_list: list[WazaNameCombobox] = []

        self._pokemon_icon = MyButton(
            self, size=(60, 60), padding=0, command=self.edit_pokemon
        )
        self._pokemon_icon.grid(column=0, row=0, rowspan=2, columnspan=2, sticky=N + S)

        self._pokemon_name_var = tkinter.StringVar()
        self._pokemon_name_label = ttk.Label(self, textvariable=self._pokemon_name_var)
        self._pokemon_name_label.grid(column=0, row=2, columnspan=2)

        self._clear_button = MyButton(
            self, image=images.get_menu_icon("trush"), command=self.clear_pokemon
        )
        self._clear_button.grid(column=2, row=0)

        self._teras_var = Types.なし
        self._teras_button = TypeButton(
            self, type_=Types.なし, command=self.on_push_terasbutton
        )
        self._teras_button.grid(column=0, row=3, columnspan=2, sticky=W + E + N + S)

        self._memo_var = ""

        self.img = [tkinter.PhotoImage(file=Types.なし.icon).subsample(3, 3)] * 2
        self.type_img = ttk.Frame(self)
        self.type_img.grid(column=3, row=0)
        self.type1_img = self.img[0]
        self.type1_icon = ttk.Label(self.type_img, image=self.type1_img)
        self.type1_icon.pack(side="left")
        self.type2_img = self.img[1]
        self.type2_icon = ttk.Label(self.type_img, image=self.type2_img)
        self.type2_icon.pack(side="left")

        for i, text in enumerate(["性格", "持ち物", "特性"]):
            label = MyLabel(self, text=text)
            label.grid(column=2, row=i + 1, padx=5, pady=5)

        self._seikaku_combobox = MyCombobox(self, values=get_seikaku_list(), width=24)
        self._seikaku_combobox.bind("<<ComboboxSelected>>", self.calc_status)
        self._seikaku_combobox.grid(column=3, row=1, sticky=W + E + N + S)

        self._item_combobox = MyCombobox(self, values=ALL_ITEM_COMBOBOX_VALUES)
        self._item_combobox.grid(column=3, row=2, sticky=W + E + N + S)

        self._ability_combobox = MyCombobox(self, width=16)
        self._ability_combobox.grid(column=3, row=3, sticky=W + E + N + S)

        self._waza_label = MyLabel(self, text="わざ")
        self._waza_label.grid(column=4, row=0, rowspan=4, padx=5, pady=5)
        for i in range(4):
            cbx = WazaNameCombobox(self, width=16)
            cbx.grid(column=5, row=i)
            self.waza_list.append(cbx)

        self.memo_btn = MyButton(
            master=self,
            image=images.get_menu_icon("load"),
            padding=0,
            command=lambda: self.input_memo(),
        )
        self.memo_btn.grid(column=0, row=4)

        for i, text in enumerate(["HP", "攻撃", "防御", "特攻", "特防", "素早さ"]):
            label = MyLabel(self, text=text)
            label.grid(column=0, row=i + 5, padx=5, pady=5)
        for i, text in enumerate(["種族値", "実数値"]):
            label = MyLabel(self, text=text)
            label.grid(column=i + 1, row=4, padx=5, pady=5)
        for i in range(6):
            value = tkinter.IntVar()
            value.set(0)
            label = MyLabel(self, textvariable=value)
            label.grid(column=1, row=i + 5, padx=5, pady=5)
            self.syuzoku_list.append(value)
        for i in range(6):
            value = tkinter.IntVar()
            value.set(0)
            label = MyLabel(self, textvariable=value)
            label.grid(column=2, row=i + 5, padx=5, pady=5)
            self.jissu_list.append(value)

        self._ev_total = tkinter.StringVar()
        self._ev_total.set("努力値（合計： 0 ）")
        self._ev_label = MyLabel(self, textvariable=self._ev_total)
        self._ev_label.grid(column=3, row=4, padx=5, pady=5)

        self._iv_label = MyLabel(self, text="個体値")
        self._iv_label.grid(column=4, row=4, columnspan=2, padx=5, pady=5)
        self._register_button = MyButton(
            self,
            image=images.get_menu_icon("edit"),
            padding=0,
            command=self.register_pokemon_in_box,
        )
        self._register_button.grid(column=4, row=4, columnspan=2, sticky=N + S + E)

        self._ev_frame = EvEditors(master=self, callback=self.change_ev)
        self._ev_frame.grid(
            column=3, row=5, rowspan=6, padx=5, pady=5, sticky=N + W + E
        )

        self._iv_frame = IvEditors(master=self, callback=self.calc_status)
        self._iv_frame.grid(
            column=4, row=5, columnspan=2, rowspan=6, padx=5, pady=5, sticky=N + W + E
        )

    def edit_pokemon(self):
        dialog = PokemonInputDialog(pokemon=self.pokemon)
        dialog.open(location=(self.winfo_x(), self.winfo_y()))
        self.wait_window(dialog)
        if dialog.pokemon.no != -1:
            self.clear_pokemon()
            self.set_pokemon(dialog.pokemon)

    def set_pokemon(self, pokemon: Pokemon):
        self.pokemon = pokemon
        self._pokemon_icon.set_pokemon_icon(pid=pokemon.pid, size=(60, 60))
        self._pokemon_name_var.set(pokemon.name)
        self._teras_var = pokemon.terastype
        self._teras_button.set_type(pokemon.terastype)
        self._seikaku_combobox.set(pokemon.seikaku)
        self._item_combobox.set(pokemon.item)
        self._ability_combobox["values"] = pokemon.abilities
        self._ability_combobox.set(pokemon.ability)
        self.img[0] = tkinter.PhotoImage(file=pokemon.type[0].icon).subsample(3, 3)
        self.type1_icon.configure(
            image=self.img[0], text=pokemon.type[0].name, compound="left"
        )
        self.img[1] = tkinter.PhotoImage(
            file=pokemon.type[1].icon if len(pokemon.type) > 1 else Types.なし.icon
        ).subsample(3, 3)
        self.type2_icon.configure(
            image=self.img[1],
            text=pokemon.type[1].name if len(pokemon.type) > 1 else "",
            compound="left",
        )
        for i, statskey in enumerate([x for x in StatsKey]):
            self.syuzoku_list[i].set(pokemon.syuzoku[statskey])

        for i, statskey in enumerate([x for x in StatsKey]):
            self._ev_frame.ev_list[i].set_value(pokemon.doryoku[statskey], True)

        for i, statskey in enumerate([x for x in StatsKey]):
            self._iv_frame.iv_list[i].set_value(pokemon.kotai[statskey], True)

        for i, waza in enumerate(self.waza_list):
            value = pokemon.waza_list[i]
            waza.set(value.name if value is not None else "")

        self._memo_var = pokemon.memo

        self.calc_status()

    def clear_pokemon(self):
        self._pokemon_icon.set_image(images.get_blank_image(size=(60, 60)))
        self._pokemon_name_var.set("")
        self._teras_var = Types.なし
        self._teras_button.set_type(Types.なし)
        self._seikaku_combobox.set("")
        self._item_combobox.set("")
        self._ability_combobox["values"] = []
        self._ability_combobox.set("")
        self.img[0] = tkinter.PhotoImage(file=Types.なし.icon).subsample(3, 3)
        self.type1_icon.configure(
            image=self.img[0], text=Types.なし.name, compound="left"
        )
        self.img[1] = tkinter.PhotoImage(file=Types.なし.icon).subsample(3, 3)
        self.type2_icon.configure(
            image=self.img[1], text=Types.なし.name, compound="left"
        )

        for waza in self.waza_list:
            waza.set("")

        for syuzoku in self.syuzoku_list:
            syuzoku.set(0)

        for jissu in self.jissu_list:
            jissu.set(0)

        self._ev_frame.init_all_value()
        self._iv_frame.init_all_value()

        self._memo_var = ""
        self.pokemon = Pokemon()

    def on_push_terasbutton(self):
        type: Types = self.select_type()
        self._teras_var = type
        self._teras_button.set_type(type)

    def select_type(self) -> Types:
        dialog = TypeSelectDialog()
        dialog.open(location=(self.winfo_x(), self.winfo_y()))
        self.wait_window(dialog)
        return dialog.selected_type

    def change_ev(self, *args):
        value = 0
        for ev in self._ev_frame.ev_list:
            value += ev._ev_entry.value.get()
        self._ev_total.set("努力値（合計： " + str(value) + " ）")
        self.calc_status()

    def calc_status(self, *args):
        for i, syuzoku in enumerate(self.syuzoku_list):
            if syuzoku.get() != 0:
                if i == 0:
                    value = (
                        (syuzoku.get() * 2)
                        + self._iv_frame.iv_list[i]._iv_entry.value.get()
                        + math.floor(
                            self._ev_frame.ev_list[i]._ev_entry.value.get() / 4
                        )
                    )
                    value = math.floor(value / 2) + 60
                    self.jissu_list[i].set(value)
                else:
                    value = (
                        (syuzoku.get() * 2)
                        + self._iv_frame.iv_list[i]._iv_entry.value.get()
                        + math.floor(self._ev_frame.ev_list[i]._ev_entry.value.get())
                        / 4
                    )

                    value = math.floor(value / 2) + 5
                    value = math.floor(
                        value
                        * get_seikaku_hosei(self._seikaku_combobox.get(), StatsKey(i))
                    )
                    self.jissu_list[i].set(value)

    def set_csv_row(self):
        waza_list = self.get_all_waza()
        all_kotai = self._iv_frame.get_all_iv()
        all_doryoku = self._ev_frame.get_all_ev()

        if self._pokemon_name_var.get() == "":
            return ""
        else:
            return [
                self._pokemon_name_var.get(),
                all_kotai,
                all_doryoku,
                self._seikaku_combobox.get(),
                self._item_combobox.get(),
                self._ability_combobox.get(),
                self._teras_var.name if self._teras_var != Types.なし else "",
                self._memo_var,
                waza_list[0],
                waza_list[1],
                waza_list[2],
                waza_list[3],
            ]

    def get_all_waza(self):
        waza_list = []
        for waza in self.waza_list:
            waza_list.append(waza.get())
        return waza_list

    def input_memo(self):
        dialog = PokemonMemoInputDialog()
        dialog.open(self._memo_var, location=(self.winfo_x(), self.winfo_y()))
        self.wait_window(dialog)
        self._memo_var = dialog.memo

    def register_pokemon_in_box(self):
        if self.pokemon.no == -1:
            return
        ret = messagebox.askyesno(
            "確認",
            "ポケモンを登録しますか？",
        )
        if ret is False:
            return
        row = self.set_csv_row()
        with open("party\\csv\\box.csv", "r+") as box_csv:
            reader = csv.reader(box_csv)
            for lines in reader:
                if lines == row:
                    messagebox.showinfo("警告", "すでに全く同じ個体が登録されています")
                    return
            writer = csv.writer(box_csv, lineterminator="\n")
            writer.writerow(row)


class EvEditors(ttk.Frame):
    def __init__(self, master, callback, **kwargs):
        super().__init__(master=master, **kwargs)
        self.ev_list: list[EvEditor] = []
        for _i in range(6):
            self.ev_editor = EvEditor(self)
            self.ev_editor.setCallback(callback)
            self.ev_editor.pack(pady=5)
            self.ev_list.append(self.ev_editor)

    def init_all_value(self):
        for i in range(6):
            self.ev_list[i]._ev_entry.value.set(0)
            self.ev_list[i]._ev_entry.delete(0, tkinter.END)
            self.ev_list[i]._ev_entry.insert(0, 0)

    def get_all_ev(self):
        status_list = ["H", "A", "B", "C", "D", "S"]
        all_ev = ""
        for i in range(6):
            if self.ev_list[i]._ev_entry.value.get() != 0:
                all_ev += status_list[i] + str(self.ev_list[i]._ev_entry.value.get())
        return all_ev


class EvEditor(ttk.Frame):
    def on_validate_3(self, P, V):
        if P.isdigit() or P == "":
            return len(P) <= 3
        else:
            return False

    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)
        self.validate_cmd_3 = self.register(self.on_validate_3)

        self._ev_min_button = tkinter.Button(
            self, text="0", command=lambda: self.set_value(0, True)
        )
        self._ev_min_button["takefocus"] = False
        self._ev_min_button.pack(side="left")

        self._ev_count_down = tkinter.Button(
            self, text="↓", command=lambda: self.set_value(-4, False)
        )
        self._ev_count_down["takefocus"] = False
        self._ev_count_down.pack(side="left")

        self._ev_entry = ModifiedEntry(
            self,
            validate="key",
            width=4,
            validatecommand=(self.validate_cmd_3, "%P", "%V"),
        )
        self._ev_entry.insert(0, 0)
        self._ev_entry.pack(side="left")

        self._ev_count_up = tkinter.Button(
            self, text="↑", command=lambda: self.set_value(4, False)
        )
        self._ev_count_up["takefocus"] = False
        self._ev_count_up.pack(side="left")

        self._ev_max_button = tkinter.Button(
            self, text="252", command=lambda: self.set_value(252, True)
        )
        self._ev_max_button["takefocus"] = False
        self._ev_max_button.pack(side="left")

    def set_value(self, value: int, override: bool):
        if override:
            self._ev_entry.delete(0, tkinter.END)
            self._ev_entry.value.set(value)
        else:
            increase_num = self._ev_entry.value.get() + value
            if 0 <= increase_num <= 252:
                self._ev_entry.delete(0, tkinter.END)
                self._ev_entry.value.set(increase_num)

    def setCallback(self, func):
        self._ev_entry.bind("<<TextModified>>", func)


class IvEditors(ttk.Frame):
    def __init__(self, master, callback, **kwargs):
        super().__init__(master=master, **kwargs)
        self.iv_list: list[IvEditor] = []
        for _i in range(6):
            self.iv_editor = IvEditor(self)
            self.iv_editor.setCallback(callback)
            self.iv_editor.pack(pady=5)
            self.iv_list.append(self.iv_editor)

    def init_all_value(self):
        for i in range(6):
            self.iv_list[i]._iv_entry.value.set(31)
            self.iv_list[i]._iv_entry.delete(0, tkinter.END)
            self.iv_list[i]._iv_entry.insert(0, 31)

    def get_all_iv(self):
        status_list = ["H", "A", "B", "C", "D", "S"]
        all_iv = ""
        for i in range(6):
            if self.iv_list[i]._iv_entry.value.get() != 31:
                all_iv += status_list[i] + str(self.iv_list[i]._iv_entry.value.get())
        return all_iv


class IvEditor(ttk.Frame):
    def on_validate_2(self, P, V):
        if P.isdigit() or P == "":
            return len(P) <= 2
        else:
            return False

    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)
        self.validate_cmd_2 = self.register(self.on_validate_2)

        self._iv_min_button = tkinter.Button(
            self, text="0", command=lambda: self.set_value(0, True)
        )
        self._iv_min_button["takefocus"] = False
        self._iv_min_button.pack(side="left")

        self._iv_count_down = tkinter.Button(
            self, text="↓", command=lambda: self.set_value(-1, False)
        )
        self._iv_count_down["takefocus"] = False
        self._iv_count_down.pack(side="left")

        self._iv_entry = ModifiedEntry(
            self,
            validate="key",
            width=4,
            validatecommand=(self.validate_cmd_2, "%P", "%V"),
        )
        self._iv_entry.insert(0, 31)
        self._iv_entry.pack(side="left")

        self._iv_count_up = tkinter.Button(
            self, text="↑", command=lambda: self.set_value(1, False)
        )
        self._iv_count_up["takefocus"] = False
        self._iv_count_up.pack(side="left")

        self._iv_max_button = tkinter.Button(
            self, text="31", command=lambda: self.set_value(31, True)
        )
        self._iv_max_button["takefocus"] = False
        self._iv_max_button.pack(side="left")

    def set_value(self, value: int, override: bool):
        if override:
            self._iv_entry.delete(0, tkinter.END)
            self._iv_entry.value.set(value)
        else:
            increase_num = self._iv_entry.value.get() + value
            if 0 <= increase_num <= 31:
                self._iv_entry.delete(0, tkinter.END)
                self._iv_entry.value.set(increase_num)

    def setCallback(self, func):
        self._iv_entry.bind("<<TextModified>>", func)


class PokemonInputDialog(tkinter.Toplevel):
    def __init__(
        self, pokemon: Pokemon, title: str = "", width: int = 400, height: int = 300
    ):
        super().__init__()
        self.title("ポケモン入力")
        self.pokemon = pokemon

        notebook = ttk.Notebook(self)

        # タブの作成
        self.home_frame = PokemonFromHomeDialog(master=notebook, parent=self)
        self.box_frame = PokemonFromBoxDialog(master=notebook, parent=self)

        # notebookにタブを追加
        notebook.add(self.home_frame, text="HOMEから")
        notebook.add(self.box_frame, text="BOXから")
        notebook.pack(expand=True, fill="both", padx=10, pady=10)

    def open(self, location=tuple[int, int]):
        self.grab_set()
        self.home_frame._name_input.focus_set()
        self.geometry("+{0}+{1}".format(location[0], location[1]))


class PokemonFromHomeDialog(ttk.Frame):
    def __init__(self, master, parent, **kwargs):
        super().__init__(master, **kwargs)

        self.parent: PokemonInputDialog = parent

        self._labelframe = ttk.LabelFrame(self, text="ポケモン名を入力")
        self._labelframe.grid(row=0, column=0, columnspan=6)

        self._name_input: AutoCompleteCombobox = AutoCompleteCombobox.pokemons(
            self._labelframe
        )
        self._name_input.bind("<<submit>>", self.on_input_name)
        self._name_input.grid(row=0, column=0)

        with open("stats/ranking.txt", "r", encoding="utf-8") as ranking_json:
            lines = ranking_json.readlines()
            list = [line.rstrip("\n") for line in lines]

        pokes_frame = ttk.Frame(self, padding=10)
        for i in range(100):
            row = int(i / 10)
            column = i % 10

            no = list[i].split("-")[0].lstrip("0")
            form = (
                list[i].split("-")[1].lstrip("0")
                if list[i].split("-")[1].lstrip("0") != ""
                else 0
            )
            pid = f"{no.lstrip('0')}-{form}"

            poke_frame = ttk.Frame(pokes_frame, padding=5)
            self._pokemon_icon = MyLabel(
                poke_frame,
                size=(30, 30),
                padding=0,
            )
            self._pokemon_icon.set_pokemon_icon(pid)
            self._pokemon_icon.bind(
                "<Button-1>", lambda _, pokemon=pid: self.on_choose_pokemons(pokemon)
            )
            self._pokemon_icon.grid(row=0, column=0)
            self._pokemon_label = ttk.Label(
                poke_frame, text=DB_pokemon.get_pokemon_name_by_pid(pid)
            )
            self._pokemon_label.grid(row=0, column=1)
            self._pokemon_label.bind(
                "<Button-1>", lambda _, pokemon=pid: self.on_choose_pokemons(pokemon)
            )

            poke_frame.bind(
                "<Button-1>", lambda _, pokemon=pid: self.on_choose_pokemons(pokemon)
            )
            poke_frame.grid(row=row, column=column, padx=20, pady=20)

        pokes_frame.grid(row=1, column=0, sticky=N + E + W + S)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def on_input_name(self, *args):
        pokemon_name = self._name_input.get()
        self.parent.pokemon = Pokemon.by_name(pokemon_name, default=True)
        self.parent.destroy()

    def on_choose_pokemons(self, pid: str):
        self.parent.pokemon = Pokemon.by_pid(pid, default=True)
        self.parent.destroy()


class PokemonFromBoxDialog(ttk.Frame):
    def __init__(self, master, parent, **kwargs):
        super().__init__(master, **kwargs)

        self.parent: PokemonInputDialog = parent
        self.pokemon = self.parent.pokemon

        self.current_page_num = tkinter.IntVar()
        self.all_page_num = tkinter.IntVar()

        self.pokes_frame = ttk.Frame(self, padding=10)
        self.top_frame = ttk.Frame(self, padding=10)
        self.top_frame.pack(side="top", padx=20, fill="x")
        self.top_left_frame = ttk.Frame(self.top_frame)
        self.top_left_frame.pack(side="left", padx=20, fill="x", expand=True)
        self.top_right_frame = ttk.Frame(self.top_frame)
        self.top_right_frame.pack(side="right", padx=20, fill="x", expand=True)

        self._labelframe = ttk.LabelFrame(self.top_left_frame, text="ポケモン名を入力")
        self._labelframe.pack(side="left", padx=20, expand=True)
        self._name_input: AutoCompleteCombobox = AutoCompleteCombobox.pokemons(
            self._labelframe
        )
        if self.parent.pokemon.no != -1:
            self._name_input.set(self.parent.pokemon.name)
        self._name_input.bind("<<submit>>", self.on_input_name)
        self._name_input.pack(side="left")

        proceed_button = MyButton(
            self.top_right_frame,
            text="次へ",
            command=self.click_paging_right,
        )
        proceed_button.pack(side="right", padx=20)
        all_page_num = MyLabel(
            self.top_right_frame,
            textvariable=self.all_page_num,
        )
        all_page_num.pack(side="right", padx=20)
        slash_label = MyLabel(
            self.top_right_frame,
            text=" / ",
        )
        slash_label.pack(side="right", padx=20)
        current_page_num = MyLabel(
            self.top_right_frame,
            textvariable=self.current_page_num,
        )
        current_page_num.pack(side="right", padx=20)
        back_button = MyButton(
            self.top_right_frame,
            text="前へ",
            command=self.click_paging_left,
        )
        back_button.pack(side="right", padx=20)
        clear_button = MyButton(
            self.top_right_frame,
            text="リセット",
            command=self.reset,
        )
        clear_button.pack(side="right", padx=20)

        self.update_box_list()
        self.set_pokemon_list()

    def update_box_list(self):
        self.box_data = self.read_csv("party\\csv\\box.csv")
        self.box_data.reverse()
        if self.pokemon.no != -1:
            box = [
                pokemon for pokemon in self.box_data if pokemon[0] == self.pokemon.name
            ]
            if len(box) > 0:
                self.box_data = box
        self.current_page_num.set(1)
        self.all_page_num.set((len(self.box_data) // 15) + 1)

    def set_pokemon_list(self):
        self.pokes_frame.destroy()
        self.pokes_frame = ttk.Frame(self, padding=10)
        column_title = [
            "名前",
            "個体値",
            "努力値",
            "性格",
            "持ち物",
            "特性",
            "テラス",
        ]

        for i, value in enumerate(column_title):
            label = MyLabel(self.pokes_frame, text=value)
            label.grid(row=0, column=i + 1, padx=15, pady=10)

        label = MyLabel(self.pokes_frame, text="技")
        label.grid(row=0, column=8, columnspan=4)

        for i, row in enumerate(
            self.box_data[
                (self.current_page_num.get() - 1) * 15 : (
                    (self.current_page_num.get() - 1) * 15
                )
                + 15
            ],
            start=(self.current_page_num.get() - 1) * 15,
        ):
            choose_button = MyButton(
                master=self.pokes_frame,
                image=images.get_menu_icon("edit"),
                command=lambda idx=i: self.on_choose_pokemons(idx),
            )
            choose_button.grid(row=i + 1, column=0, padx=15, pady=10)
            for j, value in enumerate(row):
                if j != 7:
                    label = MyLabel(self.pokes_frame, text=value)
                    label.grid(
                        row=i + 1,
                        column=j + 1 if j < 7 else j,
                        padx=15,
                        pady=10,
                    )
                else:
                    memo_button = MyButton(
                        master=self.pokes_frame,
                        image=images.get_menu_icon("load"),
                        command=lambda memo=value: self.show_pokemon_memo(memo),
                    )
                    memo_button.grid(row=i + 1, column=12, padx=15, pady=10)

        self.pokes_frame.pack(fill="both", expand=True, side="top")

    def read_csv(self, file_path):
        rows = []
        with open(file_path, mode="r", newline="") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                rows.append(row)
        return rows

    def on_input_name(self, *args):
        pokemon_name = self._name_input.get()
        self.pokemon = Pokemon.by_name(pokemon_name, default=True)
        self.update_box_list()
        self.set_pokemon_list()

    def show_pokemon_memo(self, memo: str):
        dialog = PokemonMemoLabelDialog()
        dialog.open(memo, location=(self.winfo_x(), self.winfo_y()))
        self.wait_window(dialog)

    def on_choose_pokemons(self, index: int):
        pokemon: Pokemon = Pokemon.by_name(self.box_data[index][0])
        pokemon.set_load_data(self.box_data[index], True)
        self.parent.pokemon = pokemon
        self.parent.destroy()

    def reset(self):
        self.pokemon = Pokemon()
        self._name_input.set("")
        self.update_box_list()
        self.set_pokemon_list()

    def click_paging_left(self):
        if self.current_page_num.get() > 1:
            self.current_page_num.set(self.current_page_num.get() - 1)
            self.set_pokemon_list()

    def click_paging_right(self):
        if self.current_page_num.get() < self.all_page_num.get():
            self.current_page_num.set(self.current_page_num.get() + 1)
            self.set_pokemon_list()


class PokemonMemoInputDialog(tkinter.Toplevel):
    def __init__(self, title: str = "", width: int = 400, height: int = 300):
        super().__init__()
        self.title("メモ入力")
        self.memo = ""

        # ウィジェットの配置
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.memo_input = ScrolledText(main_frame, height=3, width=60, padx=3, pady=3)
        self.memo_input.pack(padx=10, pady=10)

        self.button = MyButton(main_frame, text="決定", command=self.close)
        self.button.pack(padx=10, pady=10)

    def open(self, memo: str, location=tuple[int, int]):
        self.grab_set()
        self.memo_input.insert(tkinter.END, memo)
        self.memo_input.focus_set()
        self.geometry("+{0}+{1}".format(location[0], location[1]))

    def close(self, *args):
        self.memo = self.memo_input.get("1.0", "end-1c")
        self.destroy()


class TableNumInputDialog(tkinter.Toplevel):
    def on_validate_3(self, P, V):
        if P.isdigit() or P == "":
            return len(P) <= 3
        else:
            return False

    def __init__(self, title: str = "", width: int = 400, height: int = 300):
        super().__init__()
        self.validate_cmd_3 = self.register(self.on_validate_3)
        self.title("星取表作成")
        self.no = 30

        # ウィジェットの配置
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._labelframe = ttk.LabelFrame(
            main_frame, text="上位何体までの星取表を作成しますか？"
        )
        self._labelframe.pack()

        self._no_input = ModifiedEntry(
            self._labelframe,
            validate="key",
            width=4,
            validatecommand=(self.validate_cmd_3, "%P", "%V"),
        )
        self._no_input.insert(0, 3)
        self._no_input.pack(padx=10, pady=10)

        self.button = MyButton(self._labelframe, text="決定", command=self.on_input_no)
        self.button.pack(padx=10, pady=10)

    def open(self, location=tuple[int, int]):
        self.grab_set()
        self._no_input.focus_set()
        self.geometry("+{0}+{1}".format(location[0], location[1]))

    def on_input_no(self, *args):
        self.no = (
            int(self._no_input.get())
            if int(self._no_input.get()) <= 150 and int(self._no_input.get()) >= 10
            else 30
        )
        self.destroy()
