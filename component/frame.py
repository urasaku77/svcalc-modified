from __future__ import annotations
import math
import time
import tkinter
from tkinter import ttk, N, E, W, S
from typing import TYPE_CHECKING
from tkinter.scrolledtext import ScrolledText
import webbrowser

from component import const, images
from component.button import MyButton, TypeIconButton
from component.combobox import MyCombobox, WazaNameCombobox
from component.const import *
from component.label import MyLabel
from pokedata.calc import DamageCalcResult
from pokedata.const import Types, ABILITY_VALUES, Walls
from pokedata.pokemon import Pokemon
from pokedata.stats import Stats, StatsKey
from pokedata.waza import WazaBase
from pokedata.exception import changeble_form_in_battle

if TYPE_CHECKING:
    from stage import Stage


# 選択状態ポケモン表示フレーム
class ActivePokemonFrame(ttk.LabelFrame):

    def __init__(self, master, player: int, **kwargs):
        super().__init__(master,
                         padding=5,
                         **kwargs)
        self._player: int = player
        self._pokemon: Pokemon = Pokemon()
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

        self._rank_label = RankFrame(self, player)
        self._rank_label.grid(column=2, row=3, columnspan=2, sticky=W+E)

        # ランククリアボタンととフォーム変更ボタン
        other_button_frame = ttk.Frame(self)
        other_button_frame.grid(column=4, row=3)
        
        self._form_button_state = tkinter.BooleanVar()
        self._form_button_state.set(False)
        self._form_button = MyButton(other_button_frame, text='フォーム', state=tkinter.DISABLED, command=self.change_form)
        self._form_button.grid(column=1, row=0, sticky=W)

        clear_btn = MyButton(
            master=other_button_frame,
            image=images.get_menu_icon("trush"), padding=0,
            command=lambda: self.on_push_rankclear_button()
        )
        clear_btn.grid(column=0, row=0)

    def set_pokemon(self, poke: Pokemon):
        self._pokemon = poke
        self._pokemon_icon.set_pokemon_icon(pid=poke.pid, size=(60, 60))
        self._status_combobox.set(poke.status_text)
        self._item_combobox.set(poke.item)
        self._ability_combobox["values"] = poke.abilities
        self._ability_combobox.set(poke.ability)
        self.set_ability_values(poke.ability)
        self._rank_label.change_all_box(poke.rank)
        self._ability_value_combobox.set(poke.ability_value)
        self._teras_button.set_type(poke.battle_terastype)
        if poke.no in changeble_form_in_battle:
            self._form_button["state"] = tkinter.NORMAL 
        else:
            self._form_button["state"] = tkinter.DISABLED 

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

    def on_push_rankclear_button(self):
        self._stage.clear_rank(self._player)
    
    def change_form(self):
        self._pokemon.form_change()
        self._pokemon_icon.set_pokemon_icon(pid=self._pokemon.pid, size=(60, 60))
        self._status_combobox.set(self._pokemon.status_text)
        self._stage.set_info(self._player)
        self._stage.calc_damage()

# ランクフレーム
class RankFrame(ttk.Frame):
    def __init__(self, master, player: int, **kwargs):
        super().__init__(master, **kwargs)
        self._rank: Stats = Stats(0)
        self._spinbox_dict = {}
        self._player = player
        self._stage: Stage | None = None

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

    def set_stage(self, stage: Stage):
        self._stage = stage

    @property
    def rank(self) -> Stats:
        return self._rank

    def set_rank(self, rank: Stats):
        self.change_all_box(rank)
        if self._stage is not None:
            self._stage.edit_rank(self._player, self._rank)

    def set_rank_value(self, key: StatsKey, value: int):
        self.change_box(key, value)
        if self._stage is not None:
            self._stage.edit_rank(self._player, self._rank)
    
    def change_box(self, key: StatsKey, value: int):
        self._rank[key] = value
        self._spinbox_dict[key].select_clear()
        if value > 0:
            self._spinbox_dict[key].set("+" + str(value))
            self._spinbox_dict[key]["foreground"] = "coral"
        else:
            self._spinbox_dict[key].set(value)
            self._spinbox_dict[key]["foreground"] = "steel blue" if value < 0 else ""
    
    def change_all_box(self, rank: Stats):
        for key in [x for x in StatsKey if x != StatsKey.H]:
            self.change_box(key, rank[key])

    def on_push_spin(self, key: StatsKey):
        self.set_rank_value(key, int(self._spinbox_dict[key].get()))


