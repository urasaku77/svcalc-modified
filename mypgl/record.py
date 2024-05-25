import datetime
import math
import tkinter

from PIL import Image, ImageTk

from database.battle import DB_battle
from mypgl.const import Const


class Record(tkinter.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("対戦履歴")

        self.page_num_var = tkinter.IntVar(value=1)
        self.page_num_label = None
        self.page_position_label = None

        self.party_num = 0
        self.party_subnum = 0

        self.battle_time_label_list = []
        self.sensyutu_img_list = []
        self.rank_label_list = []
        self.win_lose_label_list = []
        self.canvas_list = []
        self.battle_data_list = []

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

        self.display_gui()

    def open(self):
        self.focus_set()
        self.geometry("1800x950")

    def display_gui(self):
        kikan_label = tkinter.Label(self, text="期間")
        kikan_label.place(x=Const.searchX, y=Const.searchY - Const.searchDY)
        rank_label = tkinter.Label(self, text="パーティ絞り込み")
        rank_label.place(x=Const.searchX, y=Const.searchY + Const.searchDY * 2)

        self.from_year_var = tkinter.IntVar(self)
        self.from_year_var.set(int(self.recent_date.year))
        from_year_menu = tkinter.OptionMenu(self, self.from_year_var, *Const.yearList)
        from_year_menu.place(x=Const.searchX, y=Const.searchY)
        self.from_month_var = tkinter.IntVar(self)
        self.from_month_var.set(int(self.recent_date.month))
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
        self.to_year_var.set(int(self.recent_date.year))
        to_year_menu = tkinter.OptionMenu(self, self.to_year_var, *Const.yearList)
        to_year_menu.place(x=Const.searchX + 200, y=Const.searchY)
        self.to_month_var = tkinter.IntVar(self)
        self.to_month_var.set(int(self.recent_date.month))
        self.to_date_var = tkinter.IntVar(self)
        self.to_date_var.set(int(self.recent_date.day))
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
            command=self.get_battle_data,
        )
        search_button.place(
            x=Const.searchX + 200, y=Const.searchY + Const.searchDY * 2.7
        )
        self.favorite_var = tkinter.BooleanVar()
        self.favorite_var.set(False)
        favorite_check = tkinter.Checkbutton(
            self,
            variable=self.favorite_var,
            text="お気に入り",
            command=self.filter_favorites,
        )
        favorite_check.place(
            x=Const.searchX + 270, y=Const.searchY + Const.searchDY * 2.7
        )

        koumoku_label0 = tkinter.Label(
            self,
            text="対戦時間",
        )
        koumoku_label0.place(x=Const.summaryX + 20, y=Const.koumokuY)
        koumoku_label1 = tkinter.Label(
            self,
            text="自分のパーティ",
        )
        koumoku_label1.place(x=Const.myPokemonX, y=Const.koumokuY)
        koumoku_label2 = tkinter.Label(self, text="選出")
        koumoku_label2.place(x=Const.mysensyutuX, y=Const.koumokuY)
        koumoku_label3 = tkinter.Label(self, text="勝敗")
        koumoku_label3.place(x=Const.winLoseX - 20, y=Const.koumokuY)
        koumoku_label4 = tkinter.Label(self, text="相手のパーティ")
        koumoku_label4.place(x=Const.opoPokemonX + 50, y=Const.koumokuY)
        koumoku_label4 = tkinter.Label(self, text="選出")
        koumoku_label4.place(x=Const.opposensyutuX + 50, y=Const.koumokuY)
        koumoku_label5 = tkinter.Label(self, text="TN")
        koumoku_label5.place(x=Const.tnX, y=Const.koumokuY)
        koumoku_label6 = tkinter.Label(self, text="相手の順位")
        koumoku_label6.place(x=Const.rankX, y=Const.koumokuY)

        paging_left_button = tkinter.Button(
            self, text="◀", command=self.click_paging_left
        )
        paging_left_button.place(x=1500, y=Const.koumokuY)
        paging_right_button = tkinter.Button(
            self, text="▶", command=self.click_paging_right
        )
        paging_right_button.place(x=1600, y=Const.koumokuY)

    def get_battle_data(self):
        self.from_date, self.to_date = DB_battle.chenge_date_from_datetime_to_unix(
            self.from_year_var.get(),
            self.from_month_var.get(),
            self.from_date_var.get(),
            self.to_year_var.get(),
            self.to_month_var.get(),
            self.to_date_var.get(),
            self.time9_bln.get(),
        )
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
        if self.party_num != 0 and self.party_subnum != 0:
            self.battle_data_list = DB_battle.get_battle_data_by_date_and_party_subnum(
                self.from_date, self.to_date, self.party_num, self.party_subnum
            )
        elif self.party_num != 0:
            self.battleDataList = DB_battle.get_battle_data_by_date_and_party_num(
                self.from_date, self.to_date, self.party_num
            )
        else:
            self.battle_data_list = DB_battle.get_battle_data_by_date(
                self.from_date, self.to_date
            )
        self.page_num_var.set(1)
        self.update_result()

    def update_result(self):
        self.sensyutu_img_list = []

        self.canvas = tkinter.Canvas(self, width=1800, height=720)
        self.canvas.place(x=0, y=Const.pokemonImageY + 5)
        self.canvas.create_line(
            Const.outlineX,
            Const.outlineY,
            Const.outlineEndX,
            Const.outlineEndY,
            width=2.0,
            tag="line",
        )
        self.canvas.create_line(
            Const.outline2X,
            Const.outlineY,
            Const.outline2X,
            Const.outlineEndY,
            width=2.0,
            tag="line",
        )
        i = (self.page_num_var.get() - 1) * 15

        if self.page_position_label is not None:
            self.page_position_label.destroy()
        if self.page_num_label is not None:
            self.page_num_label.destroy()
        self.page_num_label = tkinter.Label(
            self,
            textvariable=self.page_num_var,
        )
        self.page_num_label.place(x=1540, y=Const.koumokuY)
        self.page_position_label = tkinter.Label(
            self,
            text=f"/ {math.ceil(len(self.battle_data_list) / 15)}",
        )
        self.page_position_label.place(x=1560, y=Const.koumokuY)
        for battle_data in self.battle_data_list[
            (self.page_num_var.get()) * 15 - 15 : (self.page_num_var.get()) * 15
        ]:
            battle_time = datetime.datetime.fromtimestamp(battle_data[1])
            self.canvas.create_text(
                Const.summaryX + 50,
                Const.textStartY + Const.imageStartY + Const.battleDataDY * int(i % 15),
                text=battle_time.strftime("%Y/%m/%d %H:%M"),
            )
            self.display_my_pokemon(battle_data, int(i % 15))
            self.display_my_sensyutu(battle_data, int(i % 15))
            self.display_opo_pokemon(battle_data, int(i % 15))
            self.display_oppo_sensyutu(battle_data, int(i % 15))
            self.canvas.create_text(
                Const.winLoseX,
                Const.textStartY + Const.imageStartY + Const.battleDataDY * int(i % 15),
                text="win" if battle_data[2] == 1 else "lose",
                font=Const.titleFont,
            )
            self.canvas.create_text(
                Const.tnX + Const.tnDX,
                Const.textStartY + Const.imageStartY + Const.battleDataDY * int(i % 15),
                text=battle_data[4],
                font=Const.titleFont,
            )
            if battle_data[5] is not None and battle_data[5] != "":
                rankTxt = str(battle_data[5]) + "位"
            else:
                rankTxt = "-位"
            self.canvas.create_text(
                Const.rankX + Const.rankDX,
                Const.textStartY + Const.imageStartY + Const.battleDataDY * int(i % 15),
                text=rankTxt,
                font=Const.titleFont,
            )
            self.canvas.create_text(
                Const.memoX,
                Const.textStartY + Const.imageStartY + Const.battleDataDY * int(i % 15),
                text=battle_data[6],
                font=Const.smallFont,
            )

            i = i + 1
            if i > (self.page_num_var.get()) * 15 - 1:
                break

    def display_my_sensyutu(self, battle_data, i):
        for index, value in enumerate(range(21, 24)):
            if not (battle_data[value] is None or battle_data[value] == "-1"):
                img = Image.open(Const.createPass(battle_data[value]))
                img = img.resize((40, 40))
                img = ImageTk.PhotoImage(img)
                self.canvas.create_image(
                    Const.mysensyutuX + Const.myPartyDX * index,
                    Const.imageStartY + Const.battleDataDY * i,
                    image=img,
                    anchor=tkinter.NW,
                )
                self.sensyutu_img_list.append(img)

    def display_oppo_sensyutu(self, battle_data, i):
        for index, value in enumerate(range(24, 27)):
            if not (battle_data[value] is None or battle_data[value] == "-1"):
                img = Image.open(Const.createPass(battle_data[value]))
                img = img.resize((40, 40))
                img = ImageTk.PhotoImage(img)
                self.canvas.create_image(
                    Const.opposensyutuX + Const.myPartyDX * index,
                    Const.imageStartY + Const.battleDataDY * i,
                    image=img,
                    anchor=tkinter.NW,
                )
                self.sensyutu_img_list.append(img)

    def display_opo_pokemon(self, battle_data, i):
        for index, value in enumerate(range(15, 21)):
            if not battle_data[value] == "-1":
                img = Image.open(Const.createPass(battle_data[value]))
                img = img.resize((40, 40))
                img = ImageTk.PhotoImage(img)
                self.canvas.create_image(
                    Const.opoPokemonX + Const.myPartyDX * index,
                    Const.imageStartY + Const.battleDataDY * i,
                    image=img,
                    anchor=tkinter.NW,
                )
                self.sensyutu_img_list.append(img)

    def display_my_pokemon(self, battle_data, i):
        for index, value in enumerate(range(9, 15)):
            if not battle_data[value] == "-1":
                img = Image.open(Const.createPass(battle_data[value]))
                img = img.resize((40, 40))
                img = ImageTk.PhotoImage(img)
                self.canvas.create_image(
                    Const.myPokemonX + Const.myPartyDX * index,
                    Const.imageStartY + Const.battleDataDY * i,
                    image=img,
                    anchor=tkinter.NW,
                )
                self.sensyutu_img_list.append(img)

    def filter_favorites(self):
        if self.favorite_var.get():
            self.battle_data_list = [x for x in self.battle_data_list if x[3] == "1"]
            self.page_num_var.set(1)
            self.update_result()
        else:
            self.get_battle_data()

    def click_paging_left(self):
        if self.page_num_var.get() > 1:
            self.sensyutu_img_list = []
            self.page_num_var.set(self.page_num_var.get() - 1)
            self.update_result()

    def click_paging_right(self):
        if self.page_num_var.get() < len(self.battle_data_list) / 15:
            self.canvas.destroy()
            self.sensyutu_img_list = []
            self.page_num_var.set(self.page_num_var.get() + 1)
            self.update_result()
