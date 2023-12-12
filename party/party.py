# coding: utf-8

import csv
import glob
import os
from tkinter import N, E, W, S, filedialog, messagebox
from tkinter import ttk
import tkinter
from tkinter.scrolledtext import ScrolledText

from component import images
from component.button import TypeButton, MyButton
from component.combobox import AutoCompleteCombobox, ModifiedEntry, MyCombobox, WazaNameCombobox
from component.const import ALL_ITEM_COMBOBOX_VALUES
from component.dialog import TypeSelectDialog
from component.label import MyLabel
from pokedata.const import Types
from pokedata.nature import get_seikaku_hosei, get_seikaku_list
from pokedata.pokemon import Pokemon
from pokedata.stats import StatsKey

# パーティCSV編集用ダイアログ
class PartyEditor(tkinter.Toplevel):
    
    def __init__(self, title: str = "パーティ編集", width: int = 400, height: int = 300):
        super().__init__()
        self.title(title)
        
        main_frame = ttk.Frame(self, padding=5)
        main_frame.grid(row=0, column=0, sticky=N+E+W+S)
        
        self.settings = PartySettings(main_frame, padding=5)
        self.settings.grid(row=0, column=0, columnspan=2, sticky=N+E+W+S)
        
        self.read_csv_button = MyButton(main_frame, text="CSV読み込み", command=self.select_csv)
        self.read_csv_button.grid(row=0, column=2, padx=5, pady=5, sticky=N+S+W)

        self.read_csv_button = MyButton(main_frame, text="CSV書き込み", command=self.save_csv)
        self.read_csv_button.grid(row=0, column=2, padx=5, pady=5, sticky=N+S)

        self.all_clear_button = MyButton(main_frame, text="全クリア", command=self.all_clear)
        self.all_clear_button.grid(row=0, column=2, padx=5, pady=5, sticky=N+S+E)

        self.using = UseParty(main_frame, text="使用するパーティ", padding=5)
        self.using.grid(row=0, column=3, columnspan=2, sticky=N+E+W+S)

        self.pokemons = PokemonEditors(main_frame, text="パーティ編集", padding=5)
        self.pokemons.grid(row=1, column=0, columnspan=5, sticky=N+E+W+S)
        
        self.select_csv(csv=self.using.using_var.get())

    def save_csv(self):
        ret = messagebox.askyesno('確認', '表示されているデータをCSV書き込みますか？\n（既存のファイルの場合は上書きされます）')
        if ret == False:
            return
        self.title = self.settings.title_entry.get()
        self.num = self.settings.num_entry.get()
        self.sub_num = self.settings.sub_num_entry.get()

        if self.title == "":
            return
        
        # 新規登録時の採番処理
        file_list = sorted(glob.glob("party/csv/*"))
        last_file = file_list[len(file_list)-1]
        if self.num == "":
            self.num = str(int(last_file.replace('party/csv\\', '')[0])+1)
            self.sub_num = "0"
        elif self.sub_num == "":
            same_num_list= [file for file in file_list if file.startswith('party/csv\\'+self.num+"-")]
            last_same_num_file=sorted(same_num_list)[len(same_num_list)-1]
            self.sub_num = str(int(last_same_num_file.split("-")[1][0])+1)

        # CSV書き込み処理
        filepath = "party\\csv\\"+self.num + "-" + self.sub_num + "_" + self.title + ".csv"
        with open(filepath, 'w') as party_csv:
            writer = csv.writer(party_csv, lineterminator="\n")
            writer.writerow(["名前", "個体値", "努力値", "性格", "持ち物", "特性", "テラス", "技", "技", "技", "技"])
            for pokemon in self.pokemons.pokemon_panel_list:
                row = pokemon.set_csv_row()
                writer.writerow(row)

        # メモ書き込み処理
        self.memo = self.settings.memo.get("1.0", "end-1c")
        with open("party\\txt\\"+self.num + "-" + self.sub_num + "_" + self.title + ".txt", 'w') as txt:
            txt.write(self.memo)
            txt.close()

        # 使用するパーティ変更処理
        if self.settings.is_use_var.get():
            self.using.change_csv(value=filepath.split("party\\csv\\")[1])

    def select_csv(self, csv:str=""):
        if csv == "":
            typ = [('','*.csv')] 
            current_directory = os.getcwd()
            fle = filedialog.askopenfilename(filetypes = typ, initialdir = os.path.join(current_directory, 'party', "csv")) 
            if fle == "":
                return

            csv = fle.split('party/csv/')[1]
        
        self.settings.clear_setting()

        self.settings.num_entry.insert(0, csv.split("-")[0])
        self.settings.sub_num_entry.insert(0, csv.split("-")[1].split("_")[0])
        self.settings.title_entry.insert(0, csv.split("-")[1].split("_")[1].split(".")[0])
        memo_file= "party\\txt\\" + csv.replace("csv","txt")
        with open(memo_file, 'r') as txt:
            self.memo = txt.read()
            txt.close()
        self.settings.memo.insert(tkinter.END, self.memo)
        self.settings.is_use_var.set(True) if csv == self.using.using_var.get() else self.settings.is_use_var.set(False) 

        from pokedata.loader import get_party_data
        for i, data in enumerate(get_party_data(file_path='party/csv/' + csv)):
            pokemon: Pokemon = Pokemon.by_name(data[0])
            pokemon.set_load_data(data, True)
            self.pokemons.pokemon_panel_list[i].set_pokemon(pokemon)
            self.pokemons.pokemon_panel_list[i].change_ev()
    
    def all_clear(self):
        ret = messagebox.askyesno('確認', '表示されているデータをすべてクリアしますか？')
        if ret == True:
            self.settings.clear_setting()
            for pokemon in self.pokemons.pokemon_panel_list:
                pokemon.clear_pokemon()

    def open(self, location=tuple[int, int]):
        self.grab_set()
        self.focus_set()
        self.geometry("+{0}+{1}".format(location[0], location[1]))


