import tkinter as tk
from tkinter import ttk
import component.const as const
import jaconv


class MyCombobox(ttk.Combobox):
    EVENT_SUBMIT = "<<submit>>"

    def __init__(self, master=None, **kwargs):
        ttk.Combobox.__init__(self, master,
                              justify="center",
                              **kwargs)
        # self["font"] = (const.FONT_FAMILY, 12)


# オートコンプリート機能コンボボックス
class AutoCompleteCombobox(MyCombobox):

    def __init__(self, master, suggest_values=None, **kwargs):
        MyCombobox.__init__(self, master, **kwargs)
        self._suggest_values = suggest_values
        self.bind('<Return>', self.on_enter)
        self.bind('<<ComboboxSelected>>', self.on_selected)

    # エンター押下時
    def on_enter(self, *args):
        text: str = jaconv.alphabet2kata(self.get())
        if len(text) < 2:
            return
        suggest_list = self.filtered_list(text)
        if len(suggest_list) == 1:
            self.set(suggest_list[0])
            self.event_generate(MyCombobox.EVENT_SUBMIT)
        elif len(suggest_list) > 1:
            self["values"] = suggest_list
            self.tk.call("ttk::combobox::Post", self)

    # コンボボックスが選択された時
    def on_selected(self, *args):
        self["values"] = []
        self.event_generate(MyCombobox.EVENT_SUBMIT)

    def filtered_list(self, value) -> list[str]:
        return list(filter(lambda x: value in x, self._suggest_values))

    @staticmethod
    def pokemons(master, **kwargs):
        from data.db import DB
        return AutoCompleteCombobox(master=master,
                                    suggest_values=DB.get_pokemon_namelist(),
                                    **kwargs)


# 技名オートコンプリート機能コンボボックス
class WazaNameCombobox(AutoCompleteCombobox):

    def __init__(self, master, **kwargs):
        from data.db import DB
        super().__init__(master=master,
                         suggest_values=DB.get_waza_namedict(),
                         **kwargs)

    def filtered_list(self, value) -> list[str]:
        waza = jaconv.alphabet2kata(value)
        lst = list(filter(lambda x: waza in x[0], self._suggest_values.items()))
        return [hira for kata, hira in lst]

    # エンター押下時
    def on_enter(self, *args):
        if len(self.get()) == 0:
            self.event_generate(MyCombobox.EVENT_SUBMIT)
        else:
            super().on_enter(*args)
