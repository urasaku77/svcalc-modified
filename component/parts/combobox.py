import tkinter as tk
from tkinter import Event, ttk

import jaconv


class MyCombobox(ttk.Combobox):
    EVENT_SUBMIT = "<<submit>>"

    def __init__(self, master=None, **kwargs):
        ttk.Combobox.__init__(self, master, justify="center", **kwargs)
        # self["font"] = (const.FONT_FAMILY, 12)


# オートコンプリート機能コンボボックス
class AutoCompleteCombobox(MyCombobox):
    def __init__(self, master, suggest_values=None, **kwargs):
        MyCombobox.__init__(self, master, **kwargs)
        self._suggest_values = suggest_values
        self.bind("<Return>", self.on_enter)
        self.bind("<<ComboboxSelected>>", self.on_selected)

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
        from database.pokemon import DB_pokemon

        return AutoCompleteCombobox(
            master=master,
            suggest_values=DB_pokemon.get_pokemon_namelist(form=True),
            **kwargs,
        )


# 技名オートコンプリート機能コンボボックス
class WazaNameCombobox(AutoCompleteCombobox):
    def __init__(self, master, **kwargs):
        from database.pokemon import DB_pokemon

        super().__init__(
            master=master, suggest_values=DB_pokemon.get_waza_namedict(), **kwargs
        )

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


# 入力変更監視フォーム
class ModifiedEntry(tk.Entry):
    def __init__(self, *args, **kwargs):
        # Entry自体の初期化は元のクラスと同様。
        tk.Entry.__init__(self, *args, **kwargs)
        self.value = tk.IntVar(value=0)
        # traceメソッドでStringVarの中身を監視。変更があったらvar_changedをコールバック
        self.value.trace_add("write", self.var_changed)
        # EntryとStringVarを紐づけ。
        self.configure(textvariable=self.value)
        # フォーカス時に全選択
        self.bind("<FocusIn>", self.select_all)
        # フォーカスされていたら解除
        self.bind("<Button-1>", self.clear_selection)
        # Enterを押したら次のウィジェットへ
        self.bind("<Return>", self.focus_next_widget)

    # argsにはtrace発生元のVarの_nameが入っている
    # argsのnameと内包StringVarの_nameが一致したらイベントを発生させる。
    def var_changed(self, *args):
        if args[0] == self.value._name:
            s = self.value.get()
            self.event_generate("<<TextModified>>")

    def select_all(self, event: Event, *args):
        event.widget.select_range(0, tk.END)
        event.widget.icursor(tk.END)

    def clear_selection(self, event: Event, *args):
        event.widget.icursor(tk.END)
        event.widget.select_clear()

    def focus_next_widget(self, event: Event, *args):
        event.widget.tk_focusNext().focus()
        return "break"