class PartySettings(ttk.Frame):

    def on_validate_4(self, P, V):
        if P.isdigit() or P == "":
            return len(P) <= 4
        else:
            return False

    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)
        self.validate_cmd_4 = self.register(self.on_validate_4)
        
        self.edit_frame = ttk.LabelFrame(master=self, text="パーティ情報")
        self.edit_frame.pack(side="left")
                
        self.num_label = ttk.Label(self.edit_frame, text="番号")
        self.num_label.grid(row=0, column=0, sticky=N+S, padx=3)
        self.num_entry = ModifiedEntry(self.edit_frame, validate="key", width=8, validatecommand=(self.validate_cmd_4, "%P", "%V"))
        self.num_entry.grid(row=0, column=1, sticky=E+W)
        
        self.sub_num_label = ttk.Label(self.edit_frame, text="連番")
        self.sub_num_label.grid(row=0, column=2, sticky=N+E+W+S, padx=3, pady=3)
        self.sub_num_entry = ModifiedEntry(self.edit_frame, validate="key", width=8, validatecommand=(self.validate_cmd_4, "%P", "%V"))
        self.sub_num_entry.grid(row=0, column=3, sticky=E+W, padx=3, pady=3)
        
        self.is_use_var = tkinter.BooleanVar()
        self.is_use_check = tkinter.Checkbutton(self.edit_frame, variable=self.is_use_var, text="使用するパーティに設定")
        self.is_use_check.grid(row=0, column=4, sticky=N+E+W+S, padx=3, pady=3)
        
        self.title_label = ttk.Label(self.edit_frame, text="タイトル")
        self.title_label.grid(row=1, column=0, sticky=N+E+W+S, padx=3, pady=3)
        self.title_entry = tkinter.Entry(self.edit_frame)
        self.title_entry.grid(row=1, column=1, columnspan=4, sticky=N+E+W+S, padx=3, pady=3)
        
        self.memo_label = ttk.Label(self.edit_frame, text="メモ")
        self.memo_label.grid(column=5, row=0, rowspan=2, sticky=N+E+W+S)
        self.memo = ScrolledText(self.edit_frame, height=3, width=60, padx=3, pady=3)
        self.memo.grid(column=6, row=0, columnspan=4, rowspan=2, sticky=N+E+W+S)
    
    def clear_setting(self):
        self.num_entry.delete(0, tkinter.END)
        self.sub_num_entry.delete(0, tkinter.END)
        self.is_use_var.set(False)
        self.title_entry.delete(0, tkinter.END)
        self.memo.delete("1.0", tkinter.END)


