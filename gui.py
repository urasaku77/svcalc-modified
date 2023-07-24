from kivy.event import EventDispatcher
from kivy.properties import ListProperty, ObjectProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior, ToggleButtonBehavior
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from typing import Optional, Union
from data.db import DB
from pokedata.const import *
from pokedata.pokemon import Pokemon
from pokedata.waza import WazaBase
from pokedata.calc import DamageCalcResult
import datetime


# ドロップダウン付きウィジェット
# options に、要素選択用のボタンを追加する。ボタンは高さを指定しないと0になる
class DropDownWidget(Widget):
    options = ListProperty(('',))

    def __init__(self, **kw):
        super(DropDownWidget, self).__init__(**kw)
        ddn = self.drop_down = DropDown()
        ddn.bind(on_select=self.on_select)

    def on_options(self, _instance, value):
        ddn = self.drop_down
        ddn.clear_widgets()
        for widg in value:
            widg.bind(on_release=lambda btn: ddn.select(btn.text))
            ddn.add_widget(widg)

    def on_select(self, _instance, value):
        pass


# 編集可能コンボボックス
# options に、ドロップダウン用のウィジェットを追加して使用する
# select_callback に、要素選択時のコールバック(引数str)を指定できる
class ComboEdit(TextInput, DropDownWidget):
    __events__ = ("on_confirm", )
    options = ListProperty(())

    def __init__(self, **kw):
        super(ComboEdit, self).__init__(**kw)
        self.multiline = False

    def on_select(self, _instance, value):
        self.text = value
        self.dispatch("on_confirm")

    def on_confirm(self, *args):
        pass

    def _on_focus(self, instance, value, *largs):
        super(ComboEdit, self)._on_focus(instance, value, *largs)
        if value is True and self.drop_down.parent is None:
            self.drop_down.open(self)


# ポケモン名サジェスト機能コンボボックス
# 入力時にサジェストされる。ローマ字、ひらがな対応
# ドロップダウン選択か、候補が1つの時にエンターで決定
class PokeNameComboEdit(ComboEdit):

    def __init__(self, **kw):
        super(PokeNameComboEdit, self).__init__(**kw)
        self.namelist: list[str] = DB.get_pokemon_namelist(form=True)
        self.hint_text = "ポケモン名を入力"

    def on_text(self, _instance, value):
        import jaconv
        text = jaconv.alphabet2kata(value)
        if len(text) < 2:
            self.options = ()
            return
        itemlist = [] if len(value) == 0 else list(
            filter(lambda x: text in x, self.namelist))
        itemlist = itemlist[:10] if len(itemlist) > 10 else itemlist
        self.options = tuple(
            [Button(text=item, size_hint_y=None, height=30) for item in itemlist])

    def on_text_validate(self, *args):
        if len(self.options) == 1:
            self.on_select(self, self.options[0].text)
            self.options = ()


# 技名サジェスト機能コンボボックス
class WazaNameComboEdit(ComboEdit):

    cid = NumericProperty(-1)

    def __init__(self, **kw):
        super(WazaNameComboEdit, self).__init__(**kw)
        self.namedict: dict[str, str] = DB.get_waza_namedict()

    def on_text(self, _instance, value):
        import jaconv
        text = jaconv.alphabet2kata(value)
        if len(text) < 2:
            self.options = ()
            return
        itemlist: list = list(filter(lambda x: text in x[0], self.namedict.items()))
        itemlist = itemlist[:10] if len(itemlist) > 10 else itemlist
        self.options = tuple(
            [Button(text=item[1], size_hint_y=None, height=30) for item in itemlist])

    def on_text_validate(self, *args):
        if len(self.options) == 1:
            self.on_select(self, self.options[0].text)
            self.options = ()


# 技ボタン
# クリックすると編集モード（技名コンボボックスが出る）
class WazaButton(RelativeLayout):
    __events__ = ("on_confirm",)

    def __init__(self, **kw):
        super(WazaButton, self).__init__(**kw)
        self.__before_text: str = ""

    @property
    def text(self):
        return self.button.text

    @text.setter
    def text(self, value):
        self.button.text = value

    @property
    def before_text(self):
        return self.__before_text

    @property
    def button(self) -> Button:
        return self.ids["button"]

    @property
    def comboEdit(self) -> ComboEdit:
        return self.ids["comboedit"]

    def click(self):
        self.button.disabled = True
        self.comboEdit.text = ""
        self.comboEdit.disabled = False
        self.comboEdit.focus = True

    def focus_comboedit(self, value):
        if value is False:
            self.button.disabled = False
            self.comboEdit.disabled = True

    def waza_confirm(self, text: str):
        self.__before_text = self.text
        self.text = text
        self.button.disabled = False
        self.comboEdit.disabled = True
        self.dispatch("on_confirm")

    def on_confirm(self, *args):
        pass


