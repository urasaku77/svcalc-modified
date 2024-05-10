import datetime
import tkinter

from PIL import Image, ImageTk

from database.battle import DB_battle
from mypgl.const import Const


class Analytics(tkinter.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("myPGL")

        before_recent_date = DB_battle.get_recent_date()[0]
        self.recent_date = (
            datetime.date(
                datetime.datetime.fromtimestamp(before_recent_date).year,
                datetime.datetime.fromtimestamp(before_recent_date).month,
                datetime.datetime.fromtimestamp(before_recent_date).day,
            )
            if before_recent_date is not None
            else datetime.datetime.today()
        )
        self.party_num = 0
        self.party_subnum = 0

        self.pokemon_list = []
        self.result_1_list = []
        self.result_2_list = []
        self.result_1_label_list = []
        self.result_2_label_list = []

        self.img_list = []
        self.canvas_list = []

        self.record_count_label = None
        self.whole_win_rate_label = None

        self.sort_condition_options = [("KP（選出/初手）", 0), ("勝率", 1)]
        self.sort_line_options = [("降順", False), ("昇順", True)]

        self.display_gui(self.recent_date)
        self.update_result(
            int(self.recent_date.year),
            int(self.recent_date.month),
            1,
            int(self.recent_date.year),
            int(self.recent_date.month),
            int(self.recent_date.day),
            True,
        )

        for i in range(50):
            rank_label = tkinter.Label(self, text=str(i + 1) + "位")
            rank_label.place(x=Const.list2[i][1] - 40, y=Const.list2[i][2])

    def open(self):
        self.grab_set()
        self.focus_set()
        self.geometry("1280x720")

    def display_gui(self, search_date: datetime.datetime):
        kikan_label = tkinter.Label(self, text="期間")
        kikan_label.place(x=Const.searchX, y=Const.searchY - Const.searchDY)
        rank_label = tkinter.Label(self, text="パーティ絞り込み")
        rank_label.place(x=Const.searchX, y=Const.searchY + Const.searchDY * 2)

        self.from_year_var = tkinter.IntVar(self)
        self.from_year_var.set(int(search_date.year))
        from_year_menu = tkinter.OptionMenu(self, self.from_year_var, *Const.yearList)
        from_year_menu.place(x=Const.searchX, y=Const.searchY)
        self.from_month_var = tkinter.IntVar(self)
        self.from_month_var.set(int(search_date.month))
        self.from_date_var = tkinter.IntVar(self)
        self.from_date_var.set(1)
        from_month_menu = tkinter.OptionMenu(
            self, self.from_month_var, *Const.monthList
        )
        from_month_menu.place(x=Const.searchX + 70, y=Const.searchY)
        from_date_menu = tkinter.OptionMenu(self, self.from_date_var, *Const.dateList)
        from_date_menu.place(x=Const.searchX + 120, y=Const.searchY)

        mack_label = tkinter.Label(self, text=" ~ ", font=Const.titleFont)
        mack_label.place(x=Const.searchX + 170, y=Const.searchY)

        self.to_year_var = tkinter.IntVar(self)
        self.to_year_var.set(int(search_date.year))
        to_year_menu = tkinter.OptionMenu(self, self.to_year_var, *Const.yearList)
        to_year_menu.place(x=Const.searchX + 200, y=Const.searchY)
        self.to_month_var = tkinter.IntVar(self)
        self.to_month_var.set(int(search_date.month))
        self.to_date_var = tkinter.IntVar(self)
        self.to_date_var.set(int(search_date.day))
        to_month_menu = tkinter.OptionMenu(self, self.to_month_var, *Const.monthList)
        to_month_menu.place(x=Const.searchX + 270, y=Const.searchY)
        to_date_menu = tkinter.OptionMenu(self, self.to_date_var, *Const.dateList)
        to_date_menu.place(x=Const.searchX + 330, y=Const.searchY)

        self.time9_bln = tkinter.BooleanVar()
        self.time9_bln.set(True)
        time9_check = tkinter.Checkbutton(
            self, variable=self.time9_bln, text="初日を9時以降にする"
        )
        time9_check.place(x=Const.searchX + 400, y=Const.searchY)

        num_label = tkinter.Label(self, text="番号")
        num_label.place(x=Const.searchX, y=Const.searchY + Const.searchDY * 3)
        self.num_txt = tkinter.Entry(self, width=Const.txtboxWidth)
        self.num_txt.place(x=Const.searchX + 40, y=Const.searchY + Const.searchDY * 3)
        sub_num_label = tkinter.Label(self, text="連番")
        sub_num_label.place(x=Const.searchX + 90, y=Const.searchY + Const.searchDY * 3)
        self.sub_num_txt = tkinter.Entry(self, width=Const.txtboxWidth)
        self.sub_num_txt.place(
            x=Const.searchX + 130, y=Const.searchY + Const.searchDY * 3
        )
        search_button = tkinter.Button(
            self,
            text="検索",
            command=self.update_result,
        )
        search_button.place(
            x=Const.searchX + 200, y=Const.searchY + Const.searchDY * 2.7
        )
        self.title_var = tkinter.StringVar()
        self.title_var.set("ＫＰと勝率")
        self.main_title_label = tkinter.Button(
            self,
            textvariable=self.title_var,
            font=Const.titleFont,
            state="disable",
            command=self.change_mode,
        )
        sort_condition_frame = tkinter.Frame(self)
        self.sort_condition_var = tkinter.IntVar()
        self.sort_condition_var.set(0)
        for text, value in self.sort_condition_options:
            rb = tkinter.Radiobutton(
                sort_condition_frame,
                text=text,
                variable=self.sort_condition_var,
                value=value,
                command=self.change_sort_condition,
            )
            rb.grid(sticky="w")
        sort_condition_frame.place(x=Const.searchX + 130, y=Const.kpStartY - 60)
        sort_line_frame = tkinter.Frame(self)
        self.sort_line_var = tkinter.BooleanVar()
        self.sort_line_var.set(True)
        for text, value in self.sort_line_options:
            rb = tkinter.Radiobutton(
                sort_line_frame,
                text=text,
                variable=self.sort_line_var,
                value=value,
                command=self.change_sort_condition,
            )
            rb.grid(sticky="w")
        sort_line_frame.place(x=Const.searchX + 270, y=Const.kpStartY - 60)
        self.main_title_label.place(x=Const.kpStartX, y=Const.kpStartY - 60)
        self.subtitle_var = tkinter.StringVar()
        self.subtitle_var.set("直近使用したパーティ")
        self.sub_title_label = tkinter.Label(
            self, textvariable=self.subtitle_var, font=Const.titleFont
        )
        self.sub_title_label.place(x=Const.myPartyStartX, y=Const.myPartyStartY - 30)

    def update_result(self):
        self.from_date, self.to_date = DB_battle.chenge_date_from_datetime_to_unix(
            self.from_year_var.get(),
            self.from_month_var.get(),
            self.from_date_var.get(),
            self.to_year_var.get(),
            self.to_month_var.get(),
            self.to_date_var.get(),
            self.time9_bln.get(),
        )
        self.delete_result_page()
        self.sort_condition_var.set(0)
        self.sort_line_var.set(True)
        self.party_num = (
            int(self.num_txt.get())
            if self.num_txt.get() is not None and self.num_txt.get() != ""
            else 0
        )
        self.party_subnum = (
            int(self.sub_num_txt.get())
            if self.sub_num_txt.get() is not None and self.sub_num_txt.get() != ""
            else 0
        )
        self.title_var.set("ＫＰと勝率")
        self.main_title_label["state"] = (
            "disable" if self.party_num == 0 and self.party_subnum == 0 else "normal"
        )
        if self.party_num != 0 and self.party_subnum != 0:
            self.pokemon_list = [
                item[0]
                for item in DB_battle.calc_kp_for_party_subnum(
                    self.from_date,
                    self.to_date,
                    self.party_num,
                    self.party_subnum,
                )
            ]
            self.result_1_list = [
                item[1]
                for item in DB_battle.calc_kp_for_party_subnum(
                    self.from_date,
                    self.to_date,
                    self.party_num,
                    self.party_subnum,
                )
            ]
            self.result_2_list = DB_battle.get_win_rate_for_party_subnum(
                self.pokemon_list,
                self.from_date,
                self.to_date,
                self.party_num,
                self.party_subnum,
            )
            self.record_count = DB_battle.count_record_for_party_subnum(
                self.from_date, self.to_date, self.party_num, self.party_subnum
            )
            self.win_count = DB_battle.count_win_for_party_subnum(
                self.from_date, self.to_date, self.party_num, self.party_subnum
            )
        elif self.party_num != 0:
            self.pokemon_list = [
                item[0]
                for item in DB_battle.calc_kp_for_party_num(
                    self.from_date, self.to_date, self.party_num
                )
            ]
            self.result_1_list = [
                item[1]
                for item in DB_battle.calc_kp_for_party_num(
                    self.from_date, self.to_date, self.party_num
                )
            ]
            self.result_2_list = DB_battle.get_win_rate_for_party_num(
                self.pokemon_list, self.from_date, self.to_date, self.party_num
            )
            self.record_count = DB_battle.count_record_for_party_num(
                self.from_date, self.to_date, self.party_num
            )
            self.win_count = DB_battle.count_win_for_party_num(
                self.from_date, self.to_date, self.party_num
            )
        else:
            self.pokemon_list = [
                item[0] for item in DB_battle.calc_kp(self.from_date, self.to_date)
            ]
            self.result_1_list = [
                item[1] for item in DB_battle.calc_kp(self.from_date, self.to_date)
            ]
            self.result_2_list = DB_battle.get_win_rate(
                self.pokemon_list, self.from_date, self.to_date
            )
            self.record_count = DB_battle.count_record(self.from_date, self.to_date)
            self.win_count = DB_battle.count_win(self.from_date, self.to_date)
        self.display_result_1()
        self.display_result_2()
        self.display_image()
        self.record_count_label = tkinter.Label(
            self,
            text="対戦数：" + str(self.record_count[0]),
            font=Const.titleFont,
        )
        self.record_count_label.place(x=Const.myPartyStartX + 50, y=Const.searchY)
        whole_win_rate = (
            self.win_count[0] * 100 / self.record_count[0]
            if self.record_count[0] != 0
            else 0
        )
        self.whole_win_rate_label = tkinter.Label(
            self,
            text=str("勝率：" + "{:.1f}".format(whole_win_rate)) + "%",
            font=Const.titleFont,
        )
        self.whole_win_rate_label.place(
            x=Const.myPartyStartX + 50, y=Const.searchY + Const.searchDY * 2
        )
        self.display_party_detail()

    def display_result_1(self):
        if self.title_var.get() == "ＫＰと勝率":
            for i in range(len(self.result_1_list)):
                if i > 49:
                    break
                result_1_label = tkinter.Label(
                    self,
                    text=str(
                        "{:.1f}".format(
                            (
                                int(self.result_1_list[i])
                                * 100
                                / int(self.record_count[0])
                            )
                        )
                    )
                    + "%",
                )
                result_1_label.place(x=Const.list2[i][1] - 40, y=Const.list2[i][2] + 20)
                self.result_1_label_list.append(result_1_label)
        else:
            for i in range(len(self.result_1_list)):
                if i > 49:
                    break
                result_1_label = tkinter.Label(
                    self,
                    text=str("{:.1f}".format(self.result_1_list[i] * 100)) + "%",
                )
                result_1_label.place(x=Const.list2[i][1] - 40, y=Const.list2[i][2] + 20)
                self.result_1_label_list.append(result_1_label)

    def display_result_2(self):
        for i in range(len(self.result_2_list)):
            if i > 49:
                break
            result_2_label = tkinter.Label(
                self, text=str("{:.1f}".format(self.result_2_list[i] * 100)) + "%"
            )
            result_2_label.place(x=Const.list2[i][1] - 40, y=Const.list2[i][2] + 40)
            self.result_2_label_list.append(result_2_label)
            i = i + 1

    def display_image(self):
        i = 0
        for pokemon in self.pokemon_list:
            if len(pokemon[0]) < 1:
                break
            img = Image.open(Const.createPass(pokemon))
            img = img.resize((40, 40))
            img = ImageTk.PhotoImage(img)
            canvas = tkinter.Canvas(self, width=50, height=50)
            canvas.place(x=Const.list2[i][1], y=Const.list2[i][2] + 10)
            canvas.create_image(5, 5, image=img, anchor=tkinter.NW)
            self.img_list.append(img)
            self.canvas_list.append(canvas)
            i = i + 1
            if i > 49:
                break

    def change_sort_condition(self):
        self.delete_result()
        new_result_list = list(
            zip(
                self.pokemon_list,
                self.result_1_list,
                self.result_2_list,
                strict=False,
            )
        )

        if self.sort_condition_var.get() == 0:
            new_result_list.sort(key=lambda x: x[1], reverse=self.sort_line_var.get())
        elif self.sort_condition_var.get() == 1:
            new_result_list.sort(key=lambda x: x[2], reverse=self.sort_line_var.get())

        self.pokemon_list = [item[0] for item in new_result_list]
        self.result_1_list = [item[1] for item in new_result_list]
        self.result_2_list = [item[2] for item in new_result_list]

        self.display_result_1()
        self.display_result_2()
        self.display_image()

    def change_mode(self):
        self.delete_result()
        if self.title_var.get() == "ＫＰと勝率":
            self.title_var.set("選出と勝率")
            self.result_1_list = (
                DB_battle.get_oppo_chosen_rate_for_party_num(
                    self.pokemon_list, self.from_date, self.to_date, self.party_num
                )
                if self.party_subnum == 0
                else DB_battle.get_oppo_chosen_rate_for_party_subnum(
                    self.pokemon_list,
                    self.from_date,
                    self.to_date,
                    self.party_num,
                    self.party_subnum,
                )
            )
            self.result_2_list = (
                DB_battle.get_oppo_chosen_and_win_rate_for_party_num(
                    self.pokemon_list, self.from_date, self.to_date, self.party_num
                )
                if self.party_subnum == 0
                else DB_battle.get_oppo_chosen_and_win_rate_for_party_subnum(
                    self.pokemon_list,
                    self.from_date,
                    self.to_date,
                    self.party_num,
                    self.party_subnum,
                )
            )

        elif self.title_var.get() == "選出と勝率":
            self.title_var.set("初手と勝率")
            self.result_1_list = (
                DB_battle.get_oppo_first_chosen_rate_for_party_num(
                    self.pokemon_list, self.from_date, self.to_date, self.party_num
                )
                if self.party_subnum == 0
                else DB_battle.get_oppo_first_chosen_rate_for_party_subnum(
                    self.pokemon_list,
                    self.from_date,
                    self.to_date,
                    self.party_num,
                    self.party_subnum,
                )
            )
            self.result_2_list = (
                DB_battle.get_oppo_first_chosen_and_win_rate_for_party_num(
                    self.pokemon_list, self.from_date, self.to_date, self.party_num
                )
                if self.party_subnum == 0
                else DB_battle.get_oppo_first_chosen_and_win_rate_for_party_subnum(
                    self.pokemon_list,
                    self.from_date,
                    self.to_date,
                    self.party_num,
                    self.party_subnum,
                )
            )

        elif self.title_var.get() == "初手と勝率":
            self.title_var.set("ＫＰと勝率")
            self.pokemon_list = (
                [
                    item[0]
                    for item in DB_battle.calc_kp_for_party_num(
                        self.from_date, self.to_date, self.party_num
                    )
                ]
                if self.party_subnum == 0
                else [
                    item[0]
                    for item in DB_battle.calc_kp_for_party_subnum(
                        self.from_date, self.to_date, self.party_num, self.party_subnum
                    )
                ]
            )
            self.result_1_list = (
                [
                    item[1]
                    for item in DB_battle.calc_kp_for_party_num(
                        self.from_date, self.to_date, self.party_num
                    )
                ]
                if self.party_subnum == 0
                else [
                    item[1]
                    for item in DB_battle.calc_kp_for_party_subnum(
                        self.from_date, self.to_date, self.party_num, self.party_subnum
                    )
                ]
            )
            self.result_2_list = (
                DB_battle.get_win_rate_for_party_num(
                    self.pokemon_list, self.from_date, self.to_date, self.party_num
                )
                if self.party_subnum == 0
                else DB_battle.get_win_rate_for_party_subnum(
                    self.pokemon_list,
                    self.from_date,
                    self.to_date,
                    self.party_num,
                    self.party_subnum,
                )
            )

        self.display_result_1()
        self.display_result_2()
        self.display_image()

    def display_party_detail(self):
        party_canvas = tkinter.Canvas(self, width=350, height=600)
        party_canvas.place(x=0, y=Const.myPartyStartY)

        if self.party_num != 0 and self.party_subnum != 0:
            pokemon_list = DB_battle.get_my_party_for_party_subnum(
                self.party_num, self.party_subnum
            )
            if pokemon_list != -1:
                win_rate_list = DB_battle.get_win_rate_per_pokemon_for_party_subnum(
                    list(pokemon_list[0]),
                    self.from_date,
                    self.to_date,
                    self.party_num,
                    self.party_subnum,
                )
                chosen_rate_list = DB_battle.get_chosen_rate_for_party_subnum(
                    list(pokemon_list[0]),
                    self.from_date,
                    self.to_date,
                    self.party_num,
                    self.party_subnum,
                )
                chosen_and_win_rate_list = (
                    DB_battle.get_chosen_and_win_rate_for_party_subnum(
                        list(pokemon_list[0]),
                        self.from_date,
                        self.to_date,
                        self.party_num,
                        self.party_subnum,
                    )
                )
                first_chosen_rate_list = (
                    DB_battle.get_first_chosen_rate_for_party_subnum(
                        list(pokemon_list[0]),
                        self.from_date,
                        self.to_date,
                        self.party_num,
                        self.party_subnum,
                    )
                )
                first_chosen_and_win_rate_list = (
                    DB_battle.get_first_chosen_and_win_rate_for_party_subnum(
                        list(pokemon_list[0]),
                        self.from_date,
                        self.to_date,
                        self.party_num,
                        self.party_subnum,
                    )
                )
                self.subtitle_var.set("パーティ詳細")
                for i in range(len(list(pokemon_list[0]))):
                    img = Image.open(Const.createPass(pokemon_list[0][i]))
                    img = img.resize((40, 40))
                    img = ImageTk.PhotoImage(img)
                    canvas = tkinter.Canvas(self, width=50, height=50)
                    canvas.place(
                        x=Const.myPartyDetailList[0][0],
                        y=Const.myPartyDetailList[i][1],
                    )
                    canvas.create_image(5, 5, image=img, anchor=tkinter.NW)
                    self.img_list.append(img)
                    party_num_label = tkinter.Label(
                        self,
                        text="勝率："
                        + "{:.1f}".format(win_rate_list[i] * 100)
                        + "%\n選出率："
                        + "{:.1f}".format(chosen_rate_list[i] * 100)
                        + "%ー選出時勝率："
                        + "{:.1f}".format(chosen_and_win_rate_list[i] * 100)
                        + "%\n初手選出率："
                        + "{:.1f}".format(first_chosen_rate_list[i] * 100)
                        + "%ー初手選出時勝率："
                        + "{:.1f}".format(first_chosen_and_win_rate_list[i] * 100)
                        + "%",
                    )
                    party_num_label.place(
                        x=Const.myPartyDetailList[0][0] + 50,
                        y=Const.myPartyDetailList[i][1],
                    )
            else:
                self.display_my_party()

        elif self.party_num != 0:
            pokemon_list = DB_battle.get_my_party_for_party_num(self.party_num)
            if pokemon_list != -1:
                win_rate_list = DB_battle.get_win_rate_per_pokemon_for_party_num(
                    list(pokemon_list[0]),
                    self.from_date,
                    self.to_date,
                    self.party_num,
                )
                chosen_rate_list = DB_battle.get_chosen_rate_for_party_num(
                    list(pokemon_list[0]),
                    self.from_date,
                    self.to_date,
                    self.party_num,
                )
                chosen_and_win_rate_list = (
                    DB_battle.get_chosen_and_win_rate_for_party_num(
                        list(pokemon_list[0]),
                        self.from_date,
                        self.to_date,
                        self.party_num,
                    )
                )
                first_chosen_rate_list = DB_battle.get_first_chosen_rate_for_party_num(
                    list(pokemon_list[0]),
                    self.from_date,
                    self.to_date,
                    self.party_num,
                )
                first_chosen_and_win_rate_list = (
                    DB_battle.get_first_chosen_and_win_rate_for_party_num(
                        list(pokemon_list[0]),
                        self.from_date,
                        self.to_date,
                        self.party_num,
                    )
                )
                self.subtitle_var.set("パーティ詳細")
                for i in range(len(list(pokemon_list[0]))):
                    img = Image.open(Const.createPass(pokemon_list[0][i]))
                    img = img.resize((40, 40))
                    img = ImageTk.PhotoImage(img)
                    canvas = tkinter.Canvas(self, width=50, height=50)
                    canvas.place(
                        x=Const.myPartyDetailList[0][0],
                        y=Const.myPartyDetailList[i][1],
                    )
                    canvas.create_image(5, 5, image=img, anchor=tkinter.NW)
                    self.img_list.append(img)
                    party_num_label = tkinter.Label(
                        self,
                        text="勝率："
                        + "{:.1f}".format(win_rate_list[i] * 100)
                        + "%\n選出率："
                        + "{:.1f}".format(chosen_rate_list[i] * 100)
                        + "%ー選出時勝率："
                        + "{:.1f}".format(chosen_and_win_rate_list[i] * 100)
                        + "%\n初手選出率："
                        + "{:.1f}".format(first_chosen_rate_list[i] * 100)
                        + "%ー初手選出時勝率："
                        + "{:.1f}".format(first_chosen_and_win_rate_list[i] * 100)
                        + "%",
                    )
                    party_num_label.place(
                        x=Const.myPartyDetailList[0][0] + 50,
                        y=Const.myPartyDetailList[i][1],
                    )
            else:
                self.display_my_party()
        else:
            self.display_my_party()

    def display_my_party(self):
        self.subtitle_var.set("直近使用したパーティ")
        pokemon_list = DB_battle.get_my_party()
        for i in range(len(pokemon_list)):
            party_num = f"{pokemon_list[i][6]}-{pokemon_list[i][7]}"
            for j in range(7):
                if j == 6:
                    party_num_label = tkinter.Label(
                        self, text=party_num, font=Const.titleFont
                    )
                    party_num_label.place(
                        x=Const.myPartyPointList[i * 7 + j][0],
                        y=Const.myPartyPointList[i * 7 + j][1],
                    )
                else:
                    img = Image.open(Const.createPass(pokemon_list[i][j]))
                    img = img.resize((40, 40))
                    img = ImageTk.PhotoImage(img)
                    canvas = tkinter.Canvas(self, width=50, height=50)
                    canvas.place(
                        x=Const.myPartyPointList[i * 7 + j][0],
                        y=Const.myPartyPointList[i * 7 + j][1],
                    )
                    canvas.create_image(5, 5, image=img, anchor=tkinter.NW)
                    self.img_list.append(img)

    def delete_result_page(self):
        if self.record_count_label is not None:
            self.record_count_label.destroy()
        if self.whole_win_rate_label is not None:
            self.whole_win_rate_label.destroy()
        if self.result_1_label_list is not []:
            for kpLabel in self.result_1_label_list:
                kpLabel.destroy()
                self.result_1_label_list = []
        if self.result_2_label_list is not []:
            for win_rate_label in self.result_2_label_list:
                win_rate_label.destroy()
                self.win_rate_label = []
        if self.canvas_list is not []:
            for canvas in self.canvas_list:
                canvas.delete("all")
                self.canvas_list = []

    def delete_result(self):
        if self.result_1_label_list is not []:
            for kp_label in self.result_1_label_list:
                kp_label.destroy()
                self.result_1_label_list = []
        if self.result_2_label_list is not []:
            for win_rate_label in self.result_2_label_list:
                win_rate_label.destroy()
                self.win_rate_label = []