class UseParty(ttk.LabelFrame):
    
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)
        self.grid_columnconfigure([0, 1, 2, 3], weight=1)
        self.grid_rowconfigure([0, 1], weight=1)
        
        self.using_var = tkinter.StringVar()
        self.using_var.set("test.csv")
        self.using_label = MyLabel(self, textvariable=self.using_var)
        self.using_label.grid(column=0, row=0,  rowspan=2, columnspan=3, sticky=N+W+E+S)
        
        self.using_button = MyButton(self, text="変更", command=self.change_csv)
        self.using_button.grid(column=3, row=0, rowspan=2, sticky=E)
        
        self.get_using_csv()
        self.using_var.set(self.using_party)

    def get_using_csv(self):
        with open('party\\setting.txt', 'r') as txt:
            self.using_party = txt.read()
            self.using_var.set(self.using_party)
            txt.close()
    
    def change_csv(self, value:str = ""):
        if value == "":
            typ = [('','*.csv')]
            current_directory = os.getcwd()
            value = filedialog.askopenfilename(filetypes = typ, initialdir = os.path.join(current_directory, 'party', "csv")).split('party/csv/')[1]

        with open('party\\setting.txt', 'w') as txt:
            txt.write(value)
            self.using_var.set(value)
            txt.close()


class PokemonEditors(ttk.LabelFrame):
    
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)
        self.pokemon_panel_list: list[PokemonEditor] = []
                
        for i in range(6):
            self.pokemon_panel = PokemonEditor(self, text=str(i+1)+"体目")
            c = i if i < 3 else i-3
            r = 0 if i < 3 else 1
            self.pokemon_panel.grid(column=c, row=r, sticky=E)
            self.pokemon_panel_list.append(self.pokemon_panel)


