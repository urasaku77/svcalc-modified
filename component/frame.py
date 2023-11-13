from __future__ import annotations
import tkinter
from tkinter import ttk, N, E, W, S
from typing import TYPE_CHECKING
import webbrowser

from component import const, images
from component.button import MyButton, TypeIconButton
from component.combobox import MyCombobox, WazaNameCombobox
from component.const import *
from component.label import MyLabel
from pokedata.calc import DamageCalcResult
from pokedata.const import Types, ABILITY_VALUES, Walls
from pokedata.pokemon import Pokemon
from pokedata.waza import WazaBase

if TYPE_CHECKING:
    from stage import Stage


# 選択状態ポケモン表示フレーム
class ActivePokemonFrame(ttk.LabelFrame):

    def __init__(self, master, player: int, **kwargs):
        super().__init__(master,
                         padding=5,
                         **kwargs)
        self._player: int = player
        self._stage: Stage | None = None
        self.columnconfigure(2, weight=1)

        # ウィジェットの配置
        left_frame = ttk.Frame(self)
        left_frame.grid(column=0, row=0, rowspan=4)

        self._pokemon_icon = MyButton(left_frame, size=(60, 60), padding=0, command=self.on_push_pokemon_button)
        self._pokemon_icon.grid(column=0, row=0)

        teras_frame = ttk.LabelFrame(left_frame, text="テラス", labelanchor="n")
        teras_frame.grid(column=0, row=1, sticky=W+E)
        teras_frame.columnconfigure(0, weight=1)

        self._teras_button = TypeIconButton(teras_frame,
                                            types=Types.なし,
                                            command=self.on_push_terasbutton)
        self._teras_button.grid(column=0, row=0, sticky=W + E)

        for i, text in enumerate(["ステータス", "持ち物", "特性", "ランク"]):
            label = MyLabel(self, text=text)
            label.grid(column=1, row=i, padx=5, pady=5)
        label = MyLabel(self, text="壁")
        label.grid(column=3, row=0, padx=5, pady=5)

        self._status_combobox = MyCombobox(
            self, values=DORYOKU_COMBOBOX_VALUES, width=24)
        self._status_combobox.bind("<<ComboboxSelected>>", self.on_select_doryoku)
        self._status_combobox.grid(column=2, row=0, sticky=W+E)

        self._item_combobox = MyCombobox(self, values=ITEM_COMBOBOX_VALUES)
        self._item_combobox.bind("<<ComboboxSelected>>", self.on_select_item)
        self._item_combobox.bind("<Return>", self.on_select_item)
        self._item_combobox.grid(column=2, row=1, sticky=W+E)

        self._ability_combobox = MyCombobox(self, width=16)
        self._ability_combobox.bind("<<ComboboxSelected>>", self.on_select_ability)
        self._ability_combobox.grid(column=2, row=2, sticky=W+E)

        self._ability_value_combobox = MyCombobox(self, width=4, state="disable")
        self._ability_value_combobox.bind(
            "<<ComboboxSelected>>", self.on_select_ability_value)
        self._ability_value_combobox.grid(column=3, row=2)
        
        self._wall_combobox = MyCombobox(self, width=16, values=WALL_COMBOBOX_VALUES)
        self._wall_combobox.bind("<<ComboboxSelected>>", self.on_select_wall)
        self._wall_combobox.grid(column=4, row=0, sticky=W)

        self.burned = tkinter.BooleanVar()
        self.burned_check = tkinter.Checkbutton(self, text='やけど', variable=self.burned, command=self.change_burned)
        self.burned.set(False)
        self.burned_check.grid(column=3, row=1, sticky=W)
        
        self.critical = tkinter.BooleanVar()
        self.critical_check = tkinter.Checkbutton(self, text='きゅうしょ', variable=self.critical, command=self.change_critical)
        self.critical.set(False)
        self.critical_check.grid(column=4, row=1, sticky=W)
        
        self.charging = tkinter.BooleanVar()
        self.charging_check = tkinter.Checkbutton(self, text='じゅうでん', variable=self.charging, command=self.change_charging)
        self.charging.set(False)
        self.charging_check.grid(column=4, row=2, sticky=W)

        self._rank_label = MyLabel(self, anchor=tkinter.W)
        self._rank_label.grid(column=2, row=3, sticky=W+E)

        _rank_menu_frame = ttk.Frame(self)
        _rank_menu_frame.grid(column=3, row=3)

        # ランク編集ボタン
        edit_btn = MyButton(
            master=_rank_menu_frame,
            image=images.get_menu_icon("edit"), padding=0,
            command=lambda: self.on_push_rankedit_button()
        )
        edit_btn.grid(column=0, row=0)

        # ランククリアボタン
        clear_btn = MyButton(
            master=_rank_menu_frame,
            image=images.get_menu_icon("trush"), padding=0,
            command=lambda: self.on_push_rankclear_button()
        )
        clear_btn.grid(column=1, row=0)

    def set_pokemon(self, poke: Pokemon):
        self._pokemon_icon.set_pokemon_icon(pid=poke.pid, size=(60, 60))
        self._status_combobox.set(poke.status_text)
        self._item_combobox.set(poke.item)
        self._ability_combobox["values"] = poke.abilities
        self._ability_combobox.set(poke.ability)
        self.set_ability_values(poke.ability)
        self._ability_value_combobox.set(poke.ability_value)
        self._teras_button.set_type(poke.battle_terastype)
        self._rank_label["text"] = poke.rank.rank_text

    def set_stage(self, stage: Stage):
        self._stage = stage

    def set_ability_values(self, ability: str):
        if len(ability) > 0:
            for k, v in ABILITY_VALUES.items():
                if ability in k:
                    self._ability_value_combobox["values"] = v
                    self._ability_value_combobox["state"] = "normal"
                    self._ability_value_combobox.set(v[0])
                    return
        self._ability_value_combobox["state"] = "disable"
        self._ability_value_combobox.set("")

    def change_burned(self):
        self._stage.set_value_to_active_pokemon(player=self._player,ailment=self.burned.get())

    def change_critical(self):
        self._stage.set_value_to_active_pokemon(player=self._player,critical=self.critical.get())
        
    def change_charging(self):
        self._stage.set_value_to_active_pokemon(player=self._player,charging=self.charging.get())

    def on_select_doryoku(self, *_args):
        values = self._status_combobox.get().split(" ")
        self._status_combobox.delete(0, 30)
        self._stage.set_value_to_active_pokemon(
            player=self._player,
            seikaku=values[0],
            doryoku_text=values[1]
        )

    def on_select_item(self, *_args):
        self._stage.set_value_to_active_pokemon(
            player=self._player,
            item=self._item_combobox.get()
        )

    def on_select_ability(self, *_args):
        ability = self._ability_combobox.get()
        self._stage.set_value_to_active_pokemon(
            player=self._player,
            ability=ability
        )
        self.set_ability_values(ability)

    def on_select_ability_value(self, *_args):
        self._stage.set_value_to_active_pokemon(
            player=self._player,
            ability_value=self._ability_value_combobox.get()
        )
    
    def on_select_wall(self, *_args):
        for wall in Walls:
            if wall.name == self._wall_combobox.get():
                self._stage.set_value_to_active_pokemon(
                    player=self._player,
                    wall=wall
                )

    def on_push_pokemon_button(self):
        self._stage.set_chosen(self._player)

    def on_push_terasbutton(self, *_args):
        self._stage.select_terastype(self._player)

    def on_push_rankedit_button(self):
        self._stage.edit_rank(self._player)

    def on_push_rankclear_button(self):
        self._stage.clear_rank(self._player)