# ポケモン表示パネル
class ActivePokemonPanel(BoxLayout, EventDispatcher):

    __events__ = ("on_click_icon", )

    pokemon = ObjectProperty(None, allownone=True)
    player = NumericProperty(-1)
    evs_combobox = ObjectProperty()
    teras_button = ObjectProperty()
    icon = ObjectProperty()
    formchange_icon = ObjectProperty()
    ability_values = ListProperty([""])
    critical = BooleanProperty(False)
    burn = BooleanProperty(False)
    charging = BooleanProperty(False)

    def __init__(self, **kw):
        from kivy_gui.popup import TypeSelectPopupContent
        super(ActivePokemonPanel, self).__init__(**kw)
        self.func_for_click_icon = dummy
        self.popup = Popup(
            title="テラスタイプ選択",
            content=TypeSelectPopupContent(selected=self.on_select_terastype),
            size_hint=(0.8, 0.6))

    @property
    def battle_terastype_icon(self):
        if self.pokemon is None:
            return Types.なし.icon
        return self.pokemon.battle_terastype.icon

    def init_pokemon(self):
        self.pokemon = None
        self.ids["_teras_button"].icon = Types.なし.icon
        self.ids["_teras_button"].text = Types.なし.name
        self.ids["_evs_combobox"].disabled = True
        self.ids["item"].disabled = True
        self.ids["ability"].disabled = True
        self.ids["abilities_valid"].disabled = True
        self.ability_values = [""]
        self.ids["wall"].disabled = True
        self.ids["wall"].text = "なし"
        self.critical = False
        self.burn = False
        self.charging = False
        self.change_rank()

    def on_pokemon(self, *args):
        if self.pokemon is not None:
            pokemon: Pokemon = self.pokemon
            self.set_ability(pokemon.ability)
            self.critical = False
            self.burn = False
            self.charging = False
            self.teras_button.icon = pokemon.battle_terastype.icon
            self.teras_button.text = pokemon.battle_terastype.name
            self.ids["_evs_combobox"].disabled = False
            self.ids["ability"].disabled = False
            self.ids["item"].disabled = False
            self.ids["wall"].disabled = False
            self.change_rank()

    def set_ability(self, ability: str):
        self.ability_values = [""]
        if ability == "" and len(self.pokemon.abilities) != 0:
            ability = [x for x in self.pokemon.abilities if x  != ""][0]
        for k, v in ABILITY_VALUES.items():
            if ability == k:
                self.ability_values = v
                break
        if ability != self.ids["ability"].text:
            self.pokemon.ability = ability
            self.pokemon.ability_value = self.ability_values[0]
            self.ids["ability"].text = self.pokemon.ability
            self.ids["abilities_valid"].items = self.ability_values
            self.ids["abilities_valid"].text = self.pokemon.ability_value
        self.ids["abilities_valid"].disabled = True if self.ability_values[0] == "" else False

    def set_wall(self, value):
        for wall in Walls:
            if wall.name == value:
                self.pokemon.wall = wall
        self.pokemon.statechanged()

    def set_func_for_click_icon(self,func):
        self.func_for_click_icon = func

    def on_click_icon(self, *args):
        self.func_for_click_icon()

    def change_rank(self, type:str="", up:bool=True):
        if self.pokemon is not None:
            value = 0
            last_value = 0
            match type:
                case "A":
                    value = self.pokemon.rank.A
                case "B":
                    value = self.pokemon.rank.B
                case "C":
                    value = self.pokemon.rank.C
                case "D":
                    value = self.pokemon.rank.D
                case "S":
                    value = self.pokemon.rank.S
                case _:
                    self.pokemon.rank.init_values(0)
                    self.pokemon.statechanged()
                    return
            if up:
                last_value = value + 1
            else:
                last_value = value - 1
            if last_value > 6 or last_value < -6:
                return
            self.pokemon.rank.set_values_from_int(type, last_value)
            self.pokemon.statechanged()

    def change_critical(self):
        self.critical = not self.critical
        if self.pokemon is None:
            return
        for waza in self.pokemon.waza_list:
            if waza is not None:
                waza.critical = self.critical
        self.pokemon.statechanged()

    def change_burn(self):
        self.burn = not self.burn
        if self.pokemon is None:
            return
        if self.burn:
            self.pokemon.ailment = Ailments.やけど
        else:
            self.pokemon.ailment = Ailments.なし
        self.pokemon.statechanged()

    def change_charging(self):
        self.charging = not self.charging
        if self.pokemon is None:
            return
        self.pokemon.charging = self.charging
        self.pokemon.statechanged()

    def change_ranks(self):
        if self.pokemon is not None:
            self.ids["A"].text = str(self.pokemon.rank.A)
            self.ids["B"].text = str(self.pokemon.rank.B)
            self.ids["C"].text = str(self.pokemon.rank.C)
            self.ids["D"].text = str(self.pokemon.rank.D)
            self.ids["S"].text = str(self.pokemon.rank.S)

    def form_change(self):
        pokemon: Pokemon = self.pokemon
        if pokemon is not None:
            pokemon.form_change()
            self.evs_combobox.text = pokemon.marked_status_text
            self.icon = pokemon.icon
            self.formchange_icon = pokemon.changeable_icon

    def on_select_doryoku_preset(self, value):
        if self.pokemon is not None:
            self.pokemon.set_doryoku_preset(value)
            self.evs_combobox.text = self.pokemon.marked_status_text

    def on_click_terasicon(self):
        if self.pokemon is not None:
            if self.player == 0 and self.pokemon.terastype != Types.なし:
                self.set_terastype()
            else:
                self.select_terastype()

    def set_terastype(self):
        if self.pokemon.battle_terastype == Types.なし:
            self.on_select_terastype(self.pokemon.terastype.name)
        else:
            self.on_select_terastype("なし")

    def select_terastype(self, *_args):
        self.popup.open()

    def on_select_terastype(self, value):
        if self.pokemon is not None:
            terastype = Types[value]
            self.pokemon.battle_terastype = terastype
            self.teras_button.icon = terastype.icon
            self.teras_button.text = terastype.name
            self.popup.dismiss()


