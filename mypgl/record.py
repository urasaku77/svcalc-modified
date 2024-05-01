import datetime
import math
import tkinter

from PIL import Image, ImageTk

from database.battle import DB_battle
from mypgl.common.const import Const


class Record(tkinter.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("対戦履歴画面")

        self.page_num_var = tkinter.IntVar(value=1)
        self.page_num_label = None
        self.page_position_label = None

        self.battleTimeLabelList = []
        self.sensyutuImgList = []
        self.rankLabelList = []
        self.winLoseLabelList = []
        self.canvasList = []
        self.battleDataList = []

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

        self.displayGui()

    def open(self):
        self.grab_set()
        self.focus_set()
        self.geometry("1800x950")

    def displayGui(self):
        kikanLabel = tkinter.Label(self, text="期間")
        kikanLabel.place(x=Const.searchX, y=Const.searchY - Const.searchDY)
        rankLabel = tkinter.Label(self, text="パーティ絞り込み")
        rankLabel.place(x=Const.searchX, y=Const.searchY + Const.searchDY * 2)
        """FROM時間"""
        fromYearVar = tkinter.IntVar(self)
        fromYearVar.set(int(self.recentDate.year))
        fromYearMenu = tkinter.OptionMenu(self, fromYearVar, *Const.yearList)
        fromYearMenu.place(x=Const.searchX, y=Const.searchY)
        fromMonthVar = tkinter.IntVar(self)
        fromMonthVar.set(int(self.recentDate.month))
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
        toYearVar.set(int(self.recentDate.year))
        toYearMenu = tkinter.OptionMenu(self, toYearVar, *Const.yearList)
        toYearMenu.place(x=Const.searchX + 200, y=Const.searchY)
        toMonthVar = tkinter.IntVar(self)
        toMonthVar.set(int(self.recentDate.month))
        toDateVar = tkinter.IntVar(self)
        toDateVar.set(int(self.recentDate.day))
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
            command=lambda: self.get_battle_data(
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
        koumokuLabel0 = tkinter.Label(
            self,
            text="対戦時間",
        )
        koumokuLabel0.place(x=Const.summaryX + 20, y=Const.koumokuY)
        koumokuLabel1 = tkinter.Label(
            self,
            text="自分のパーティ",
        )
        koumokuLabel1.place(x=Const.myPokemonX, y=Const.koumokuY)
        koumokuLabel2 = tkinter.Label(self, text="選出")
        koumokuLabel2.place(x=Const.mysensyutuX, y=Const.koumokuY)
        koumokuLabel3 = tkinter.Label(self, text="勝敗")
        koumokuLabel3.place(x=Const.winLoseX - 20, y=Const.koumokuY)
        koumokuLabel4 = tkinter.Label(self, text="相手のパーティ")
        koumokuLabel4.place(x=Const.opoPokemonX + 50, y=Const.koumokuY)
        koumokuLabel4 = tkinter.Label(self, text="選出")
        koumokuLabel4.place(x=Const.opposensyutuX + 50, y=Const.koumokuY)
        koumokuLabel5 = tkinter.Label(self, text="TN")
        koumokuLabel5.place(x=Const.tnX, y=Const.koumokuY)
        koumokuLabel6 = tkinter.Label(self, text="相手の順位")
        koumokuLabel6.place(x=Const.rankX, y=Const.koumokuY)

        pagingLeftButton = tkinter.Button(self, text="◀", command=self.clickPagingLeft)
        pagingLeftButton.place(x=1500, y=Const.koumokuY)
        pagingRightButton = tkinter.Button(
            self, text="▶", command=self.clickPagingRight
        )
        pagingRightButton.place(x=1600, y=Const.koumokuY)

    def get_battle_data(
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
        if (
            self.numTxt.get() is not None
            and self.numTxt.get() != ""
            and self.subNumTxt.get() is not None
            and self.subNumTxt.get() != ""
        ):
            self.battleDataList = DB_battle.get_battle_data_by_date_and_party_subnum(
                self.from_date, self.to_date, self.numTxt.get(), self.subNumTxt.get()
            )
        elif self.numTxt.get() is not None and self.numTxt.get() != "":
            self.battleDataList = DB_battle.get_battle_data_by_date_and_party_num(
                self.from_date, self.to_date, self.numTxt.get()
            )
        else:
            self.battleDataList = DB_battle.get_battle_data_by_date(
                self.from_date, self.to_date
            )
        self.page_num_var.set(1)
        self.updateSummary()

    def updateSummary(self):
        self.sensyutuImgList = []

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
            text=f"/ {math.ceil(len(self.battleDataList) / 15)}",
        )
        self.page_position_label.place(x=1560, y=Const.koumokuY)
        for battleData in self.battleDataList[
            (self.page_num_var.get()) * 15 - 15 : (self.page_num_var.get()) * 15
        ]:
            battleTime = datetime.datetime.fromtimestamp(battleData[1])
            self.canvas.create_text(
                Const.summaryX + 50,
                Const.textStartY + Const.imageStartY + Const.battleDataDY * int(i % 15),
                text=battleTime.strftime("%Y/%m/%d %H:%M"),
            )
            self.displayMyPokemon(battleData, int(i % 15))
            self.displayMySensyutu(battleData, int(i % 15))
            self.displayOpoPokemon(battleData, int(i % 15))
            self.displayOppoSensyutu(battleData, int(i % 15))
            self.canvas.create_text(
                Const.winLoseX,
                Const.textStartY + Const.imageStartY + Const.battleDataDY * int(i % 15),
                text="win" if battleData[2] == 1 else "lose",
                font=Const.titleFont,
            )
            self.canvas.create_text(
                Const.tnX + Const.tnDX,
                Const.textStartY + Const.imageStartY + Const.battleDataDY * int(i % 15),
                text=battleData[4],
                font=Const.titleFont,
            )
            if battleData[5] is not None and battleData[5] != "":
                rankTxt = str(battleData[5]) + "位"
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
                text=battleData[6],
                font=Const.smallFont,
            )

            i = i + 1
            if i > (self.page_num_var.get()) * 15 - 1:
                break

    def displayMySensyutu(self, battleData, i):
        if not (battleData[21] is None or battleData[21] == "-1"):
            img = Image.open(Const.createPass(battleData[21]))
            img = img.resize((40, 40))
            img = ImageTk.PhotoImage(img)
            self.canvas.create_image(
                Const.mysensyutuX,
                Const.imageStartY + Const.battleDataDY * i,
                image=img,
                anchor=tkinter.NW,
            )
            self.sensyutuImgList.append(img)
        if not (battleData[22] is None or battleData[22] == "-1"):
            img = Image.open(Const.createPass(battleData[22]))
            img = img.resize((40, 40))
            img = ImageTk.PhotoImage(img)
            self.canvas.create_image(
                Const.mysensyutuX + Const.myPartyDX,
                Const.imageStartY + Const.battleDataDY * i,
                image=img,
                anchor=tkinter.NW,
            )
            self.sensyutuImgList.append(img)
        if not (battleData[23] is None or battleData[23] == "-1"):
            img = Image.open(Const.createPass(battleData[23]))
            img = img.resize((40, 40))
            img = ImageTk.PhotoImage(img)
            self.canvas.create_image(
                Const.mysensyutuX + Const.myPartyDX * 2,
                Const.imageStartY + Const.battleDataDY * i,
                image=img,
                anchor=tkinter.NW,
            )
            self.sensyutuImgList.append(img)

    def displayOppoSensyutu(self, battleData, i):
        if not (battleData[24] is None or battleData[24] == "-1"):
            img = Image.open(Const.createPass(battleData[24]))
            img = img.resize((40, 40))
            img = ImageTk.PhotoImage(img)
            self.canvas.create_image(
                Const.opposensyutuX,
                Const.imageStartY + Const.battleDataDY * i,
                image=img,
                anchor=tkinter.NW,
            )
            self.sensyutuImgList.append(img)
        if not (battleData[25] is None or battleData[25] == "-1"):
            img = Image.open(Const.createPass(battleData[25]))
            img = img.resize((40, 40))
            img = ImageTk.PhotoImage(img)
            self.canvas.create_image(
                Const.opposensyutuX + Const.myPartyDX,
                Const.imageStartY + Const.battleDataDY * i,
                image=img,
                anchor=tkinter.NW,
            )
            self.sensyutuImgList.append(img)
        if not (battleData[26] is None or battleData[26] == "-1"):
            img = Image.open(Const.createPass(battleData[26]))
            img = img.resize((40, 40))
            img = ImageTk.PhotoImage(img)
            self.canvas.create_image(
                Const.opposensyutuX + Const.myPartyDX * 2,
                Const.imageStartY + Const.battleDataDY * i,
                image=img,
                anchor=tkinter.NW,
            )
            self.sensyutuImgList.append(img)

    def displayOpoPokemon(self, battleData, i):
        if not battleData[15] == "-1":
            img = Image.open(Const.createPass(battleData[15]))
            img = img.resize((40, 40))
            img = ImageTk.PhotoImage(img)
            self.canvas.create_image(
                Const.opoPokemonX,
                Const.imageStartY + Const.battleDataDY * i,
                image=img,
                anchor=tkinter.NW,
            )
            self.sensyutuImgList.append(img)
        if not battleData[16] == "-1":
            img = Image.open(Const.createPass(battleData[16]))
            img = img.resize((40, 40))
            img = ImageTk.PhotoImage(img)
            self.canvas.create_image(
                Const.opoPokemonX + Const.myPartyDX,
                Const.imageStartY + Const.battleDataDY * i,
                image=img,
                anchor=tkinter.NW,
            )
            self.sensyutuImgList.append(img)
        if not battleData[17] == "-1":
            img = Image.open(Const.createPass(battleData[17]))
            img = img.resize((40, 40))
            img = ImageTk.PhotoImage(img)
            self.canvas.create_image(
                Const.opoPokemonX + Const.myPartyDX * 2,
                Const.imageStartY + Const.battleDataDY * i,
                image=img,
                anchor=tkinter.NW,
            )
            self.sensyutuImgList.append(img)
        if not battleData[18] == "-1":
            img = Image.open(Const.createPass(battleData[18]))
            img = img.resize((40, 40))
            img = ImageTk.PhotoImage(img)
            self.canvas.create_image(
                Const.opoPokemonX + Const.myPartyDX * 3,
                Const.imageStartY + Const.battleDataDY * i,
                image=img,
                anchor=tkinter.NW,
            )
            self.sensyutuImgList.append(img)
        if not battleData[19] == "-1":
            img = Image.open(Const.createPass(battleData[19]))
            img = img.resize((40, 40))
            img = ImageTk.PhotoImage(img)
            self.canvas.create_image(
                Const.opoPokemonX + Const.myPartyDX * 4,
                Const.imageStartY + Const.battleDataDY * i,
                image=img,
                anchor=tkinter.NW,
            )
            self.sensyutuImgList.append(img)
        if not battleData[20] == "-1":
            img = Image.open(Const.createPass(battleData[20]))
            img = img.resize((40, 40))
            img = ImageTk.PhotoImage(img)
            self.canvas.create_image(
                Const.opoPokemonX + Const.myPartyDX * 5,
                Const.imageStartY + Const.battleDataDY * i,
                image=img,
                anchor=tkinter.NW,
            )
            self.sensyutuImgList.append(img)

    def displayMyPokemon(self, battleData, i):
        if not battleData[9] == "-1":
            img = Image.open(Const.createPass(battleData[9]))
            img = img.resize((40, 40))
            img = ImageTk.PhotoImage(img)
            self.canvas.create_image(
                Const.myPokemonX,
                Const.imageStartY + Const.battleDataDY * i,
                image=img,
                anchor=tkinter.NW,
            )
            self.sensyutuImgList.append(img)
        if not battleData[10] == "-1":
            img = Image.open(Const.createPass(battleData[10]))
            img = img.resize((40, 40))
            img = ImageTk.PhotoImage(img)
            self.canvas.create_image(
                Const.myPokemonX + Const.myPartyDX,
                Const.imageStartY + Const.battleDataDY * i,
                image=img,
                anchor=tkinter.NW,
            )
            self.sensyutuImgList.append(img)
        if not battleData[11] == "-1":
            img = Image.open(Const.createPass(battleData[11]))
            img = img.resize((40, 40))
            img = ImageTk.PhotoImage(img)
            self.canvas.create_image(
                Const.myPokemonX + Const.myPartyDX * 2,
                Const.imageStartY + Const.battleDataDY * i,
                image=img,
                anchor=tkinter.NW,
            )
            self.sensyutuImgList.append(img)
        if not battleData[12] == "-1":
            img = Image.open(Const.createPass(battleData[12]))
            img = img.resize((40, 40))
            img = ImageTk.PhotoImage(img)
            self.canvas.create_image(
                Const.myPokemonX + Const.myPartyDX * 3,
                Const.imageStartY + Const.battleDataDY * i,
                image=img,
                anchor=tkinter.NW,
            )
            self.sensyutuImgList.append(img)
        if not battleData[13] == "-1":
            img = Image.open(Const.createPass(battleData[13]))
            img = img.resize((40, 40))
            img = ImageTk.PhotoImage(img)
            self.canvas.create_image(
                Const.myPokemonX + Const.myPartyDX * 4,
                Const.imageStartY + Const.battleDataDY * i,
                image=img,
                anchor=tkinter.NW,
            )
            self.sensyutuImgList.append(img)
        if not battleData[14] == "-1":
            img = Image.open(Const.createPass(battleData[14]))
            img = img.resize((40, 40))
            img = ImageTk.PhotoImage(img)
            self.canvas.create_image(
                Const.myPokemonX + Const.myPartyDX * 5,
                Const.imageStartY + Const.battleDataDY * i,
                image=img,
                anchor=tkinter.NW,
            )
            self.sensyutuImgList.append(img)

    def clickPagingLeft(self):
        if self.page_num_var.get() > 1:
            self.sensyutuImgList = []
            self.page_num_var.set(self.page_num_var.get() - 1)
            self.updateSummary()

    def clickPagingRight(self):
        if self.page_num_var.get() < len(self.battleDataList) / 15:
            self.canvas.destroy()
            self.sensyutuImgList = []
            self.page_num_var.set(self.page_num_var.get() + 1)
            self.updateSummary()