# 技・ダメージ表示リストフレーム
class WazaDamageListFrame(ttk.LabelFrame):

    def __init__(self, master, index: int, **kwargs):
        super().__init__(master, **kwargs, padding=5)
        self._index = index
        self._stage: Stage | None = None
        self.columnconfigure(3, weight=1)

        self._cbx_list: list[WazaNameCombobox] = []
        self._reg_btn_list: list[MyButton] = []
        self._lbl_list: list[MyLabel] = []
        self._btn_list: list[MyButton] = []
        self._dmgframe_list = []

        num = 5 if self._index == 0 else 10
        for i in range(num):
            if self._index == 1:
                lbl = MyLabel(self, text = u'', width=4)
                lbl.grid(column=0, row=i)
                self._lbl_list.append(lbl)
            
            cbx = WazaNameCombobox(self, width=16)
            cbx.grid(column=1, row=i)
            cbx.bind("<<submit>>", lambda _, idx=i: self.on_submit_waza(idx))
            self._cbx_list.append(cbx)

            btn = MyButton(
                self, width=4, command=lambda idx=i: self.on_push_waza_button(idx))
            btn.grid(column=2, row=i, sticky=W)
            self._btn_list.append(btn)

            dmgframe = DamageDispFrame(self)
            dmgframe.grid(column=3, row=i, sticky=W+E)
            self._dmgframe_list.append(dmgframe)

    def set_stage(self, stage: Stage):
        self._stage = stage

    def on_submit_waza(self, index: int):
        waza = self._cbx_list[index].get()
        self._stage.set_value_to_active_pokemon(self._index, waza=(index, waza))

    def on_push_waza_button(self, index: int):
        self._stage.set_value_to_active_pokemon(self._index, waza_effect=index)

    def set_waza_info(self, lst: list[WazaBase]):
        for i in range(len(self._cbx_list)):
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
    
    def set_waza_rate(self, lst: list[float]):
        for i in range(len(self._lbl_list)):
            rate = lst[i]
            if rate is not None:
                self._lbl_list[i]["text"] = str(rate)
            else:
                self._lbl_list[i]["text"] = ""

    def set_damages(self, lst: list[DamageCalcResult]):
        for i in range(len(self._dmgframe_list)):
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
        self._pokemon_list: list[str] = ["-1", "-1", "-1", "-1", "-1", "-1"]

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
                self._pokemon_list[i] = pokemon.pid
            else:
                self._button_list[i].set_image(images.get_blank_image(size=(30, 30)))
                self._pokemon_list[i] = "-1"
    
    def set_party_from_capture(self, party: list[Pokemon]):
        self._stage.load_party(1, party)
        self.set_party(party)

    def on_push_pokemon_button(self, index: int):
        self._stage.set_active_pokemon_from_index(player=self._player, index=index)
        self._stage.set_info(self._player)

    def on_push_edit_button(self):
        self._stage.edit_party(self._player)

    def on_push_load_button(self):
        self._stage.load_party(self._player)

    def on_push_clear_button(self):
        self._stage.clear_party(self._player)

    def set_first_chosen_to_active(self):
        index =self._stage.search_first_chosen()
        if index != -1:
            self.on_push_pokemon_button(index)

# 選出表示フレーム
class ChosenFrame(ttk.LabelFrame):

    def __init__(self, master, player: int, **kwargs):
        super().__init__(master, **kwargs)
        self._player: int = player
        self._stage: Stage | None = None
        self._button_list: list[MyButton] = []
        self._pokemon_list: list[str] = ["-1", "-1", "-1"]

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
            self._pokemon_list[index] = pokemon.pid
        else:
            self._button_list[index].set_image(images.get_blank_image(size=(30, 30)))
            self._pokemon_list[index] = "-1"

    def set_chosen_from_capture(self, index:list[int]):
        self._stage.set_chosen(0, index)

    def on_push_pokemon_button(self, index: int):
        self._stage.delete_chosen(self._player, index)

    def on_push_clear_button(self):
        self._stage.clear_chosen(self._player)

