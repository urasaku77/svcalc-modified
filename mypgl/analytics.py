import datetime
import tkinter

from PIL import Image, ImageTk

from database.battle import DB_battle
from mypgl.common.const import Const


class Analytics(tkinter.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("myPGL")

        beforeRecentDate = DB_battle.get_recent_date()[0]
        self.recentDate = (
            datetime.date(
                datetime.datetime.fromtimestamp(beforeRecentDate).year,
                datetime.datetime.fromtimestamp(beforeRecentDate).month,
                datetime.datetime.fromtimestamp(beforeRecentDate).day,
            )
            if beforeRecentDate is not None
            else datetime.datetime.today()
        )
        self.party_num = 0
        self.party_subnum = 0
        self.imgList = []
        self.kpList = []
        self.kpLabelList = []
        self.winRateLabelList = []
        self.canvasList = []
        self.recordCountLabel = None
        self.wholeWinRateLabel = None

        self.createSearch(self.recentDate)
        self.searchKP(
            int(self.recentDate.year),
            int(self.recentDate.month),
            1,
            int(self.recentDate.year),
            int(self.recentDate.month),
            int(self.recentDate.day),
            True,
        )

        for i in range(50):
            rankLabel = tkinter.Label(self, text=str(i + 1) + "位")
            rankLabel.place(x=Const.list2[i][1] - 40, y=Const.list2[i][2])

    def open(self):
        self.grab_set()
        self.focus_set()
        self.geometry("1280x720")

    def createSearch(self, searchDate: datetime.datetime):
        kikanLabel = tkinter.Label(self, text="期間")
        kikanLabel.place(x=Const.searchX, y=Const.searchY - Const.searchDY)
        rankLabel = tkinter.Label(self, text="パーティ絞り込み")
        rankLabel.place(x=Const.searchX, y=Const.searchY + Const.searchDY * 2)
        """FROM時間"""
        fromYearVar = tkinter.IntVar(self)
        fromYearVar.set(int(searchDate.year))
        fromYearMenu = tkinter.OptionMenu(self, fromYearVar, *Const.yearList)
        fromYearMenu.place(x=Const.searchX, y=Const.searchY)
        fromMonthVar = tkinter.IntVar(self)
        fromMonthVar.set(int(searchDate.month))
        fromDateVar = tkinter.IntVar(self)
        fromDateVar.set(1)
        fromMonthMenu = tkinter.OptionMenu(self, fromMonthVar, *Const.monthList)
        fromMonthMenu.place(x=Const.searchX + 70, y=Const.searchY)
        fromDateMenu = tkinter.OptionMenu(self, fromDateVar, *Const.dateList)
        fromDateMenu.place(x=Const.searchX + 120, y=Const.searchY)

        mackLabel = tkinter.Label(self, text=" ~ ", font=Const.titleFont)
        mackLabel.place(x=Const.searchX + 170, y=Const.searchY)

        """TO時間"""
        toYearVar = tkinter.IntVar(self)
        toYearVar.set(int(searchDate.year))
        toYearMenu = tkinter.OptionMenu(self, toYearVar, *Const.yearList)
        toYearMenu.place(x=Const.searchX + 200, y=Const.searchY)
        toMonthVar = tkinter.IntVar(self)
        toMonthVar.set(int(searchDate.month))
        toDateVar = tkinter.IntVar(self)
        toDateVar.set(int(searchDate.day))
        toMonthMenu = tkinter.OptionMenu(self, toMonthVar, *Const.monthList)
        toMonthMenu.place(x=Const.searchX + 270, y=Const.searchY)
        toDateMenu = tkinter.OptionMenu(self, toDateVar, *Const.dateList)
        toDateMenu.place(x=Const.searchX + 330, y=Const.searchY)
        """初日を9時以降にする"""
        time9Bln = tkinter.BooleanVar()
        time9Bln.set(True)
        time9Check = tkinter.Checkbutton(
            self, variable=time9Bln, text="初日を9時以降にする"
        )
        time9Check.place(x=Const.searchX + 400, y=Const.searchY)
        numLabel = tkinter.Label(self, text="番号")
        numLabel.place(x=Const.searchX, y=Const.searchY + Const.searchDY * 3)
        self.numTxt = tkinter.Entry(self, width=Const.txtboxWidth)
        self.numTxt.place(x=Const.searchX + 40, y=Const.searchY + Const.searchDY * 3)
        subNumLabel = tkinter.Label(self, text="連番")
        subNumLabel.place(x=Const.searchX + 90, y=Const.searchY + Const.searchDY * 3)
        self.subNumTxt = tkinter.Entry(self, width=Const.txtboxWidth)
        self.subNumTxt.place(
            x=Const.searchX + 130, y=Const.searchY + Const.searchDY * 3
        )
        searchButton = tkinter.Button(
            self,
            text="検索",
            command=lambda: self.searchKP(
                fromYearVar.get(),
                fromMonthVar.get(),
                fromDateVar.get(),
                toYearVar.get(),
                toMonthVar.get(),
                toDateVar.get(),
                time9Bln.get(),
            ),
        )
        searchButton.place(
            x=Const.searchX + 200, y=Const.searchY + Const.searchDY * 2.7
        )
        self.title_var = tkinter.StringVar()
        self.title_var.set("KPと勝率")
        self.mainTitleLabel = tkinter.Button(
            self,
            textvariable=self.title_var,
            font=Const.titleFont,
            state="disable",
            command=self.change_mode,
        )
        self.mainTitleLabel.place(x=Const.kpStartX, y=Const.kpStartY - 60)
        self.subtitle_var = tkinter.StringVar()
        self.subtitle_var.set("直近使用したパーティ")
        self.subTitleLabel = tkinter.Label(
            self, textvariable=self.subtitle_var, font=Const.titleFont
        )
        self.subTitleLabel.place(x=Const.myPartyStartX, y=Const.myPartyStartY - 30)

    def searchKP(
        self,
        fromYear,
        fromMonth,
        fromDate,
        toYear,
        toMonth,
        toDate,
        time9Bl,
    ):
        self.from_date, self.to_date = DB_battle.chenge_date_from_datetime_to_unix(
            fromYear,
            fromMonth,
            fromDate,
            toYear,
            toMonth,
            toDate,
            time9Bl,
        )
        self.delete_result_page()
        if (
            self.numTxt.get() is not None
            and self.numTxt.get() != ""
            and self.subNumTxt.get() is not None
            and self.subNumTxt.get() != ""
        ):
            list1 = DB_battle.calc_kp_for_party_subnum(
                self.from_date, self.to_date, self.numTxt.get(), self.subNumTxt.get()
            )
            self.kpList = list1
            self.recordCount = DB_battle.count_record_for_party_subnum(
                self.from_date, self.to_date, self.numTxt.get(), self.subNumTxt.get()
            )
            self.winCount = DB_battle.count_win_for_party_subnum(
                self.from_date, self.to_date, self.numTxt.get(), self.subNumTxt.get()
            )
            self.displayWinRateForPartySubnum(
                self.from_date, self.to_date, self.numTxt.get(), self.subNumTxt.get()
            )
            self.party_num = int(self.numTxt.get())
            self.party_subnum = int(self.subNumTxt.get())
        elif self.numTxt.get() is not None and self.numTxt.get() != "":
            list1 = DB_battle.calc_kp_for_party_num(
                self.from_date, self.to_date, self.numTxt.get()
            )
            self.kpList = list1
            self.recordCount = DB_battle.count_record_for_party_num(
                self.from_date, self.to_date, self.numTxt.get()
            )
            self.winCount = DB_battle.count_win_for_party_num(
                self.from_date, self.to_date, self.numTxt.get()
            )
            self.displayWinRateForPartyNum(
                self.from_date, self.to_date, self.numTxt.get()
            )
            self.party_num = int(self.numTxt.get())
            self.party_subnum = 0
        else:
            list1 = DB_battle.calc_kp(self.from_date, self.to_date)
            self.kpList = list1
            self.recordCount = DB_battle.count_record(self.from_date, self.to_date)
            self.winCount = DB_battle.count_win(self.from_date, self.to_date)
            self.displayWinRate(self.from_date, self.to_date)
            self.party_num = 0
            self.party_subnum = 0
        self.displayKP(self.kpList, self.recordCount)
        self.recordCountLabel = tkinter.Label(
            self,
            text="対戦数：" + str(self.recordCount[0]),
            font=Const.titleFont,
        )
        self.recordCountLabel.place(x=Const.myPartyStartX + 50, y=Const.searchY)
        wholeWinRate = (
            self.winCount[0] * 100 / self.recordCount[0]
            if self.recordCount[0] != 0
            else 0
        )
        self.wholeWinRateLabel = tkinter.Label(
            self,
            text=str("勝率：" + "{:.1f}".format(wholeWinRate)) + "%",
            font=Const.titleFont,
        )
        self.wholeWinRateLabel.place(
            x=Const.myPartyStartX + 50, y=Const.searchY + Const.searchDY * 2
        )
        self.displayPartyDetail()

    def displayKP(self, list1, recordCount):
        i = 0
        for list in list1:
            if len(list[0]) < 1:
                break
            if recordCount[0] == 0:
                recordCount = (-1,)
            img = Image.open(Const.createPass(list[0]))
            img = img.resize((40, 40))
            img = ImageTk.PhotoImage(img)
            canvas = tkinter.Canvas(self, width=50, height=50)
            canvas.place(x=Const.list2[i][1], y=Const.list2[i][2] + 10)
            canvas.create_image(5, 5, image=img, anchor=tkinter.NW)
            self.kpLabel = tkinter.Label(
                self,
                text=str("{:.1f}".format((int(list[1]) * 100 / int(recordCount[0]))))
                + "%",
            )
            self.kpLabel.place(x=Const.list2[i][1] - 40, y=Const.list2[i][2] + 20)
            self.imgList.append(img)
            self.canvasList.append(canvas)
            self.kpLabelList.append(self.kpLabel)
            i = i + 1
            if i > 49:
                break

    def displayWinRate(self, from_date, to_date):
        self.title_var.set("KPと勝率")
        self.mainTitleLabel["state"] = "disable"
        winRateList = DB_battle.get_win_rate(self.kpList, from_date, to_date)
        i = 0
        for winRate in winRateList:
            kpLabel = tkinter.Label(
                self, text=str("{:.1f}".format(winRate * 100)) + "%"
            )
            kpLabel.place(x=Const.list2[i][1] - 40, y=Const.list2[i][2] + 40)
            self.winRateLabelList.append(kpLabel)
            i = i + 1
            if i > 49:
                break

    def displayWinRateForPartyNum(self, from_date, to_date, party_num):
        self.title_var.set("KPと勝率")
        self.mainTitleLabel["state"] = "normal"
        winRateList = DB_battle.get_win_rate_for_party_num(
            self.kpList, from_date, to_date, party_num
        )
        i = 0
        for winRate in winRateList:
            kpLabel = tkinter.Label(
                self, text=str("{:.1f}".format(winRate * 100)) + "%"
            )
            kpLabel.place(x=Const.list2[i][1] - 40, y=Const.list2[i][2] + 40)
            self.winRateLabelList.append(kpLabel)
            i = i + 1
            if i > 49:
                break

    def displayWinRateForPartySubnum(self, from_date, to_date, party_num, party_subnum):
        self.title_var.set("KPと勝率")
        self.mainTitleLabel["state"] = "normal"
        winRateList = DB_battle.get_win_rate_for_party_subnum(
            self.kpList, from_date, to_date, party_num, party_subnum
        )
        i = 0
        for winRate in winRateList:
            kpLabel = tkinter.Label(
                self, text=str("{:.1f}".format(winRate * 100)) + "%"
            )
            kpLabel.place(x=Const.list2[i][1] - 40, y=Const.list2[i][2] + 40)
            self.winRateLabelList.append(kpLabel)
            i = i + 1
            if i > 49:
                break

    def change_mode(self):
        self.delete_result()
        if self.title_var.get() == "KPと勝率":
            self.title_var.set("選出と勝率")
            chosenRateList = (
                DB_battle.get_oppo_chosen_rate_for_party_num(
                    self.kpList, self.from_date, self.to_date, self.party_num
                )
                if self.party_subnum == 0
                else DB_battle.get_oppo_chosen_rate_for_party_subnum(
                    self.kpList,
                    self.from_date,
                    self.to_date,
                    self.party_num,
                    self.party_subnum,
                )
            )
            winRateList = (
                DB_battle.get_oppo_chosen_and_win_rate_for_party_num(
                    self.kpList, self.from_date, self.to_date, self.party_num
                )
                if self.party_subnum == 0
                else DB_battle.get_oppo_chosen_and_win_rate_for_party_subnum(
                    self.kpList,
                    self.from_date,
                    self.to_date,
                    self.party_num,
                    self.party_subnum,
                )
            )

            for i in range(len(chosenRateList)):
                self.kpLabel = tkinter.Label(
                    self,
                    text=str("{:.1f}".format(chosenRateList[i] * 100)) + "%",
                )
                self.kpLabel.place(x=Const.list2[i][1] - 40, y=Const.list2[i][2] + 20)
                self.kpLabelList.append(self.kpLabel)

                kpLabel = tkinter.Label(
                    self, text=str("{:.1f}".format(winRateList[i] * 100)) + "%"
                )
                kpLabel.place(x=Const.list2[i][1] - 40, y=Const.list2[i][2] + 40)
                self.winRateLabelList.append(kpLabel)
                if i + 1 > 49:
                    break

        elif self.title_var.get() == "選出と勝率":
            self.title_var.set("初手と勝率")
            chosenRateList = (
                DB_battle.get_oppo_first_chosen_rate_for_party_num(
                    self.kpList, self.from_date, self.to_date, self.party_num
                )
                if self.party_subnum == 0
                else DB_battle.get_oppo_first_chosen_rate_for_party_subnum(
                    self.kpList,
                    self.from_date,
                    self.to_date,
                    self.party_num,
                    self.party_subnum,
                )
            )
            winRateList = (
                DB_battle.get_oppo_first_chosen_and_win_rate_for_party_num(
                    self.kpList, self.from_date, self.to_date, self.party_num
                )
                if self.party_subnum == 0
                else DB_battle.get_oppo_first_chosen_and_win_rate_for_party_subnum(
                    self.kpList,
                    self.from_date,
                    self.to_date,
                    self.party_num,
                    self.party_subnum,
                )
            )

            for i in range(len(chosenRateList)):
                self.kpLabel = tkinter.Label(
                    self,
                    text=str("{:.1f}".format(chosenRateList[i] * 100)) + "%",
                )
                self.kpLabel.place(x=Const.list2[i][1] - 40, y=Const.list2[i][2] + 20)
                self.kpLabelList.append(self.kpLabel)

                kpLabel = tkinter.Label(
                    self, text=str("{:.1f}".format(winRateList[i] * 100)) + "%"
                )
                kpLabel.place(x=Const.list2[i][1] - 40, y=Const.list2[i][2] + 40)
                self.winRateLabelList.append(kpLabel)
                if i + 1 > 49:
                    break

        elif self.title_var.get() == "初手と勝率":
            self.title_var.set("KPと勝率")
            self.displayWinRateForPartyNum(
                self.from_date, self.to_date, self.party_num
            ) if self.party_subnum == 0 else self.displayWinRateForPartySubnum(
                self.from_date, self.to_date, self.party_num, self.party_subnum
            )
            self.displayKP(self.kpList, self.recordCount)

    def displayPartyDetail(self):
        partyCanvas = tkinter.Canvas(self, width=350, height=600)
        partyCanvas.place(x=0, y=Const.myPartyStartY)

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
                    self.imgList.append(img)
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
                self.displayMyParty()

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
                    self.imgList.append(img)
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
                self.displayMyParty()
        else:
            self.displayMyParty()

    def displayMyParty(self):
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
                    self.imgList.append(img)

    def delete_result_page(self):
        if self.recordCountLabel is not None:
            self.recordCountLabel.destroy()
        if self.wholeWinRateLabel is not None:
            self.wholeWinRateLabel.destroy()
        if self.kpLabelList is not []:
            for kpLabel in self.kpLabelList:
                kpLabel.destroy()
                self.kpLabelList = []
        if self.winRateLabelList is not []:
            for winRateLabel in self.winRateLabelList:
                winRateLabel.destroy()
                self.winRateLabel = []
        if self.canvasList is not []:
            for canvas in self.canvasList:
                canvas.delete("all")
                self.canvasList = []

    def delete_result(self):
        if self.kpLabelList is not []:
            for kpLabel in self.kpLabelList:
                kpLabel.destroy()
                self.kpLabelList = []
        if self.winRateLabelList is not []:
            for winRateLabel in self.winRateLabelList:
                winRateLabel.destroy()
                self.winRateLabel = []