# 技・ダメージ表示リストフレーム
class WazaDamageListFrame(ttk.LabelFrame):

    def __init__(self, master, index: int, **kwargs):
        super().__init__(master, **kwargs, padding=5)
        self._index = index
        self._stage: Stage | None = None
        self.columnconfigure(2, weight=1)

        self._cbx_list: list[WazaNameCombobox] = []
        self._btn_list: list[MyButton] = []
        self._dmgframe_list = []

        for i in range(8):
            cbx = WazaNameCombobox(self, width=16)
            cbx.grid(column=0, row=i)
            cbx.bind("<<submit>>", lambda _, idx=i: self.on_submit_waza(idx))
            self._cbx_list.append(cbx)

            btn = MyButton(
                self, width=4, command=lambda idx=i: self.on_push_waza_button(idx))
            btn.grid(column=1, row=i)
            self._btn_list.append(btn)

            dmgframe = DamageDispFrame(self)
            dmgframe.grid(column=2, row=i, sticky=W+E)
            self._dmgframe_list.append(dmgframe)

    def set_stage(self, stage: Stage):
        self._stage = stage

    def on_submit_waza(self, index: int):
        waza = self._cbx_list[index].get()
        self._stage.set_value_to_active_pokemon(self._index, waza=(index, waza))

    def on_push_waza_button(self, index: int):
        self._stage.set_value_to_active_pokemon(self._index, waza_effect=index)

    def set_waza_info(self, lst: list[WazaBase]):
        for i in range(8):
            wazabase = lst[i]
            if wazabase is not None:
                self._cbx_list[i].set(wazabase.name)
                match wazabase.type:
                    case wazabase.TYPE_ADD_POWER | wazabase.TYPE_MULTI_HIT | wazabase.TYPE_POWER_HOSEI:
                        self._btn_list[i].text = "x" + str(wazabase.value)
                    case wazabase.TYPE_SELF_BUFF:
                        self._btn_list[i].text = "＋"
                    case _:
                        self._btn_list[i].text = ""
            else:
                self._cbx_list[i].set("")
                self._btn_list[i].text = ""

    def set_damages(self, lst: list[DamageCalcResult]):
        for i in range(min(len(lst), 8)):
            result = lst[i]
            self._dmgframe_list[i].set_calc_result(result)