# 基本情報フレーム
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
        
        self.ketaguri_label = ttk.Label(self, text=" けたぐりの威力： ", font=(const.FONT_FAMILY, 11))
        self.ketaguri_label.grid(column=0, row=2, columnspan=7, sticky=E)
        self.ketaguri = tkinter.StringVar()
        self.ketaguri.set("")
        self.ketaguri_text = ttk.Label(self, textvariable=self.ketaguri, font=(const.FONT_FAMILY, 11, "bold"))
        self.ketaguri_text.grid(column=7, row=2, columnspan=1, sticky=W)

        self.weight = tkinter.StringVar()
        self.weight.set("")
        self.weight_text = ttk.Label(self, textvariable=self.weight, font=(const.FONT_FAMILY, 11))
        self.weight_text.grid(column=8, row=2, columnspan=8, sticky=W)
        
        self.poketetsu_button = MyButton(self, text="ポケ徹", command=self.open_poketetsu)
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
            self.weight.set( "(重さ：" + str(pokemon.weight) + " kg )")
            if pokemon.weight < 10:
                self.ketaguri.set("20")
            elif pokemon.weight < 25:
                self.ketaguri.set("40")
            elif pokemon.weight < 50:
                self.ketaguri.set("60")
            elif pokemon.weight < 100:
                self.ketaguri.set("80")
            elif pokemon.weight < 200:
                self.ketaguri.set("100")
            else:
                self.ketaguri.set("120")

    def open_poketetsu(self):
        if self._no != 0:
            url = "https://yakkun.com/sv/zukan/?national_no=" + str(self._no)
            webbrowser.open(url)

