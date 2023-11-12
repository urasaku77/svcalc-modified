from tkinter import N, E, W, S
from tkinter import ttk
import tkinter

from component import images
from component.button import TypeButton, MyButton
from component.combobox import AutoCompleteCombobox
from component.label import MyLabel
from pokedata.const import Types
from pokedata.pokemon import Pokemon
from pokedata.stats import Stats, StatsKey


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

        self._name_input: AutoCompleteCombobox = AutoCompleteCombobox.pokemons(self._labelframe)
        self._name_input.bind("<<submit>>", self.on_input_name)
        self._name_input.grid(row=0, column=0)

        for i in range(6):
            radio = ttk.Radiobutton(main_frame, value=i,
                                    variable=self._selected,
                                    command=self.on_push_radiobutton)
            radio.grid(row=1, column=i)
            self._radio_buttons.append(radio)

            label = MyLabel(main_frame, size=(40, 40), relief=tkinter.RAISED, padding=0)
            label.grid(row=2, column=i)
            self._labels.append(label)

        self._close_button = ttk.Button(main_frame, text="決定",
                                        command=lambda: self.destroy())
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
            button = TypeButton(self, type_=t,
                                command=lambda x=t: self.on_push_button(x))
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


# ランク編集ダイアログ
class RankSelectDialog(tkinter.Toplevel):
    def __init__(self, title: str = "ランク変更", width: int = 400, height: int = 300):
        super().__init__()
        self.title(title)
        self._rank: Stats = Stats(0)
        self._spinbox_dict = {}

        for i, statskey in enumerate([x for x in StatsKey if x != StatsKey.H]):
            label = MyLabel(self, text=statskey.name, anchor=tkinter.CENTER)
            label.grid(column=i, row=0, padx=2, sticky=W+E)

            spin = ttk.Spinbox(self,
                               from_=-6,
                               to=6,
                               increment=1,
                               state="readonly",
                               width=3,
                               command=lambda key=statskey: self.on_push_spin(key))
            spin.grid(column=i, row=1, padx=2)
            self._spinbox_dict[statskey] = spin

        self.set_rank(self._rank)

        btn = MyButton(
            self, text="決定", width=4,
            command=lambda: self.on_push_button())
        btn.grid(column=6, row=1, padx=2)

    @property
    def rank(self) -> Stats:
        return self._rank

    def set_rank(self, rank: Stats):
        for key in [x for x in StatsKey if x != StatsKey.H]:
            self.set_rank_value(key, rank[key])

    def set_rank_value(self, key: StatsKey, value: int):
        self._rank[key] = value
        self._spinbox_dict[key].select_clear()
        if value > 0:
            self._spinbox_dict[key].set("+" + str(value))
            self._spinbox_dict[key]["foreground"] = "coral"
        else:
            self._spinbox_dict[key].set(value)
            self._spinbox_dict[key]["foreground"] = "steel blue" if value < 0 else ""

    def open(self, location=tuple[int, int]):
        self.grab_set()
        self.focus_set()
        self.geometry("+{0}+{1}".format(location[0], location[1]))

    def on_push_spin(self, key: StatsKey):
        self.set_rank_value(key, int(self._spinbox_dict[key].get()))

    def on_push_button(self):
        self.destroy()