class PokemonEditor(ttk.LabelFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)

        self.syuzoku_list: list[tkinter.IntVar] = []
        self.jissu_list: list[tkinter.IntVar] = []
        self.waza_list: list[WazaNameCombobox] = []

        self._pokemon_icon = MyButton(self, size=(60, 60), padding=0, command=self.edit_pokemon)
        self._pokemon_icon.grid(column=0, row=0, rowspan=2, columnspan=2, sticky=N+S)

        self._pokemon_name_var = tkinter.StringVar()
        self._pokemon_name_label = ttk.Label(self, textvariable=self._pokemon_name_var)
        self._pokemon_name_label.grid(column=0, row=2, columnspan=2)
        
        self._clear_button = MyButton(self, text="クリア", command=self.clear_pokemon)
        self._clear_button.grid(column=2, row=0)

        self._teras_var = Types.なし
        self._teras_button = TypeButton(self,type_=Types.なし, command=self.on_push_terasbutton)
        self._teras_button.grid(column=0, row=3, columnspan=2, sticky=W+E+N+S)

        self.img = [ tkinter.PhotoImage(file=Types.なし.icon).subsample(3,3) ]*2
        self.type_img = ttk.Frame(self)
        self.type_img.grid(column=3, row=0)
        self.type1_img = self.img[0]
        self.type1_icon = ttk.Label(self.type_img, image=self.type1_img)
        self.type1_icon.pack(side="left")
        self.type2_img = self.img[1]
        self.type2_icon = ttk.Label(self.type_img, image=self.type2_img)
        self.type2_icon.pack(side="left")

        for i, text in enumerate(["性格", "持ち物", "特性"]):
            label = MyLabel(self, text=text)
            label.grid(column=2, row=i+1, padx=5, pady=5)

        self._seikaku_combobox = MyCombobox(self, values=get_seikaku_list(), width=24)
        self._seikaku_combobox.bind("<<ComboboxSelected>>", self.calc_status)
        self._seikaku_combobox.grid(column=3, row=1, sticky=W+E+N+S)

        self._item_combobox = MyCombobox(self, values=ALL_ITEM_COMBOBOX_VALUES)
        self._item_combobox.grid(column=3, row=2, sticky=W+E+N+S)

        self._ability_combobox = MyCombobox(self, width=16)
        self._ability_combobox.grid(column=3, row=3, sticky=W+E+N+S)

        self._waza_label = MyLabel(self, text="わざ")
        self._waza_label.grid(column=4, row=0, rowspan=4, padx=5, pady=5)
        for i in range(4):  
            cbx = WazaNameCombobox(self, width=16)
            cbx.grid(column=5, row=i)
            self.waza_list.append(cbx)

        for i, text in enumerate(["HP", "攻撃", "防御", "特攻", "特防", "素早さ"]):
            label = MyLabel(self, text=text)
            label.grid(column=0, row=i+5, padx=5, pady=5)
        for i, text in enumerate(["種族値", "実数値"]):
            label = MyLabel(self, text=text)
            label.grid(column=i+1, row=4, padx=5, pady=5)
        for i in range(6):
            value = tkinter.IntVar()
            value.set(0)
            label = MyLabel(self, textvariable=value)
            label.grid(column=1, row=i+5, padx=5, pady=5)
            self.syuzoku_list.append(value)
        for i in range(6):
            value = tkinter.IntVar()
            value.set(0)
            label = MyLabel(self, textvariable=value)
            label.grid(column=2, row=i+5, padx=5, pady=5)
            self.jissu_list.append(value)
        
        self._ev_total = tkinter.StringVar()
        self._ev_total.set("努力値（合計： 0 ）")
        self._ev_label = MyLabel(self, textvariable=self._ev_total)
        self._ev_label.grid(column=3, row=4, padx=5, pady=5)

        self._iv_label = MyLabel(self, text="個体値")
        self._iv_label.grid(column=4, row=4, columnspan=2, padx=5, pady=5)
        
        self._ev_frame = EvEditors(master=self, callback=self.change_ev)
        self._ev_frame.grid(column=3, row=5, rowspan=6, padx=5, pady=5, sticky=N+W+E)

        self._iv_frame = IvEditors(master=self, callback=self.calc_status)
        self._iv_frame.grid(column=4, row=5, columnspan=2, rowspan=6, padx=5, pady=5, sticky=N+W+E)

    def edit_pokemon(self):
        dialog = PokemonInputDialog()
        dialog.open(location=(self.winfo_x(), self.winfo_y()))
        self.wait_window(dialog)
        self.clear_pokemon()
        self._pokemon_icon.set_pokemon_icon(pid=dialog.pokemon.pid, size=(60, 60))
        self._pokemon_name_var.set(dialog.pokemon.name)
        self._ability_combobox["values"] = dialog.pokemon.abilities
        self._ability_combobox.set(dialog.pokemon.abilities[0])
        self.img[0]=tkinter.PhotoImage(file=dialog.pokemon.type[0].icon).subsample(3,3)
        self.type1_icon.configure(image=self.img[0], text=dialog.pokemon.type[0].name, compound='left')
        self.img[1]=tkinter.PhotoImage(file=dialog.pokemon.type[1].icon if len(dialog.pokemon.type) > 1 else Types.なし.icon).subsample(3,3)
        self.type2_icon.configure(image=self.img[1], text=dialog.pokemon.type[1].name if len(dialog.pokemon.type) > 1 else "", compound='left')
        
        for i, value in enumerate([dialog.pokemon.syuzoku.H, dialog.pokemon.syuzoku.A, dialog.pokemon.syuzoku.B, dialog.pokemon.syuzoku.C, dialog.pokemon.syuzoku.D, dialog.pokemon.syuzoku.S]):
            self.syuzoku_list[i].set(value)
        
        self.calc_status()
    
    def set_pokemon(self, pokemon:Pokemon):
        self._pokemon_icon.set_pokemon_icon(pid=pokemon.pid, size=(60, 60))
        self._pokemon_name_var.set(pokemon.name)
        self._teras_var = pokemon.terastype
        self._teras_button.set_type(pokemon.terastype)
        self._seikaku_combobox.set(pokemon.seikaku)
        self._item_combobox.set(pokemon.item)
        self._ability_combobox["values"] = pokemon.abilities
        self._ability_combobox.set(pokemon.ability)
        self.img[0]=tkinter.PhotoImage(file=pokemon.type[0].icon).subsample(3,3)
        self.type1_icon.configure(image=self.img[0], text=pokemon.type[0].name, compound='left')
        self.img[1]=tkinter.PhotoImage(file=pokemon.type[1].icon if len(pokemon.type) > 1 else Types.なし.icon).subsample(3,3)
        self.type2_icon.configure(image=self.img[1], text=pokemon.type[1].name if len(pokemon.type) > 1 else "", compound='left')
        
        for i, value in enumerate([pokemon.syuzoku.H, pokemon.syuzoku.A, pokemon.syuzoku.B, pokemon.syuzoku.C, pokemon.syuzoku.D, pokemon.syuzoku.S]):
            self.syuzoku_list[i].set(value)
        
        for i, doryoku in enumerate(self._ev_frame.ev_list):
            doryokus = self.doryoku_list = [pokemon.doryoku.H, pokemon.doryoku.A, pokemon.doryoku.B, pokemon.doryoku.C, pokemon.doryoku.D, pokemon.doryoku.S]
            doryoku.set_value(doryokus[i], True)

        for i, kotai in enumerate(self._iv_frame.iv_list):
            kotais = self.doryoku_list = [pokemon.kotai.H, pokemon.kotai.A, pokemon.kotai.B, pokemon.kotai.C, pokemon.kotai.D, pokemon.kotai.S]
            kotai.set_value(kotais[i], True)

        for i,waza in enumerate(self.waza_list):
            value = pokemon.waza_list[i]
            waza.set(value.name if value is not None else "")
        
        self.calc_status()


    def clear_pokemon(self):
        self._pokemon_icon.set_image(images.get_blank_image(size=(60, 60)))
        self._pokemon_name_var.set("")
        self._teras_var = Types.なし
        self._teras_button.set_type(Types.なし)
        self._seikaku_combobox.set("")
        self._item_combobox.set("")
        self._ability_combobox["values"] = []
        self._ability_combobox.set("")
        self.img[0]=tkinter.PhotoImage(file=Types.なし.icon).subsample(3,3)
        self.type1_icon.configure(image=self.img[0], text=Types.なし.name, compound='left')
        self.img[1]=tkinter.PhotoImage(file=Types.なし.icon).subsample(3,3)
        self.type2_icon.configure(image=self.img[1], text=Types.なし.name, compound='left')

        for waza in self.waza_list:
            waza.set("")

        for syuzoku in self.syuzoku_list:
            syuzoku.set(0)
        
        for jissu in self.jissu_list:
            jissu.set(0)
        
        self._ev_frame.init_all_value()
        self._iv_frame.init_all_value()

    def on_push_terasbutton(self):
        type: Types = self.select_type()
        self._teras_var = type
        self._teras_button.set_type(type)
    
    def select_type(self) -> Types:
        dialog = TypeSelectDialog()
        dialog.open(location=(self.winfo_x(), self.winfo_y()))
        self.wait_window(dialog)
        return dialog.selected_type

    def change_ev(self, *args):
        value = 0
        for ev in self._ev_frame.ev_list:
            value += ev._ev_num.get()
        self._ev_total.set("努力値（合計： "+str(value)+" ）")
        self.calc_status()

    def calc_status(self, *args):
        for i, syuzoku in enumerate(self.syuzoku_list):
            if syuzoku.get() != 0:
                if i == 0:
                    value = int(syuzoku.get() + float(self._iv_frame.iv_list[i]._iv_num.get())/2 + float(self._ev_frame.ev_list[i]._ev_num.get())/8 + 60)
                    self.jissu_list[i].set(value)
                else:
                    hosei = get_seikaku_hosei(self._seikaku_combobox.get(), StatsKey(i))
                    value = int((syuzoku.get() + float(self._iv_frame.iv_list[i]._iv_num.get())/2 + float(self._ev_frame.ev_list[i]._ev_num.get())/8 + 5) * hosei)
                    self.jissu_list[i].set(value)

    def set_csv_row(self):
        waza_list = self.get_all_waza()
        all_kotai = self._iv_frame.get_all_iv()
        all_doryoku = self._ev_frame.get_all_ev()

        if self._pokemon_name_var.get() == "":
            return ""
        else:
            return [self._pokemon_name_var.get(), all_kotai, all_doryoku, self._seikaku_combobox.get(), self._item_combobox.get(), self._ability_combobox.get(), self._teras_var.name if self._teras_var != Types.なし else "", waza_list[0], waza_list[1], waza_list[2], waza_list[3]]

    def get_all_waza(self):
        waza_list = []
        for waza in self.waza_list:
            waza_list.append(waza.get())
        return waza_list    