# 技＋ダメージ計算結果表示パネルのリスト
class WazaListPanel(BoxLayout):

    num = NumericProperty(10)
    built_flag = NumericProperty(0)

    def __init__(self, **kw):
        super(WazaListPanel, self).__init__(**kw)
        self.pokemon: Optional[Pokemon] = None
        self.orientation = "vertical"
        self.wazapanel_list: list[WazaPanel] = []
        for i in range(10):
            wazapanel = WazaPanel(index=i)
            self.wazapanel_list.append(wazapanel)

    def set_pokemon(self, pokemon: Pokemon):
        if self.built_flag == 0:
            for i in range(self.num):
                self.add_widget(self.wazapanel_list[i])
            self.built_flag = 1

        self.pokemon = pokemon
        for i, wazabase in enumerate(self.pokemon.waza_list):
            self.wazapanel_list[i].set_pokemon(self.pokemon)

    def set_damage_calc_results(self, results: list['DamageCalcResult']):
        for i in range(len(results)):
            self.wazapanel_list[i].set_damage_calc_result(results[i])

    def initWazaPanels(self):
        self.clear_widgets()
        self.built_flag=0
        self.__init__()

# 技リスト＋ダメージ計算結果表示パネル
class WazaPanel(BoxLayout):
    __events__ = ("on_confirm_waza", "on_click_center_button",)

    index = NumericProperty(-1)

    def __init__(self, **kw):
        super(WazaPanel, self).__init__(**kw)
        self.pokemon: Optional[Pokemon] = None

        # 技名ボタン
        self.waza_button: WazaButton = WazaButton(size_hint_x=3)
        self.waza_button.bind(on_confirm=lambda x: self.on_select_waza(x.text))
        # 中央ボタン
        self.center_button = Button(
            size_hint_x=1, width=40, on_press=self.click_center_button)
        self.center_button.disabled = True
        # ダメージ計算結果表示パネル
        self.hpbar_panel: HpBarPanel = HpBarPanel(size_hint_x=5)

        self.add_widget(self.waza_button)
        self.add_widget(self.center_button)
        self.add_widget(self.hpbar_panel)
        self.spacing = 5

    # ポケモン情報のセット
    def set_pokemon(self, pokemon: Pokemon):
        self.pokemon = pokemon
        self.show_wazabase_info()

    @property
    def wazabase(self) -> WazaBase:
        return self.pokemon.waza_list[self.index]

    # 技情報の表示
    def show_wazabase_info(self):
        wazabase = self.wazabase
        if wazabase is None:
            self.waza_button.text = ""
            self.center_button.text = ""
            self.center_button.disabled = True
            return

        # 技名セット
        self.waza_button.text = wazabase.name

        # 回数や威力補正がある技の場合
        match wazabase.type:
            case wazabase.TYPE_ADD_POWER | wazabase.TYPE_MULTI_HIT | wazabase.TYPE_POWER_HOSEI:
                self.center_button.text = "x" + str(wazabase.value)
                self.center_button.disabled = False
            case wazabase.TYPE_SELF_BUFF:
                self.center_button.text = "＋"
                self.center_button.disabled = False
            case _:
                self.center_button.text = ""
                self.center_button.disabled = True

    # ダメージ計算結果のセット
    def set_damage_calc_result(self, result: 'DamageCalcResult'):
        self.hpbar_panel.result = result

    # 技名コンボボックスが決定された時
    def on_select_waza(self, value) -> None:
        self.pokemon.set_waza(self.index, value)
        self.show_wazabase_info()

    # 中央ボタンが押された時
    def click_center_button(self, *args):
        self.pokemon.use_waza_effect(self.index)
        self.center_button.text = "×" + str(self.wazabase.value)

    # イベント用
    def on_confirm_waza(self, *args):
        pass

    # イベント用
    def on_click_center_button(self, *args):
        pass