# 天気フレーム
class WeatherFrame(ttk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self._stage: Stage | None = None
        self._weather_combobox = MyCombobox(self, width=17, height=30, values=WEATHER_COMBOBOX_VALUES)
        self._weather_combobox.bind("<<ComboboxSelected>>", self.change_weather)
        self._weather_combobox.pack()

    def set_stage(self, stage: Stage):
        self._stage = stage

    def change_weather(self, *args):
        self._stage.change_weather(self._weather_combobox.get())

# フィールドフレーム
class FieldFrame(ttk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self._stage: Stage | None = None
        self._field_combobox = MyCombobox(self, width=17, height=30, values=FIELD_COMBOBOX_VALUES)
        self._field_combobox.bind("<<ComboboxSelected>>", self.change_field)
        self._field_combobox.pack()

    def set_stage(self, stage: Stage):
        self._stage = stage

    def change_field(self, *args):
        self._stage.change_field(self._field_combobox.get())

# 素早さ比較ボタン
class SpeedButton(MyButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def set_stage(self, stage: Stage):
        self._stage = stage

    def get_active_pokemons(self):
        return self._stage.get_active_pokemons()

# HOME情報フレーム
class HomeFrame(ttk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._stage: Stage | None = None
        self._tree_list: list[ttk.Treeview] = []
        self._type = [["もちもの", "./home/home_motimono.csv"], ["とくせい", "./home/home_tokusei.csv"], ["せいかく", "./home/home_seikaku.csv"], ["テラスタイプ", "./home/home_terastal.csv"]]
        for i in range(len(self._type)):
            # 列の識別名を指定
            column = ('No', self._type[i][0], '%')
            # Treeviewの生成
            tree = ttk.Treeview(self, columns=column, height=9)
            tree['show'] = 'headings'
            # 列の設定
            tree.column('No', width=10)
            tree.column(self._type[i][0], width=70)
            tree.column('%', width=25)
            # 列の見出し設定
            tree.heading('No', text='No')
            tree.heading(self._type[i][0], text=self._type[i][0])
            tree.heading('%',text='%')
            # ウィジェットの配置
            tree.pack(side=tkinter.LEFT)
            self._tree_list.append(tree)
    
    def set_stage(self, stage: Stage):
        self._stage = stage

    def set_home_data(self, name: str):
        for i in range(len(self._type)):
            from pokedata.loader import get_home_data
            data_list = get_home_data(name, self._type[i][1])
        
            # レコードの追加
            self._tree_list[i].delete(*self._tree_list[i].get_children())
            for j in range(len(data_list)):
                self._tree_list[i].insert(parent='', index='end', iid=self._type[i][0] + str(j) ,values=(j+1, data_list[j][0], data_list[j][1]))
                self._tree_list[i].bind("<<TreeviewSelect>>", lambda e, index=i: self.select_record(index))             

    def select_record(self, index: int):
        if self._tree_list[index].selection():
            # 選択行の判別
            record_id = self._tree_list[index].focus()
            # 選択行のレコードを取得
            value = self._tree_list[index].item(record_id, 'values')
            match index:
                case 0:
                    self._stage.set_value_to_active_pokemon(player=1, item=value[1], is_same=True)
                case 1:
                    self._stage.set_value_to_active_pokemon(player=1, ability=value[1], is_same=True)
                case 2:
                    self._tree_list[index].selection_remove(self._tree_list[index].selection())
                case 3:
                    self._stage.set_value_to_active_pokemon(player=1, terastype=Types.get(value[1]), is_same=True)
    
# タイマーフレーム
class TimerFrame(ttk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.timer_on = False # タイマーの状態
        self.start_time = 0 # 開始時間
        self.set_time = 1200 # セット時間
        self.elapsed_time = 0 # 経過時間
        self.left_time = 0 # 残り時間
        self.left_min = 20 # 残り時間（分）
        self.left_sec = 0 # 残り時間（秒）
        self.after_id = 0 # after_id変数を定義
        self.button_text = tkinter.StringVar()
        self.button_text.set("スタート")

        self.bg=tkinter.StringVar()
        self.canvas_time = tkinter.Canvas(self, width=140, height=70, bg="lightgreen")
        self.canvas_time.grid(column=0, row=0, columnspan=2)

        start_button = tkinter.Button(self, width=9, height=2, textvariable=self.button_text, command=self.start_button_clicked)
        start_button.grid(column=0, row=1)

        self.reset_button = tkinter.Button(self, width=9, height=2, text="リセット", command=self.reset_button_clicked)
        self.reset_button.grid(column=1, row=1)

        self.update_min_text()
        self.update_sec_text()

    # resetボタンを押した時
    def reset_button_clicked(self):
        if self.timer_on == True:
            self.timer_on = False
            self.reset_button["state"] = tkinter.NORMAL
            self.after_cancel(self.after_id)
            self.button_text.set("スタート")

        self.set_time = 1200
        self.left_min = 20
        self.left_sec = 0
 
        self.update_min_text()
        self.update_sec_text()
        
        self.canvas_time["bg"] = "lightgreen"
 
    #startボタンを押した時
    def start_button_clicked(self):
 
        if self.set_time >= 1:
 
            if self.timer_on == False:
                self.timer_on = True
                self.reset_button["state"] = tkinter.DISABLED
 
                self.start_time =time.time() # 開始時間を代入
                self.update_time() # updateTime関数を実行
                self.button_text.set("ストップ")
 
            elif self.timer_on == True:
                self.timer_on = False
 
                self.reset_button["state"] = tkinter.NORMAL
 
                self.set_time = self.left_time
                self.after_cancel(self.after_id)
                self.button_text.set("スタート")
  
    # 時間更新処理
    def update_time(self):
        self.elapsed_time = time.time() - self.start_time  # 経過時間を計算
        self.left_time = self.set_time - self.elapsed_time # 残り時間を計算
        self.left_min = math.floor(self.left_time // 60) # 残り時間（分）を計算
        self.left_sec = math.floor(self.left_time % 60) # 残り時間（秒）を計算
 
        self.update_min_text()
        self.update_sec_text()
 
        if self.left_time > 0.1:
            self.after_id = self.after(10, self.update_time)
        else:
            self.timer_on = False
            self.reset_button["state"] = tkinter.NORMAL
 
            self.set_time = self.left_time
            self.after_cancel(self.after_id)
        
        if self.left_time < 180:
            self.canvas_time["bg"] = "red"
        elif self.left_time < 300:
            self.canvas_time["bg"] = "yellow"
        elif self.left_time < 600:
            self.canvas_time["bg"] = "blue"
    
    # 分の表示更新
    def update_min_text(self):
        self.canvas_time.delete("min_text") # 表示時間（分）を消去
        self.canvas_time.create_text(80,38, text=str(self.left_min).zfill(2) + ":", font=("MSゴシック体", "36", "bold"), tag="min_text", anchor="e") # 分を表示
 
    # 秒の表示更新
    def update_sec_text(self):
        self.canvas_time.delete("sec_text") # 表示時間（秒）を消去
        self.canvas_time.create_text(80,38,text=str(self.left_sec).zfill(2), font=("MSゴシック体", "36", "bold"), tag="sec_text", anchor="w") # 秒を表示

# カウンターフレーム(2個)
class CountersFrame(ttk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.counter_1 = CounterFrame(self)
        self.counter_1.grid(column=0, row=0)
        
        separator = ttk.Separator(self, orient="vertical")
        separator.grid(column=1, row=0, rowspan=3, sticky="ns", padx=5)

        self.counter_2 = CounterFrame(self)
        self.counter_2.grid(column=2, row=0)
        
    def clear_all_counters(self):
        self.counter_1.CountReset()
        self.counter_2.CountReset()

# カウンターフレーム(単体)
class CounterFrame(tkinter.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.name_label = tkinter.Entry(self, width=15)
        self.name_label.grid(column=0, row=0, columnspan=3)
        self.count_num = tkinter.IntVar()
        self.count_num.set(0)
        self.label_count = tkinter.Label(self, textvariable=self.count_num, anchor="center", font=(const.FONT_FAMILY, 24, "bold"))
        self.label_count.grid(column=0, row=1, columnspan=3)

        self.btn_count_down = tkinter.Button(self, text="  -  ", command=self.CountDown, height=2)
        self.btn_count_down.grid(column=0, row=2)

        self.btn_count_reset = tkinter.Button(self, text="リセット", command=self.CountReset, height=2)
        self.btn_count_reset.grid(column=1, row=2)

        self.btn_count_reset = tkinter.Button(self, text="  ＋  ", command=self.CountUp, height=2)
        self.btn_count_reset.grid(column=2, row=2)

    def CountDown(self):
        decrease_num = self.count_num.get()
        if decrease_num > 0:
            decrease_num = decrease_num - 1
            self.count_num.set(decrease_num)
            self.label_count["text"] = self.count_num.get()

    def CountReset(self):
        reset_num = 0
        self.count_num.set(reset_num)
        self.label_count["text"] = self.count_num.get()

    def CountUp(self):
        increase_num = self.count_num.get()
        if increase_num < 99:
            increase_num = increase_num + 1
            self.count_num.set(increase_num)
            self.label_count["text"] = self.count_num.get()

# 対戦記録フレーム
class RecordFrame(ttk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._stage: Stage | None = None
        self.result = -1
        
        self.tn_lbl = MyLabel(self, text="TN")
        self.tn_lbl.grid(column=0, row=0)
        self.tn = tkinter.Entry(self)
        self.tn.grid(column=1, row=0, sticky=N+E+W+S)

        self.rank_lbl = MyLabel(self, text="ランク")
        self.rank_lbl.grid(column=0, row=1)
        self.rank = tkinter.Entry(self)
        self.rank.grid(column=1, row=1, sticky=N+E+W+S)
        
        self.memo_lbl = MyLabel(self, text="メモ")
        self.memo_lbl.grid(column=0, row=2)
        self.memo = ScrolledText(self, font=("", 15), height=7, width=45)
        self.memo.grid(column=1, row=2, columnspan=4, sticky=N+E+W+S)
        
        self.favo = tkinter.BooleanVar()
        self.favo.set(False)
        self.favo_checkbox = tkinter.Checkbutton(self, variable=self.favo, text='お気に入り')
        self.favo_checkbox.grid(column=2, row=0, columnspan=2)
        
        win_btn = MyButton(self, width=4, text="勝ち", command=lambda: self.register(1))
        win_btn.grid(column=2, row=1, sticky=N+E+W+S)
        lose_btn = MyButton(self, width=4, text="負け", command=lambda: self.register(0))
        lose_btn.grid(column=3, row=1, sticky=N+E+W+S)
        draw_btn = MyButton(self, width=4, text="引き分け", command=lambda: self.register(-1))
        draw_btn.grid(column=4, row=0, sticky=N+E+W+S)
        clear_btn = MyButton(self, width=4, text="クリア", command=self.clear)
        clear_btn.grid(column=4, row=1, sticky=N+E+W+S)

    def set_stage(self, stage: Stage):
        self._stage = stage
        
    def register(self, result: int):
        self.result = result
        self._stage.record_battle()
        self._stage.loop_image_recognize()
    
    def clear(self):
        self._stage.clear_battle()
        self.tn.delete(0, tkinter.END)
        self.rank.delete(0, tkinter.END)
        self.memo.delete("1.0", "end")
        self.favo.set(False)
    
