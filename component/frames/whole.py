from __future__ import annotations

import math
import time
import tkinter
from tkinter import E, N, S, W, ttk
from tkinter.scrolledtext import ScrolledText
from typing import TYPE_CHECKING

from component.parts import const
from component.parts.button import MyButton
from component.parts.combobox import MyCombobox
from component.parts.const import FIELD_COMBOBOX_VALUES, WEATHER_COMBOBOX_VALUES
from component.parts.label import MyLabel
from pokedata.const import Types

if TYPE_CHECKING:
    from component.stage import Stage


# 天気フレーム
class WeatherFrame(ttk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._stage: Stage | None = None
        self._weather_combobox = MyCombobox(
            self, width=17, height=30, values=WEATHER_COMBOBOX_VALUES
        )
        self._weather_combobox.set(WEATHER_COMBOBOX_VALUES[0])
        self._weather_combobox.bind("<<ComboboxSelected>>", self.change_weather)
        self._weather_combobox.pack()

    def set_stage(self, stage: Stage):
        self._stage = stage

    def change_weather(self, *args):
        self._stage.change_weather(self._weather_combobox.get())

    def change_weather_from_ability(self, weather: str, *args):
        self._stage.change_weather(weather)
        self._weather_combobox.set(weather)

    def reset_weather(self, *args):
        self._weather_combobox.set(WEATHER_COMBOBOX_VALUES[0])
        self._stage.change_weather(WEATHER_COMBOBOX_VALUES[0])


# フィールドフレーム
class FieldFrame(ttk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._stage: Stage | None = None
        self._field_combobox = MyCombobox(
            self, width=17, height=30, values=FIELD_COMBOBOX_VALUES
        )
        self._field_combobox.set(FIELD_COMBOBOX_VALUES[0])
        self._field_combobox.bind("<<ComboboxSelected>>", self.change_field)
        self._field_combobox.pack()

    def set_stage(self, stage: Stage):
        self._stage = stage

    def change_field(self, *args):
        self._stage.change_field(self._field_combobox.get())

    def change_field_from_ability(self, field: str, *args):
        self._stage.change_field(field)
        self._field_combobox.set(field)

    def reset_field(self, *args):
        self._field_combobox.set(FIELD_COMBOBOX_VALUES[0])
        self._stage.change_field(FIELD_COMBOBOX_VALUES[0])


# 比較ボタン
class CompareButton(MyButton):
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
        self._type = [
            ["もちもの", "./stats/home_motimono.csv"],
            ["とくせい", "./stats/home_tokusei.csv"],
            ["せいかく", "./stats/home_seikaku.csv"],
            ["テラスタル", "./stats/home_terastal.csv"],
        ]
        for i in range(len(self._type)):
            # 列の識別名を指定
            column = ("No", self._type[i][0], "%")
            # Treeviewの生成
            tree = ttk.Treeview(self, columns=column, height=9)
            tree["show"] = "headings"
            # 列の設定
            tree.column("No", width=10)
            if i == 0:
                tree.column(self._type[i][0], width=70)
            elif i == 1:
                tree.column(self._type[i][0], width=74)
            else:
                tree.column(self._type[i][0], width=60)
            tree.column("%", width=22)
            # 列の見出し設定
            tree.heading("No", text="No")
            tree.heading(self._type[i][0], text=self._type[i][0])
            tree.heading("%", text="%")
            # ウィジェットの配置
            tree.grid(column=i, row=0)
            self._tree_list.append(tree)
            self.grid_columnconfigure(i, weight=1)

    def set_stage(self, stage: Stage):
        self._stage = stage

    def set_home_data(self, name: str):
        for i in range(len(self._type)):
            from pokedata.loader import get_home_data

            data_list = get_home_data(name, self._type[i][1])

            # レコードの追加
            self._tree_list[i].delete(*self._tree_list[i].get_children())
            for j in range(len(data_list)):
                self._tree_list[i].insert(
                    parent="",
                    index="end",
                    iid=self._type[i][0] + str(j),
                    values=(j + 1, data_list[j][0], data_list[j][1]),
                )
                self._tree_list[i].bind(
                    "<<TreeviewSelect>>", lambda e, index=i: self.select_record(index)
                )

    def select_record(self, index: int):
        if self._tree_list[index].selection():
            # 選択行の判別
            record_id = self._tree_list[index].focus()
            # 選択行のレコードを取得
            value = self._tree_list[index].item(record_id, "values")
            match index:
                case 0:
                    self._stage.set_value_to_active_pokemon(
                        player=1, item=value[1], is_same=True
                    )
                case 1:
                    self._stage.set_value_to_active_pokemon(
                        player=1, ability=value[1], is_same=True
                    )
                case 2:
                    self._stage.set_value_to_active_pokemon(
                        player=1, seikaku=value[1], is_same=True
                    )
                case 3:
                    self._stage.set_value_to_active_pokemon(
                        player=1, terastype=Types.get(value[1]), is_same=True
                    )


# タイマーフレーム
class TimerFrame(ttk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.timer_on = False  # タイマーの状態
        self.start_time = 0  # 開始時間
        self.set_time = 1200  # セット時間
        self.elapsed_time = 0  # 経過時間
        self.left_time = 0  # 残り時間
        self.left_min = 20  # 残り時間（分）
        self.left_sec = 0  # 残り時間（秒）
        self.after_id = 0  # after_id変数を定義
        self.button_text = tkinter.StringVar()
        self.button_text.set("スタート")

        self.bg = tkinter.StringVar()
        self.canvas_time = tkinter.Canvas(self, width=130, height=70, bg="lightgreen")
        self.canvas_time.grid(column=0, row=0, columnspan=2)

        start_button = tkinter.Button(
            self,
            width=9,
            height=2,
            textvariable=self.button_text,
            command=self.start_button_clicked,
        )
        start_button.grid(column=0, row=1)

        self.reset_button = tkinter.Button(
            self, width=9, height=2, text="リセット", command=self.reset_button_clicked
        )
        self.reset_button.grid(column=1, row=1)

        self.update_min_text()
        self.update_sec_text()

    # resetボタンを押した時
    def reset_button_clicked(self):
        if self.timer_on is True:
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

    # startボタンを押した時
    def start_button_clicked(self):
        if self.set_time >= 1:
            if self.timer_on is False:
                self.timer_on = True
                self.reset_button["state"] = tkinter.DISABLED

                self.start_time = time.time()  # 開始時間を代入
                self.update_time()  # updateTime関数を実行
                self.button_text.set("ストップ")

            elif self.timer_on is True:
                self.timer_on = False

                self.reset_button["state"] = tkinter.NORMAL

                self.set_time = self.left_time
                self.after_cancel(self.after_id)
                self.button_text.set("スタート")

    # 時間更新処理
    def update_time(self):
        self.elapsed_time = time.time() - self.start_time  # 経過時間を計算
        self.left_time = self.set_time - self.elapsed_time  # 残り時間を計算
        self.left_min = math.floor(self.left_time // 60)  # 残り時間（分）を計算
        self.left_sec = math.floor(self.left_time % 60)  # 残り時間（秒）を計算

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
        self.canvas_time.delete("min_text")  # 表示時間（分）を消去
        self.canvas_time.create_text(
            71,
            38,
            text=str(self.left_min).zfill(2) + ":",
            font=("MSゴシック体", "36", "bold"),
            tag="min_text",
            anchor="e",
        )  # 分を表示

    # 秒の表示更新
    def update_sec_text(self):
        self.canvas_time.delete("sec_text")  # 表示時間（秒）を消去
        self.canvas_time.create_text(
            80,
            38,
            text=str(self.left_sec).zfill(2),
            font=("MSゴシック体", "36", "bold"),
            tag="sec_text",
            anchor="w",
        )  # 秒を表示


# カウンターフレーム(2個)
class CounterFrame(tkinter.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.name_label = tkinter.Entry(self, width=7)
        self.name_label.grid(column=0, row=0, columnspan=3)
        self.count_num = tkinter.IntVar()
        self.count_num.set(0)
        self.label_count = tkinter.Label(
            self,
            textvariable=self.count_num,
            anchor="center",
            font=(const.FONT_FAMILY, 24, "bold"),
        )
        self.label_count.grid(column=0, row=1, columnspan=3)

        self.btn_count_down = tkinter.Button(
            self, text="  -  ", command=self.CountDown, height=2
        )
        self.btn_count_down.grid(column=0, row=2)

        self.btn_count_reset = tkinter.Button(
            self, text="0", command=self.CountReset, height=2
        )
        self.btn_count_reset.grid(column=1, row=2)

        self.btn_count_reset = tkinter.Button(
            self, text="  ＋  ", command=self.CountUp, height=2
        )
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


# カウンターフレーム(単体)
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


# 対戦記録フレーム
class RecordFrame(ttk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._stage: Stage | None = None
        self.result = -1

        self.tn_lbl = MyLabel(self, text="TN")
        self.tn_lbl.grid(column=0, row=0)
        self.tn = tkinter.Entry(self)
        self.tn.grid(column=1, row=0, sticky=N + E + W + S)

        self.rank_lbl = MyLabel(self, text="ランク")
        self.rank_lbl.grid(column=0, row=1)
        self.rank = tkinter.Entry(self)
        self.rank.grid(column=1, row=1, sticky=N + E + W + S)

        self.memo_lbl = MyLabel(self, text="メモ")
        self.memo_lbl.grid(column=0, row=2)
        self.memo = ScrolledText(self, font=("", 15), height=6, width=41)
        self.memo.grid(column=1, row=2, columnspan=4, sticky=N + E + W + S)

        self.favo = tkinter.BooleanVar()
        self.favo.set(False)
        self.favo_checkbox = tkinter.Checkbutton(
            self, variable=self.favo, text="お気に入り"
        )
        self.favo_checkbox.grid(column=2, row=0, columnspan=2)

        win_btn = MyButton(self, width=4, text="勝ち", command=lambda: self.register(1))
        win_btn.grid(column=2, row=1, sticky=N + E + W + S)
        lose_btn = MyButton(
            self, width=4, text="負け", command=lambda: self.register(0)
        )
        lose_btn.grid(column=3, row=1, sticky=N + E + W + S)
        draw_btn = MyButton(
            self, width=4, text="引き分け", command=lambda: self.register(-1)
        )
        draw_btn.grid(column=4, row=0, sticky=N + E + W + S)
        clear_btn = MyButton(self, width=4, text="クリア", command=self.clear)
        clear_btn.grid(column=4, row=1, sticky=N + E + W + S)

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