class WazaOptionButton(Button):
    value_type = NumericProperty(0)
    value = NumericProperty(0)

    def __init__(self, **kw):
        super(WazaOptionButton, self).__init__(**kw)

    def on_value(self, *args):
        self.text = "×" + str(self.value)


# 背景色指定ラベル（kvファイル設定あり）
class ColorLabel(Label):
    back_color = ListProperty((0.2, 0.2, 0.2, 1))


# ダメージ計算結果表示パネル
class HpBarPanel(BoxLayout):

    result = ObjectProperty(DamageCalcResult(
        attacker=Pokemon(), defender=Pokemon(), waza=None, damages=[]))
    damage_text = StringProperty("")
    damage_per_text = StringProperty("")
    hp_bar_height = NumericProperty(0)

    hp_bar_green_1 = (56 / 255, 142 / 255, 60 / 255, 1)
    hp_bar_green_2 = (56 / 255, 142 / 255, 60 / 255, 0.5)

    hp_bar_yellow_1 = (251 / 255, 192 / 255, 45 / 255, 1)
    hp_bar_yellow_2 = (251 / 255, 192 / 255, 45 / 255, 0.5)

    hp_bar_red_1 = (211 / 255, 47 / 255, 47 / 255, 1)
    hp_bar_red_2 = (211 / 255, 47 / 255, 47 / 255, 0.5)

    def __init__(self, **kw):
        super(HpBarPanel, self).__init__(**kw)

    @property
    def hp_bar_1(self) -> ColorLabel:
        return self.ids["hp_bar_1"]

    @property
    def hp_bar_2(self) -> ColorLabel:
        return self.ids["hp_bar_2"]

    @property
    def hp_bar_3(self) -> ColorLabel:
        return self.ids["hp_bar_3"]

    def on_result(self, *args):
        result: DamageCalcResult = self.result
        if result.is_damage is False:
            self.damage_text = ""
            self.damage_per_text = ""
            self.hp_bar_height = 0
            return

        self.damage_text = result.damage_text
        self.damage_per_text = "(" + result.damage_per_text + ")"
        self.hp_bar_height = 5

        w1 = max(1 - (self.result.max_damage_per / 100), 0.00001)
        w2 = max(min((self.result.max_damage_per / 100), 1) - (self.result.min_damage_per / 100), 0.00001)

        if self.result.max_damage_per > 80:
            self.hp_bar_1.back_color = HpBarPanel.hp_bar_red_1
            self.hp_bar_2.back_color = HpBarPanel.hp_bar_red_2
        elif self.result.max_damage_per > 50:
            self.hp_bar_1.back_color = HpBarPanel.hp_bar_yellow_1
            self.hp_bar_2.back_color = HpBarPanel.hp_bar_yellow_2
        else:
            self.hp_bar_1.back_color = HpBarPanel.hp_bar_green_1
            self.hp_bar_2.back_color = HpBarPanel.hp_bar_green_2

        self.hp_bar_1.size_hint_x = w1
        self.hp_bar_2.size_hint_x = w2
        self.hp_bar_3.size_hint_x = 1 - w1 - w2


# 背景色指定ボタン（kvファイル設定あり）
class ColorButton(Button):
    back_color = ListProperty((0.2, 0.2, 0.2, 1))