class EvEditors(ttk.Frame):

    def __init__(self, master, callback, **kwargs):
        super().__init__(master=master, **kwargs)
        self.ev_list: list[EvEditor] = []
        for i in range(6):
            self.ev_editor=EvEditor(self)
            self.ev_editor.setCallback(callback)
            self.ev_editor.pack(pady=10)
            self.ev_list.append(self.ev_editor)

    def init_all_value(self):
        for i in range(6):
            self.ev_list[i]._ev_num.set(0)
            self.ev_list[i]._ev_entry.delete(0, tkinter.END)
            self.ev_list[i]._ev_entry.insert(0, 0)

    def get_all_ev(self):
        status_list = ["H", "A", "B", "C", "D", "S"]
        all_ev = ""
        for i in range(6):
            if self.ev_list[i]._ev_num.get() != 0:
                all_ev += status_list[i] + str(self.ev_list[i]._ev_num.get())
        return all_ev


class EvEditor(ttk.Frame):

    def on_validate_3(self, P, V):
        if P.isdigit() or P == "":
            return len(P) <= 3
        else:
            return False

    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)
        self.validate_cmd_3 = self.register(self.on_validate_3)

        self._ev_num = tkinter.IntVar()
        self._ev_num.set(0)
        
        self._ev_min_button = tkinter.Button(self, text="0", command=lambda: self.set_value(0, True))
        self._ev_min_button.pack(side="left")
        
        self._ev_count_down = tkinter.Button(self, text="↓", command=lambda: self.set_value(-4, False))
        self._ev_count_down.pack(side="left")

        self._ev_entry = ModifiedEntry(self, text=0, validate="key", width=4, validatecommand=(self.validate_cmd_3, "%P", "%V"))
        self._ev_entry.insert(0, 0)
        self._ev_entry.pack(side="left")

        self._ev_count_up = tkinter.Button(self, text="↑", command=lambda: self.set_value(4, False))
        self._ev_count_up.pack(side="left")

        self._ev_max_button = tkinter.Button(self, text="252", command=lambda: self.set_value(252, True))
        self._ev_max_button.pack(side="left")

    def set_value(self, value: int, override: bool):
        if override:
            self._ev_entry.delete(0, tkinter.END)
            self._ev_num.set(value)
            self._ev_entry.insert(0, value)
        else:
            increase_num = self._ev_num.get() + value
            if 0 <= increase_num <= 252: 
                self._ev_entry.delete(0, tkinter.END)
                self._ev_num.set(increase_num)
                self._ev_entry.insert(0, increase_num)

    def setCallback(self, func):
        self._ev_entry.bind("<<TextModified>>", func)