# ダメージ表示
class DamageDispFrame(ttk.Frame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.dmg1_label = MyLabel(self)
        self.dmg1_label.grid(column=0, row=0, sticky=W + E)

        self.dmg2_label = MyLabel(self, font=(const.FONT_FAMILY, 8))
        self.dmg2_label.grid(column=1, row=0, sticky=W + E)

        self.hpbar = HpBarFrame(self)
        self.hpbar.grid(column=0, row=1, columnspan=2, sticky=W + E)

    def set_calc_result(self, result: DamageCalcResult):
        if result is not None and result.is_damage:
            self.dmg1_label["text"] = result.damage_text
            self.dmg2_label["text"] = result.damage_per_text
            self.hpbar.set_damage(
                mindmg=result.min_damage_per, maxdmg=result.max_damage_per)
        else:
            self.dmg1_label["text"] = ""
            self.dmg2_label["text"] = ""
            self.hpbar.clear()


# HPバー表示フレーム
class HpBarFrame(tkinter.Frame):

    def __init__(self, master, **kwargs):
        super().__init__(master,
                         height=5,
                         background="#c8c8c8",
                         **kwargs)
        self.propagate(False)

        self.bar_1 = tkinter.Frame(self, width=0, height=5, background="#323232")
        self.bar_1.propagate(False)
        self.bar_1.grid(column=0, row=0, sticky=N + S)

        self.bar_2 = tkinter.Frame(self, width=0, height=5, background="#323232")
        self.bar_2.propagate(False)
        self.bar_2.grid(column=1, row=0, sticky=N + S)

    def set_damage(self, mindmg: float, maxdmg: float):
        if maxdmg >= 80:
            colors = ("#ff3232", "#a43e3e")
        elif maxdmg >= 50:
            colors = ("#fbc02d", "#907329")
        else:
            colors = ("#0eda0e", "#25a425")

        bar_width = self.winfo_width()
        if maxdmg >= 100:
            width_1 = 0
            if mindmg >= 100:
                width_2 = 0
            else:
                width_2 = int(bar_width * (100 - mindmg) / 100)
        else:
            width_1 = int(bar_width * (100 - maxdmg) / 100)
            width_2 = int(bar_width * (maxdmg - mindmg) / 100)

        self.bar_1["width"] = width_1
        self.bar_1["background"] = colors[0]
        self.bar_2["width"] = width_2
        self.bar_2["background"] = colors[1]

    def clear(self):
        self.bar_1["width"] = 0
        self.bar_2["width"] = 0


# パーティ表示フレーム
class PartyFrame(ttk.LabelFrame):

    def __init__(self, master, player: int, **kwargs):
        super().__init__(master, **kwargs)
        self._player: int = player
        self._stage: Stage | None = None
        self._button_list: list[MyButton] = []

        # ポケモン表示ボタン
        for i in range(6):
            btn = MyButton(
                self, size=(30, 30),
                padding=0,
                command=lambda idx=i: self.on_push_pokemon_button(idx)
            )
            btn.grid(column=i, row=0, sticky=W)
            self._button_list.append(btn)

        # 編集ボタン
        edit_btn = MyButton(
            master=self, image=images.get_menu_icon("edit"), padding=0,
            command=lambda: self.on_push_edit_button()
        )
        edit_btn.grid(column=6, row=0, sticky=E)

        # パーティ読み込みボタン
        if player == 0:
            load_btn = MyButton(
                master=self, image=images.get_menu_icon("load"), padding=0,
                command=lambda: self.on_push_load_button()
            )
            load_btn.grid(column=7, row=0, sticky=E)
        # パーティクリアボタン
        elif player == 1:
            load_btn = MyButton(
                master=self, image=images.get_menu_icon("trush"), padding=0,
                command=lambda: self.on_push_clear_button()
            )
            load_btn.grid(column=7, row=0, sticky=E)

    def set_stage(self, stage: Stage):
        self._stage = stage

    def set_party(self, party: list[Pokemon]):
        for i, pokemon in enumerate(party):
            if pokemon.is_empty is False:
                self._button_list[i].set_pokemon_icon(pokemon.pid, size=(30, 30))
            else:
                self._button_list[i].set_image(images.get_blank_image(size=(30, 30)))

    def on_push_pokemon_button(self, index: int):
        self._stage.set_active_pokemon_from_index(player=self._player, index=index)
        self._stage.set_info(self._player)

    def on_push_edit_button(self):
        self._stage.edit_party(self._player)

    def on_push_load_button(self):
        self._stage.load_party(self._player)

    def on_push_clear_button(self):
        self._stage.clear_party(self._player)

# 選出表示フレーム
class ChosenFrame(ttk.LabelFrame):

    def __init__(self, master, player: int, **kwargs):
        super().__init__(master, **kwargs)
        self._player: int = player
        self._stage: Stage | None = None
        self._button_list: list[MyButton] = []

        # ポケモン表示ボタン
        for i in range(3):
            btn = MyButton(
                self, size=(30, 30),
                padding=0,
                command=lambda idx=i: self.on_push_pokemon_button(idx)
            )
            btn.grid(column=i, row=0, sticky=W)
            self._button_list.append(btn)

        # 選出クリアボタン
        load_btn = MyButton(
            master=self, image=images.get_menu_icon("trush"), padding=0,
            command=lambda: self.on_push_clear_button()
        )
        load_btn.grid(column=7, row=0, sticky=E)

    def set_stage(self, stage: Stage):
        self._stage = stage

    def set_chosen(self, pokemon: Pokemon, index: int):
        if pokemon.is_empty is False:
            self._button_list[index].set_pokemon_icon(pokemon.pid, size=(30, 30))
        else:
            self._button_list[index].set_image(images.get_blank_image(size=(30, 30)))

    def on_push_pokemon_button(self, index: int):
        self._stage.delete_chosen(self._player, index)

    def on_push_clear_button(self):
        self._stage.clear_chosen(self._player)

class InfoFrame(ttk.LabelFrame):

    def __init__(self, master, player: int, **kwargs):
        super().__init__(master, **kwargs)
        self._player: int = player
        self._no: int = 0
        global img
        img = [[ tkinter.PhotoImage(file=Types.なし.icon).subsample(3,3) ]*2, [ tkinter.PhotoImage(file=Types.なし.icon).subsample(3,3) ]*2]

        self.name = tkinter.StringVar()
        self.name.set("")
        self.name_text = ttk.Label(self, textvariable=self.name, font=(const.FONT_FAMILY, 12, "italic"),)
        self.name_text.grid(column=0, row=0, columnspan=4)
        
        self.type1_img = img[self._player][0]
        self.type1_icon = ttk.Label(self, image=self.type1_img)
        self.type1_icon.grid(column=5, row=0, columnspan=3)
        
        self.type2_img = img[self._player][1]
        self.type2_icon = ttk.Label(self, image=self.type2_img)
        self.type2_icon.grid(column=8, row=0, columnspan=3)

        self.h_label = ttk.Label(self, text=" H ", font=(const.FONT_FAMILY, 15))
        self.h_label.grid(column=0, row=1)
        self.h = tkinter.StringVar()
        self.h.set("")
        self.h_text = ttk.Label(self, textvariable=self.h, font=(const.FONT_FAMILY, 15, "bold"))
        self.h_text.grid(column=1, row=1)

        self.a_label = ttk.Label(self, text=" A ", font=(const.FONT_FAMILY, 15))
        self.a_label.grid(column=2, row=1)
        self.a = tkinter.StringVar()
        self.a.set("")
        self.a_text = ttk.Label(self, textvariable=self.a, font=(const.FONT_FAMILY, 15, "bold"))
        self.a_text.grid(column=3, row=1)

        self.b_label = ttk.Label(self, text=" B ", font=(const.FONT_FAMILY, 15))
        self.b_label.grid(column=4, row=1)
        self.b = tkinter.StringVar()
        self.b.set("")
        self.b_text = ttk.Label(self, textvariable=self.b, font=(const.FONT_FAMILY, 15, "bold"))
        self.b_text.grid(column=5, row=1)

        self.c_label = ttk.Label(self, text=" C ", font=(const.FONT_FAMILY, 15))
        self.c_label.grid(column=6, row=1)
        self.c = tkinter.StringVar()
        self.c.set("")
        self.c_text = ttk.Label(self, textvariable=self.c, font=(const.FONT_FAMILY, 15, "bold"))
        self.c_text.grid(column=7, row=1)

        self.d_label = ttk.Label(self, text=" D ", font=(const.FONT_FAMILY, 15))
        self.d_label.grid(column=8, row=1)
        self.d = tkinter.StringVar()
        self.d.set("")
        self.d_text = ttk.Label(self, textvariable=self.d, font=(const.FONT_FAMILY, 15, "bold"))
        self.d_text.grid(column=9, row=1)

        self.s_label = ttk.Label(self, text=" S ", font=(const.FONT_FAMILY, 15))
        self.s_label.grid(column=10, row=1)
        self.s = tkinter.StringVar()
        self.s.set("")
        self.s_text = ttk.Label(self, textvariable=self.s, font=(const.FONT_FAMILY, 15, "bold"))
        self.s_text.grid(column=11, row=1)
        
        self.weight_label = ttk.Label(self, text=" 重さ ", font=(const.FONT_FAMILY, 11))
        self.weight_label.grid(column=0, row=2, columnspan=3)
        self.weight = tkinter.StringVar()
        self.weight.set("")
        self.weight_text = ttk.Label(self, textvariable=self.weight, font=(const.FONT_FAMILY, 11, "bold"))
        self.weight_text.grid(column=3, row=2, columnspan=4)

        self.ketaguri_label = ttk.Label(self, text=" けたぐりの威力 ", font=(const.FONT_FAMILY, 11))
        self.ketaguri_label.grid(column=11, row=2, columnspan=12)
        self.ketaguri = tkinter.StringVar()
        self.ketaguri.set("")
        self.ketaguri_text = ttk.Label(self, textvariable=self.ketaguri, font=(const.FONT_FAMILY, 11, "bold"))
        self.ketaguri_text.grid(column=24, row=2, columnspan=4)
        
        self.poketetsu_button = tkinter.Button(self, text="ポケ徹", command=self.open_poketetsu)
        self.poketetsu_button.grid(column=11, row=0, columnspan=5)

    def set_info(self, pokemon: Pokemon):
        if pokemon.is_empty is False:
            self._no=pokemon.no
            self.name.set(pokemon.name)
            img[self._player][0]=tkinter.PhotoImage(file=pokemon.type[0].icon).subsample(3,3)
            self.type1_icon.configure(image=img[self._player][0], text=pokemon.type[0].name, compound='left')
            img[self._player][1]=tkinter.PhotoImage(file=pokemon.type[1].icon if len(pokemon.type) > 1 else Types.なし.icon).subsample(3,3)
            self.type2_icon.configure(image=img[self._player][1], text=pokemon.type[1].name if len(pokemon.type) > 1 else "", compound='left')
            self.h.set(pokemon.syuzoku.H)
            self.a.set(pokemon.syuzoku.A)
            self.b.set(pokemon.syuzoku.B)
            self.c.set(pokemon.syuzoku.C)
            self.d.set(pokemon.syuzoku.D)
            self.s.set(pokemon.syuzoku.S)
            self.weight.set(str(pokemon.weight) + " kg ")
            if pokemon.weight < 10:
                self.ketaguri.set(20)
            elif pokemon.weight < 25:
                self.ketaguri.set(40)
            elif pokemon.weight < 50:
                self.ketaguri.set(60)
            elif pokemon.weight < 100:
                self.ketaguri.set(80)
            elif pokemon.weight < 200:
                self.ketaguri.set(100)
            else:
                self.ketaguri.set(120)

    def open_poketetsu(self):
        if self._no != 0:
            url = "https://yakkun.com/sv/zukan/?national_no=" + str(self._no)
            webbrowser.open(url)