class MyButton(Widget):
    pass


# アイコンボタン
# Image＋Labelの複合ウィジェットにButtonBehaviorでボタン機能を付与している（kvファイル設定あり）
class IconButton(ButtonBehavior, BoxLayout, MyButton):

    # プロパティ
    no = NumericProperty(-1)
    icon = StringProperty("")
    button_text = StringProperty()
    back_color = ListProperty((0.3, 0.3, 0.3, 1))
    font_size = ObjectProperty(14)
    back_color_down = ListProperty((91/255, 192/255, 222/255, 1))

    @property
    def text(self) -> str:
        return self.button_text

    @text.setter
    def text(self, value) -> None:
        self.button_text = value


# アイコントグルボタン
class IconToggleButton(ToggleButtonBehavior, BoxLayout, MyButton):

    # プロパティ
    no = NumericProperty(-1)
    icon = StringProperty("image/other/blank.png")
    pokemon_name = StringProperty("")
    button_text = StringProperty()
    back_color = ListProperty((0.3, 0.3, 0.3, 1))
    font_size = ObjectProperty(14)
    back_color_down = ListProperty((91/255, 192/255, 222/255, 1))

    def on_pokemon_name(self, *args):
        if len(self.pokemon_name):
            from data.db import DB
            pid = DB.get_pokemon_pid_by_name(self.pokemon_name)
            self.icon = "image/pokeicon/" + pid + ".png"
        else:
            self.icon = "image/other/blank.png"


# パーティ表示アイコンパネル
class PartyIconPanel(BoxLayout):

    __events__ = ("on_select",)

    player = NumericProperty(0)
    select_cb = ObjectProperty(None)

    def __init__(self, **kw):
        super(PartyIconPanel, self).__init__(**kw)
        self.__buttons: list[IconToggleButton] = []
        prefix = str(datetime.datetime.now())
        for i in range(6):
            btn = IconToggleButton(
                no=i, group=f"party{prefix}",
                on_release=lambda x: self.dispatch("on_select") if x.state == "down" else None)
            btn.bind(on_release=lambda x: self.keep(x))
            self.__buttons.append(btn)
            self.add_widget(btn)

    def keep(self,instance):
        if instance.state != "down":
            instance.state = "down"

    @property
    def selected_index(self) -> int:
        for i in range(len(self.buttons)):
            if self.__buttons[i].state == "down":
                return i
        return -1

    def select_next_empty_button(self) -> int:
        for i in range(len(self.buttons)):
            if len(self.__buttons[i].pokemon_name) == 0:
                self.select(i)
                return i
        return -1

    @property
    def buttons(self) -> list[IconToggleButton]:
        return self.__buttons

    def select(self, index) -> None:
        for i in range(len(self.buttons)):
            self.buttons[i].state = "down" if i == index else "normal"

    def on_select(self, *args):
        pass

    def set_pokemon_icon(self, index: int, icon_source: Optional[str]):
        if icon_source is not None:
            self.__buttons[index].icon = icon_source
        else:
            self.__buttons[index].icon = "image/other/blank.png"

# ドロップダウン付きアイコンボタン
# options に、ドロップダウン用のウィジェットを追加して使用する
# items に、文字配列を入れるとデフォルト設定のアイコンボタンをドロップダウンに入れる
# select_callback に、要素選択時のコールバック(引数str)を指定できる
class DropDownButton(IconButton):

    __events__ = ("on_select_item", )

    options = ListProperty([])
    items = ListProperty([])
    select_callback = ObjectProperty(None)
    image_enable = BooleanProperty(False)
    font_size = ObjectProperty(14)

    def __init__(self, **kw):
        ddn = self.drop_down = DropDown()
        ddn.bind(on_select=self.on_select)
        super(DropDownButton, self).__init__(**kw)

    def on_options(self, _instance, value):
        ddn = self.drop_down
        ddn.clear_widgets()
        for widg in value:
            widg.bind(on_release=lambda btn: ddn.select(btn))
            ddn.add_widget(widg)

    def on_select(self, _instance, value):
        self.button_text = value.text
        self.dispatch("on_select_item")

    def on_press(self):
        self.drop_down.open(self)

    def on_items(self, *_args):
        self.options = tuple([IconButton(
            button_text=item, size_hint_y=None, height=30
        ) for item in self.items])

    def on_select_item(self, *args):
        pass


class LabelButton(ButtonBehavior, ColorLabel):
    def __init__(self, **kw):
        super(LabelButton, self).__init__(**kw)

def dummy():
    pass