class IvEditors(ttk.Frame):

    def __init__(self, master, callback, **kwargs):
        super().__init__(master=master, **kwargs)
        self.iv_list:list[IvEditor] = []
        for i in range(6):
            self.iv_editor=IvEditor(self)
            self.iv_editor.setCallback(callback)
            self.iv_editor.pack(pady=10)
            self.iv_list.append(self.iv_editor)
    
    def init_all_value(self):
        for i in range(6):
            self.iv_list[i]._iv_num.set(31)
            self.iv_list[i]._iv_entry.delete(0, tkinter.END)
            self.iv_list[i]._iv_entry.insert(0, 31)

    def get_all_iv(self):
        status_list = ["H", "A", "B", "C", "D", "S"]
        all_iv = ""
        for i in range(6):
            if self.iv_list[i]._iv_num.get() != 31:
                all_iv += status_list[i] + str(self.iv_list[i]._iv_num.get())
        return all_iv


class IvEditor(ttk.Frame):

    def on_validate_2(self, P, V):
        if P.isdigit() or P == "":
            return len(P) <= 2
        else:
            return False

    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)
        self.validate_cmd_2 = self.register(self.on_validate_2)

        self._iv_num = tkinter.IntVar()
        self._iv_num.set(31)
        
        self._iv_min_button = tkinter.Button(self, text="0", command=lambda: self.set_value(0, True))
        self._iv_min_button.pack(side="left")
        
        self._iv_count_down = tkinter.Button(self, text="↓", command=lambda: self.set_value(-1, False))
        self._iv_count_down.pack(side="left")

        self._iv_entry = ModifiedEntry(self, validate="key", width=4, validatecommand=(self.validate_cmd_2, "%P", "%V"))
        self._iv_entry.insert(0, 31)
        self._iv_entry.pack(side="left")

        self._iv_count_up = tkinter.Button(self, text="↑", command=lambda: self.set_value(1, False))
        self._iv_count_up.pack(side="left")

        self._iv_max_button = tkinter.Button(self, text="31", command=lambda: self.set_value(31, True))
        self._iv_max_button.pack(side="left")

    def set_value(self, value: int, override: bool):
        if override:
            self._iv_entry.delete(0, tkinter.END)
            self._iv_num.set(value)
            self._iv_entry.insert(0, value)
        else:
            increase_num = self._iv_num.get() + value
            if 0 <= increase_num <= 31: 
                self._iv_entry.delete(0, tkinter.END)
                self._iv_num.set(increase_num)
                self._iv_entry.insert(0, increase_num)
    
    def setCallback(self, func):
        self._iv_entry.bind("<<TextModified>>", func)

class PokemonInputDialog(tkinter.Toplevel):

    def __init__(self, title: str = "", width: int = 400, height: int = 300):
        super().__init__()
        self.title("ポケモン入力")
        self.pokemon = Pokemon()

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

    def open(self, location=tuple[int, int]):
        self.grab_set()
        self._name_input.focus_set()
        self.geometry("+{0}+{1}".format(location[0], location[1]))

    def on_input_name(self, *args):
        pokemon_name = self._name_input.get()
        self.pokemon = Pokemon.by_name(pokemon_name, default=True)
        self.destroy()
