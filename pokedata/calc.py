from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_DOWN, ROUND_FLOOR

from pokedata.const import *
from pokedata.stats import StatsKey
from pokedata.waza import Waza

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from pokedata.pokemon import Pokemon


@dataclass
class DamageCalcResult:
    attacker: 'Pokemon'
    defender: 'Pokemon'
    waza: Optional['Waza']
    damages: list[int]

    @property
    def is_damage(self) -> bool:
        return self.waza is not None and self.waza.category != "変化" and len(self.damages) > 0

    @property
    def enable(self) -> bool:
        return self.damages is not None

    @property
    def min_damage(self) -> int:
        return self.damages[0]

    @property
    def max_damage(self) -> int:
        return self.damages[15]

    @property
    def damage_text(self) -> str:
        return str(self.min_damage) + "-" + str(self.max_damage)

    @property
    def min_damage_per(self) -> float:
        per = Decimal(self.damages[0] / self.defender[StatsKey.H] * 100)
        return float(per.quantize(Decimal("0.1")))

    @property
    def max_damage_per(self) -> float:
        per = Decimal(self.damages[15] / self.defender[StatsKey.H] * 100)
        return float(per.quantize(Decimal("0.1")))

    @property
    def damage_per_text(self) -> str:
        return str(self.min_damage_per) + "%-" + str(self.max_damage_per) + "%"

    @property
    def to_string(self) -> str:
        return "{0} {1}".format(
            self.waza.name, self.min_damage_per)


DECIMAI_ZERO = Decimal(0)


class DamageCalc:

    @staticmethod
    def get_all_damages(
            attacker: 'Pokemon',
            defender: 'Pokemon',
            weather: Weathers = Weathers.なし,
            field: Fields = Fields.なし) -> list[DamageCalcResult]:
        result_all: list[DamageCalcResult] = []
        for wazabase in attacker.waza_list:
            if wazabase is None:
                result_all.append(DamageCalcResult(
                    attacker=attacker, defender=defender, waza=None, damages=[]))
                continue
            waza = Waza.ByWazaBase(wazabase)

            if waza.name == "トリックフラワー" or waza.name == "あんこくきょうだ" or waza.name == "すいりゅうれんだ":
                waza.critical = True

            # テラバーストによる種別、タイプ変化
            if waza.name == "テラバースト" and attacker.battle_terastype != Types.なし:
                waza.category = 物理 if attacker.rankedA >= attacker.rankedC else 特殊
                waza.type = attacker.battle_terastype

            if waza.name == "ツタこんぼう":
                if attacker.name == "オーガポン(水)":
                    waza.type = Types.みず
                elif attacker.name == "オーガポン(炎)":
                    waza.type = Types.ほのお
                elif attacker.name == "オーガポン(岩)":
                    waza.type = Types.いわ
            if waza.name == "めざめるダンス":
                waza.type = attacker.type[0]
            if waza.name == "レイジングブル":
                if attacker.name == "ケンタロス(パルデア単)":
                    waza.type = Types.かくとう
                elif attacker.name == "ケンタロス(パルデア炎)":
                    waza.type = Types.ほのお
                elif attacker.name == "ケンタロス(パルデア水)":
                    waza.type = Types.みず

            damages = DamageCalc.__get_damage(
                attacker=attacker, defender=defender, waza=waza,
                weather=weather, field=field)
            result = DamageCalcResult(
                attacker=attacker, defender=defender, waza=waza, damages=damages)
            result_all.append(result)
        return result_all

    @staticmethod
    def __get_damage(
            attacker: 'Pokemon',
            defender: 'Pokemon',
            waza: Waza,
            weather: Weathers,
            field: Fields) -> Optional[list[int]]:
        # 変化技は計算しない
        if waza.category == 変化:
            return None

        # 攻撃回数分だけ繰り返す
        total_damages = [0 for x in range(16)]
        for count in range(max(1, waza.multi_hit)):
            # 技威力
            waza_power: int = DamageCalc.__get_waza_power(
                attacker=attacker,
                defender=defender,
                waza=waza,
                weather=weather,
                field=field
            )
            if waza_power == -1:
                return None
            # 攻撃力
            attack_power: int = DamageCalc.__get_attack_power(
                attacker=attacker,
                defender=defender,
                waza=waza,
                weather=weather,
                field=field
            )
            # 防御力
            defence_power: int = DamageCalc.__get_defence_power(
                attacker=attacker,
                defender=defender,
                waza=waza,
                weather=weather,
                field=field
            )
            # ダメージ補正
            damage_hosei: int = DamageCalc.__get_damage_hosei(
                attacker=attacker,
                defender=defender,
                waza=waza,
                count=count
            )
            # 最終ダメージ
            damages = DamageCalc.__get_fix_damages(
                attacker=attacker,
                defender=defender,
                waza=waza,
                waza_power=waza_power,
                attack_power=attack_power,
                defence_power=defence_power,
                damage_hosei=damage_hosei,
                weather=weather
            )
            # 合計ダメージに合算する
            total_damages = [sum(x) for x in zip(total_damages, damages)]

        return total_damages

    # 技威力の算出
    @staticmethod
    def __get_waza_power(
            attacker: 'Pokemon',
            defender: 'Pokemon',
            waza: Waza,
            weather: Weathers,
            field: Fields) -> int:
        hosei: dict[str, int] = {}

        # region 技の初期威力
        match waza.name:
            case "ジャイロボール":
                power = min(int(Decimal(25 * defender.rankedS / attacker.rankedS).quantize(
                    DECIMAI_ZERO, rounding=ROUND_FLOOR
                ) + 1), 150)
            case "エレキボール":
                rate = int(Decimal(25 * attacker.rankedS / defender.rankedS))
                if rate < 1:
                    power = 40
                elif rate < 2:
                    power = 60
                elif rate < 3:
                    power = 80
                elif rate < 4:
                    power = 120
                else:
                    power = 150
            case "ヒートスタンプ" | "ヘビーボンバー":
                power = 40
                for ratio in reversed(range(2, 6)):
                    if attacker.weight >= int(Decimal(defender.weight * ratio)):
                        power = ratio * 20 + 20
                        break
            case "けたぐり" | "くさむすび":
                power = 120
                for values in DamageCalc.__damages_at_weight:
                    if defender.weight < values[0]:
                        power = values[1]
                        break
            case "アシストパワー" | "つけあがる":
                power = 20 + attacker.rank.sum_plus_num()*20
            case "ウェザーボール":
                power = 50
                if weather == Weathers.晴れ:
                    waza.type = Types.ほのお
                    power = 100
                elif weather == Weathers.雨:
                    waza.type = Types.みず
                    power = 100
                elif weather == Weathers.雪:
                    waza.type = Types.こおり
                    power = 100
                elif weather == Weathers.砂嵐:
                    waza.type = Types.いわ
                    power = 100
            case "だいちのはどう":
                power = 50
                if attacker.type != Types.ひこう and attacker.ability != "ふゆう" and field != Fields.なし:
                    if field == Fields.グラス:
                        waza.type = Types.くさ
                        power = 100
                    elif field == Fields.ミスト:
                        waza.type = Types.フェアリー
                        power = 100
                    elif field == Fields.エレキ:
                        waza.type = Types.でんき
                        power = 100
                    elif field == Fields.サイコ:
                        waza.type = Types.エスパー
                        power = 100
            case "サイコブレイド":
                power = 80
                if field == Fields.サイコ:
                    power = 120
            case _:
                if waza.add_power > -1:
                    power = int(waza.power * waza.add_power)
                else:
                    power = waza.power
        # endregion

        # region 攻撃側の特性補正
        key: str = "攻撃特性:" + attacker.ability
        match attacker.ability:
            case "エレキスキン" | "スカイスキン" | "フェアリースキン" | "フリーズスキン":
                if waza.type == Types.ノーマル:
                    waza.type = DamageCalc.__skin_abilities[attacker.ability]
                    hosei[key] = 4915
            case "ノーマルスキン":
                if waza.type != Types.ノーマル:
                    waza.type = Types.ノーマル
                    hosei[key] = 4915
            case "てつのこぶし":
                if waza.name in DamageCalc.__punch_moves:
                    hosei[key] = 4915
            case "すてみ":
                if waza.name in DamageCalc.__recoil_moves:
                    hosei[key] = 4915
            case "ちからずく":
                if waza.has_effect:
                    hosei[key] = 5325
            case "すなのちから":
                if waza.type in [Types.じめん, Types.いわ, Types.はがね] and weather == Weathers.砂嵐:
                    hosei[key] = 5325
            case "アナライズ":
                if attacker.ability_enable:
                    hosei[key] = 5325
            case "かたいツメ":
                if waza.is_touch:
                    hosei[key] = 5325
            case "パンクロック":
                if waza.name in DamageCalc.__sound_moves:
                    hosei[key] = 4915
            case "フェアリーオーラ":
                if waza.type == Types.フェアリー:
                    hosei[key] = 3072 if defender.ability == "オーラブレイク" else 5448
            case "ダークオーラ":
                if waza.type == Types.あく:
                    hosei[key] = 3072 if defender.ability == "オーラブレイク" else 5448
            case "きれあじ":
                if waza.name in DamageCalc.__slash_moves:
                    hosei[key] = 6144
            case "テクニシャン":
                if waza.power <= 60:
                    hosei[key] = 6144
            case "ねつぼうそう":
                if waza.category == 特殊 and attacker.ability_enable:
                    hosei[key] = 6144
            case "どくぼうそう":
                if waza.category == 物理 and attacker.ability_enable:
                    hosei[key] = 6144
            case "がんじょうあご":
                if waza.name in DamageCalc.__fung_moves:
                    hosei[key] = 6144
            case "メガランチャー":
                if waza.name in DamageCalc.__blast_moves:
                    hosei[key] = 6144
            case "はがねのせいしん":
                if waza.type == Types.はがね:
                    hosei[key] = 6144
            case "そうだいしょう":
                value = attacker.ability_value
                if len(value) > 0:
                    hosei[key] = DamageCalc.__soudaisyou_values[attacker.ability_value]
            case "とうそうしん":
                value = attacker.ability_value
                if len(value) > 0:
                    hosei[key] = DamageCalc.__tousoushin_values[attacker.ability_value]

        # endregion

        # region 防御側の特性補正
        key: str = "防御特性:" + defender.ability
        match defender.ability:
            case "たいねつ":
                if waza.type == Types.ほのお:
                    hosei[key] = 2048
            case "かんそうはだ":
                if waza.type == Types.ほのお:
                    hosei[key] = 5120
        # endregion

        # region 攻撃側の持ち物補正
        key: str = "持ち物:" + attacker.item
        match attacker.item:
            case "ちからのハチマキ":
                if waza.category == 物理:
                    hosei[key] = 4505
            case "ものしりメガネ":
                if waza.category == 特殊:
                    hosei[key] = 4505
            case "パンチグローブ":
                if waza.name in DamageCalc.__punch_moves:
                    hosei[key] = 4506
            case "こんごうだま":
                if attacker.name == "ディアルガ" and waza.type in [Types.はがね, Types.ドラゴン]:
                    hosei[key] = 4915
            case "しらたま":
                if attacker.name == "パルキア" and waza.type in [Types.みず, Types.ドラゴン]:
                    hosei[key] = 4915
            case "はっきんだま":
                if attacker.name == "ギラティナ(オリジン)" and waza.type in [Types.ゴースト, Types.ドラゴン]:
                    hosei[key] = 4915
            case "こころのしずく":
                if attacker.name in ["ラティアス", "ラティオス"] and waza.type in [Types.エスパー, Types.ドラゴン]:
                    hosei[key] = 4915
            case "ノーマルジュエル":
                if waza.type == Types.ノーマル:
                    hosei[key] = 5325
            case "いどのめん":
                if attacker.name == "オーガポン(水)":
                    hosei[key] = 4915
            case "かまどのめん":
                if attacker.name == "オーガポン(炎)":
                    hosei[key] = 4915
            case "いしずえのめん":
                if attacker.name == "オーガポン(岩)":
                    hosei[key] = 4915

        if attacker.item in DamageCalc.__type_buff_items.keys():
            # タイプ強化アイテム系
            t = DamageCalc.__type_buff_items.get(attacker.item)
            if t is not None and t == waza.type:
                hosei[attacker.item] = 4915
        # endregion

        # region 技による補正
        key: str = "技:" + waza.name
        match waza.name:
            case "ソーラービーム" | "ソーラーブレード":
                if weather in [Weathers.雨, Weathers.砂嵐, Weathers.雪]:
                    hosei[key] = 2048
            case "ワイドフォース":
                if field == Fields.サイコ and not attacker.is_flying:
                    hosei[key] = 6144
            case "ライジングボルト":
                if field == Fields.エレキ and not defender.is_flying:
                    hosei[key] = 8192
            case _:
                if attacker.charging and waza.type == Types.でんき:
                    hosei[key] = 8192
                if waza.power_hosei == 2.0:
                    hosei[key] = 8192
                if waza.power_hosei == 1.5:
                    hosei[key] = 6144
        # endregion

        # region フィールド補正
        key: str = "フィールド:" + field.name
        match field:
            case Fields.エレキ:
                if waza.type == Types.でんき and not attacker.is_flying:
                    hosei[key] = 5325
            case Fields.サイコ:
                if waza.type == Types.エスパー and not attacker.is_flying:
                    hosei[key] = 5325
            case Fields.グラス:
                if waza.type == Types.くさ and not attacker.is_flying:
                    hosei[key] = 5325
                if waza.name in ["じしん", "じならし", "マグニチュード"] and not defender.is_flying:
                    hosei[key] = 2048
            case Fields.ミスト:
                if waza.type == Types.ドラゴン and not defender.is_flying:
                    hosei[key] = 2048
        # endregion

        # 最終補正値の計算
        hosei_total = Decimal('4096')
        for value in hosei.values():
            hosei_total = (hosei_total * value / 4096).quantize(
                exp=DECIMAI_ZERO, rounding=ROUND_HALF_UP)

        power = (power * hosei_total / 4096).quantize(
            exp=DECIMAI_ZERO, rounding=ROUND_HALF_DOWN)

        return int(power) if power > 0 else 1

    # 攻撃力の算出
    @staticmethod
    def __get_attack_power(
            attacker: 'Pokemon',
            defender: 'Pokemon',
            waza: Waza,
            weather: Weathers,
            field: Fields) -> int:
        base_power: int
        hosei: dict[str, int] = {}

        # イカサマは相手の攻撃力を参照
        match waza.name:
            case "イカサマ":
                if waza.critical and defender.rank.A < 0:
                    base_power = defender[StatsKey.A]
                else:
                    base_power = defender.rankedA
            case "ボディプレス":
                if waza.critical and attacker.rank.B < 0:
                    base_power = attacker[StatsKey.B]
                else:
                    base_power = attacker.rankedB
            case _:
                statskey = StatsKey.A if waza.category == 物理 else StatsKey.C
                # 急所時、攻撃ランクが0未満なら0として扱う
                if waza.critical and attacker.rank[statskey] < 0:
                    base_power = attacker[statskey]
                # 防御側が特性てんねんの場合、ランク補正なしで計算する
                elif defender.ability == "てんねん":
                    base_power = attacker[statskey]
                else:
                    base_power = attacker.get_ranked_stats(statskey)

        power: Decimal = Decimal(base_power)

        # region 攻撃側の特性補正
        key = "攻撃特性:" + attacker.ability
        match attacker.ability:
            case "はりきり":  # 攻撃補正でなく攻撃力そのものに乗る
                if waza.category == 物理:
                    power = (power * 6144 / 4096).quantize(
                        DECIMAI_ZERO, rounding=ROUND_FLOOR)
            case "スロースタート" | "よわき":
                if attacker.ability_enable:
                    hosei[key] = 2048
            case "こだいかっせい" | "クォークチャージ":
                if attacker.ability_value == "A" and waza.category == 物理:
                    hosei[key] = 5325
                elif attacker.ability_value == "C" and waza.category == 特殊:
                    hosei[key] = 5325
            case "トランジスタ":
                if waza.type == DamageCalc.__type_buff_abilities[attacker.ability]:
                    hosei[key] = 5325
            case "ハイドロエンジン":
                if waza.category == 特殊 and field == Fields.エレキ:
                    hosei[key] = 5461
            case "ひひいろのこどう":
                if waza.category == 物理 and weather == Weathers.晴れ:
                    hosei[key] = 5461
            case "フラワーギフト":
                if weather == Weathers.晴れ and waza.category == 物理:
                    hosei[key] = 6144
            case "こんじょう":
                if attacker.ailment != Ailments.なし and waza.category == 物理:
                    hosei[key] = 6144
            case "しんりょく" | "もうか" | "もらいび" | "げきりゅう" | "むしのしらせ":
                if attacker.ability_enable and waza.type == DamageCalc.__type_buff_abilities[attacker.ability]:
                    hosei[key] = 6144
            case "サンパワー":
                if weather == Weathers.晴れ and waza.category == 特殊:
                    hosei[key] = 6144
            case "プラス" | "マイナス":
                if attacker.ability_enable and waza.category == 特殊:
                    hosei[key] = 6144
            case "いわはこび" | "はがねつかい" | "りゅうのあぎと":
                if waza.type == DamageCalc.__type_buff_abilities[attacker.ability]:
                    hosei[key] = 6144
            case "ごりむちゅう":
                if waza.category == 物理:
                    hosei[key] = 6144
            case "ちからもち" | "ヨガパワー":
                if waza.category == 物理:
                    hosei[key] = 8192
            case "すいほう":
                if waza.type == Types.みず:
                    hosei[key] = 8192
        # endregion

        # region 防御側の特性補正
        key = "防御特性:" + defender.ability
        match defender.ability:
            case "わざわいのおふだ":
                # イカサマ、ボディプレスのダメージも下げる
                if waza.category == 物理 and attacker.ability != "わざわいのおふだ":
                    hosei[key] = 3072
            case "わざわいのうつわ":
                if waza.category == 特殊 and attacker.ability != "わざわいのうつわ":
                    hosei[key] = 3072
            case "あついしぼう":
                if waza.type in [Types.ほのお, Types.こおり]:
                    hosei[key] = 2048
            case "きよめのしお":
                if waza.type in [Types.ゴースト]:
                    hosei[key] = 2048
            case "すいほう":
                if waza.type == Types.ほのお:
                    hosei[key] = 2048
        # endregion

        # region 攻撃側の持ち物補正
        key = "持ち物:" + attacker.item
        match attacker.item:
            case "こだわりハチマキ":
                if waza.category == 物理:
                    hosei[key] = 6144
            case "こだわりメガネ":
                if waza.category == 特殊:
                    hosei[key] = 6144
            case "ふといホネ":
                if attacker.name in ["カラカラ", "ガラガラ", "アローラガラガラ"] and waza.category == 物理:
                    hosei[key] = 8192
            case "しんかいのキバ":
                if attacker.name == "パールル" and waza.category == 特殊:
                    hosei[key] = 8192
            case "でんきだま":
                if attacker.name == "ピカチュウ":
                    hosei[key] = 8192
        # endregion

        # 最終補正値の計算
        hosei_total = Decimal('4096')
        for value in hosei.values():
            hosei_total = (hosei_total * value / 4096).quantize(
                exp=DECIMAI_ZERO, rounding=ROUND_HALF_UP)

        power = (power * hosei_total / 4096).quantize(
            exp=DECIMAI_ZERO, rounding=ROUND_HALF_DOWN)
        return int(power) if power > 1 else 1

    # 防御力の算出
    @staticmethod
    def __get_defence_power(
            attacker: 'Pokemon',
            defender: 'Pokemon',
            waza: Waza,
            weather: Weathers,
            field: Fields) -> int:
        power: Decimal
        hosei: dict[str, int] = {}

        # 基本防御力（急所時、防御ランクが1以上なら0で計算する）
        if waza.category == 物理 or waza.name in ["サイコショック", "サイコブレイク"]:
            df_key = StatsKey.B
        else:
            df_key = StatsKey.D
        if waza.critical and defender.rank[df_key] > 0:
            power = Decimal(defender[df_key])
        else:
            power = Decimal(defender.get_ranked_stats(df_key))

        # region SV準伝のわざわいシリーズ対応、防御力が25%減少。暫定実装
        if (df_key == StatsKey.B and attacker.ability == "わざわいのつるぎ" and defender.ability != "わざわいのつるぎ") or \
                (df_key == StatsKey.D and attacker.ability == "わざわいのたま" and defender.ability != "わざわいのたま"):
            power = (power * 3072 / 4096).quantize(
                DECIMAI_ZERO, rounding=ROUND_FLOOR)
        # endregion

        # 岩タイプは砂嵐で特防が1.5倍
        if weather == Weathers.砂嵐 and defender.has_type(Types.いわ) and df_key == StatsKey.D:
            power = (power * 6144 / 4096).quantize(
                DECIMAI_ZERO, rounding=ROUND_FLOOR)

        # 氷タイプは雪で防御が1.5倍
        if weather == Weathers.雪 and defender.has_type(Types.こおり) and df_key == StatsKey.B:
            power = (power * 6144 / 4096).quantize(
                DECIMAI_ZERO, rounding=ROUND_FLOOR)

        # region 防御側の特性補正
        key = "防御特性:" + defender.ability
        match defender.ability:
            case "こだいかっせい" | "クォークチャージ":
                if defender.ability_value == "B" and df_key == StatsKey.B:
                    hosei[key] = 5325
                elif defender.ability_value == "D" and df_key == StatsKey.D:
                    hosei[key] = 5325
            case "フラワーギフト":
                if weather == Weathers.晴れ and df_key == StatsKey.D:
                    hosei[key] = 6144
            case "ふしぎなうろこ":
                if defender.ability_enable and df_key == StatsKey.B:
                    hosei[key] = 6144
            case "くさのけがわ":
                if field == Fields.グラス and df_key == StatsKey.B:
                    hosei[key] = 6144
            case "ファーコート":
                if waza.category == 物理:
                    hosei[key] = 8192
            case "こだいかっせい" | "クォークチャージ":
                if defender.ability_value == "B" and df_key == StatsKey.B:
                    hosei[key] = 5325
                elif defender.ability_value == "D" and df_key == StatsKey.D:
                    hosei[key] = 5325
        # endregion

        # region 防御側の持ち物補正
        key = "持ち物:" + defender.item
        match defender.item:
            case "しんかのきせき":
                hosei[key] = 6144
            case "とつげきチョッキ":
                if df_key == StatsKey.D:
                    hosei[key] = 6144
        # endregion

        # 最終補正値の計算
        hosei_total = Decimal('4096')
        for value in hosei.values():
            hosei_total = (hosei_total * value / 4096).quantize(
                exp=DECIMAI_ZERO, rounding=ROUND_HALF_UP)

        power = (power * hosei_total / 4096).quantize(
            exp=DECIMAI_ZERO, rounding=ROUND_HALF_DOWN)
        return int(power) if power > 1 else 1

    # ダメージ補正値の算出
    @staticmethod
    def __get_damage_hosei(attacker: 'Pokemon', defender: 'Pokemon', waza: Waza, count: int) -> int:
        hosei: dict[str, int] = {}
        type_effective: float = defender.get_type_effective(waza)

        # region 壁の補正
        key = "壁:" + defender.wall.name
        if ((defender.wall.name in ["リフレクター", "オーロラベール"] and waza.category == 物理 and not waza in ["かわらわり", "サイコファング"]) or (defender.wall.name in ["ひかりのかべ", "オーロラベール"] and waza.category == 特殊)) and not waza.critical and attacker.ability != "すりぬけ":
            hosei[key] = 2048
        # endregion

        # region 攻撃側の特性補正
        key = "攻撃特性:" + attacker.ability
        match attacker.ability:
            case "ブレインフォース":
                pass  # 自分の技のタイプ相性が効果抜群の場合、さらに威力が1.25倍になるらしい。
            case "スナイパー":
                if waza.critical and attacker.ability_enable:
                    hosei[key] = 6144
            case "アクセルブレイク" | "イナズマドライブ":
                pass # 弱点突いたら1.33倍
            case "いろめがね":
                if type_effective < 1.0:
                    hosei[key] = 8192
        # endregion

        # region 防御側の特性補正
        key = "防御特性:" + defender.ability
        match defender.ability:
            case "もふもふ":
                if waza.type == Types.ほのお:
                    hosei["もふもふ(ほのお)"] = 6144
                if waza.is_touch:
                    hosei["もふもふ(接触)"] = 2048
            case "マルチスケイル" | "ファントムガード":
                if defender.ability_enable and attacker.ability != "かたやぶり" and count == 0:
                    hosei[key] = 2048
            case "パンクロック":
                if waza.name in DamageCalc.__sound_moves:
                    hosei[key] = 2048
            case "こおりのりんぷん":
                if waza.category == 特殊:
                    hosei[key] = 2048
            case "フレンドガード":
                pass  # 自分以外の味方が受けるダメージが3 / 4に軽減される。(ダブルバトル用)
            case "ハードロック" | "フィルター" | "プリズムアーマー":
                if type_effective > 1.0:
                    hosei[key] = 3072
        # endregion

        # region 攻撃側の持ち物補正
        key = "攻撃持ち物:" + attacker.item
        match attacker.item:
            case "たつじんのおび":
                if type_effective > 1.0:
                    hosei[key] = 4915
            case "いのちのたま":
                hosei[key] = 5324
            case "メトロノーム":
                pass  # 誰も使わないはず
        # endregion

        # 半減きのみ TBD

        # 最終補正値の計算
        hosei_total = Decimal('4096')
        for value in hosei.values():
            hosei_total = (hosei_total * value / 4096).quantize(
                exp=DECIMAI_ZERO, rounding=ROUND_HALF_UP)
        return int(hosei_total)

    # ダメージの算出
    @staticmethod
    def __get_fix_damages(
            attacker: 'Pokemon',
            defender: 'Pokemon',
            waza: Waza,
            waza_power: int,
            attack_power: int,
            defence_power: int,
            damage_hosei: int,
            weather: Weathers) -> list[int]:

        # 攻撃側のレベル × 2 ÷ 5 ＋ 2 → 切り捨て
        damage: Decimal = Decimal(attacker.lv * 2 / 5 + 2).quantize(
            DECIMAI_ZERO, rounding=ROUND_FLOOR)

        # × 最終威力 × 最終攻撃 ÷ 最終防御 → 切り捨て
        damage = (damage * waza_power * attack_power / defence_power).quantize(
            DECIMAI_ZERO, rounding=ROUND_FLOOR)

        # ÷ 50 ＋ 2 → 切り捨て
        damage = (damage / 50 + 2).quantize(
            DECIMAI_ZERO, rounding=ROUND_FLOOR)

        # × 複数対象 3072 ÷ 4096 → 五捨五超入 TBD
        # × おやこあい(2発目) 1024 ÷ 4096 → 五捨五超入 TBD?

        # × 天気弱化 2048 ÷ 4096 → 五捨五超入
        # × 天気強化 6144 ÷ 4096 → 五捨五超入
        if attacker.item != "ばんのうがさ" and defender.item != "ばんのうがさ":
            match weather:
                case Weathers.晴れ:
                    if waza.type == Types.ほのお or waza.name == "ハイドロスチーム":
                        damage = (damage * 6144 / 4096).quantize(
                            DECIMAI_ZERO, rounding=ROUND_HALF_DOWN)
                    elif waza.type == Types.みず:
                        damage = (damage * 2048 / 4096).quantize(
                            DECIMAI_ZERO, rounding=ROUND_HALF_DOWN)
                case Weathers.雨:
                    if waza.type == Types.みず:
                        damage = (damage * 6144 / 4096).quantize(
                            DECIMAI_ZERO, rounding=ROUND_HALF_DOWN)
                    elif waza.type == Types.ほのお:
                        damage = (damage * 2048 / 4096).quantize(
                            DECIMAI_ZERO, rounding=ROUND_HALF_DOWN)

        # × 急所 6144 ÷ 4096 → 五捨五超入
        if waza.critical:
            damage = (damage * 6144 / 4096).quantize(
                DECIMAI_ZERO, rounding=ROUND_HALF_DOWN)

        damages: list[int] = []
        for i in range(0, 16):
            # × 乱数(0.85, 0.86, …… 0.99, 1.00 の何れか) → 切り捨て
            rnd = Decimal('0.85') + Decimal(str(i / 100))
            rnd_damage = (damage * rnd).quantize(
                DECIMAI_ZERO, rounding=ROUND_FLOOR)

            # × タイプ一致 6144  (更にテラス一致なら8192) (適応力なら8192) ÷ 4096 → 五捨五超入
            value = 4096
            type_equal: bool = (waza.type in attacker.type)
            teras_type_equal: bool = waza.type == attacker.battle_terastype

            match attacker.ability:
                case "へんげんじざい" | "リベロ":
                    if attacker.ability_value == "有効":
                        value = 8192 if teras_type_equal else 6144
                    elif attacker.ability_value == "無効" and teras_type_equal:
                        value = 6144
                case "てきおうりょく":
                    # テラスタイプのみ一致判定がある。一致で2倍、元タイプとも一致した場合、2.25倍
                    if teras_type_equal:
                        value = 9216 if type_equal else 8192
                case _:
                    if type_equal and teras_type_equal:
                        value = 8192
                    elif type_equal or teras_type_equal:
                        value = 6144

            if value != 4096:
                rnd_damage = (rnd_damage * value / 4096).quantize(
                    DECIMAI_ZERO, rounding=ROUND_HALF_DOWN)

            # × タイプ相性 → 切り捨て
            rnd_damage = (rnd_damage * Decimal(defender.get_type_effective(waza))).\
                quantize(DECIMAI_ZERO, rounding=ROUND_FLOOR)

            # × やけど 2048 ÷ 4096 → 五捨五超入 TBD
            if attacker.ailment == Ailments.やけど and waza.category == 物理 and waza.name != "からげんき":
                rnd_damage = (rnd_damage * 2048 / 4096).quantize(
                DECIMAI_ZERO, rounding=ROUND_HALF_DOWN)

            # × ダメージの補正値 ÷ 4096 → 五捨五超入
            rnd_damage = (rnd_damage * damage_hosei / 4096).quantize(
                DECIMAI_ZERO, rounding=ROUND_HALF_DOWN)

            damages.append(int(rnd_damage))

        return damages

    # ランク補正の適用
    @staticmethod
    def add_rank_value(stats: int, rank: int) -> int:
        if rank > 0:
            stats = Decimal(stats / 2 * (2 + rank)).quantize(DECIMAI_ZERO, rounding=ROUND_FLOOR)
        elif rank < 0:
            stats = Decimal(stats / (2 + rank) * 2).quantize(DECIMAI_ZERO, rounding=ROUND_FLOOR)
        return int(stats)

    # region 特定の技や特性などの定義
    # スキン系特性
    __skin_abilities: dict[str, Types] = {
        "エレキスキン": Types.でんき,
        "スカイスキン": Types.ひこう,
        "フェアリースキン": Types.フェアリー,
        "フリーズスキン": Types.こおり,
    }
    # タイプ強化系の特性
    __type_buff_abilities: dict[str, Types] = {
        "しんりょく": Types.くさ,
        "もうか": Types.ほのお,
        "もらいび": Types.ほのお,
        "げきりゅう": Types.みず,
        "むしのしらせ": Types.むし,
        "いわはこび": Types.いわ,
        "はがねつかい": Types.はがね,
        "トランジスタ": Types.でんき,
        "りゅうのあぎと": Types.ドラゴン,
    }
    # パンチ技(てつのこぶし)
    __punch_moves = [
        "アームハンマー",
        "かみなりパンチ",
        "きあいパンチ",
        "グロウパンチ",
        "コメットパンチ",
        "シャドーパンチ",
        "ドレインパンチ",
        "ばくれつパンチ",
        "バレットパンチ",
        "ほのおのパンチ",
        "マッハパンチ",
        "メガトンパンチ",
        "れいとうパンチ"
    ]
    # 反動技(すてみ)
    __recoil_moves = [
        "アフロブレイク",
        "ウッドハンマー",
        "じごくぐるま",
        "すてみタックル",
        "とっしん",
        "とびげり",
        "とびひざげり",
        "もろはのずつき",
        "フレアドライブ",
        "ブレイブバード",
        "ボルテッカー",
        "ワイルドボルト"
    ]
    # 音技(パンクロックとか)
    __sound_moves = [
        "いびき",
        "うたかたのアリア",
        "エコーボイス",
        "さわぐ",
        "スケイルノイズ",
        "チャームボイス",
        "バークアウト",
        "ハイパーボイス",
        "ばくおんぱ",
        "むしのさざめき",
        "りんしょう",
        "オーバードライブ",
        "ぶきみなじゅもん"
    ]
    # キバ技(がんじょうあご)
    __fung_moves = [
        "かみつく",
        "かみくだく",
        "ひっさつまえば",
        "ほのおのキバ",
        "かみなりのキバ",
        "こおりのキバ",
        "どくどくのキバ",
        "サイコファング",
        "エラがみ",
        "くらいつく"
    ]
    # 波動技(メガランチャー)
    __blast_moves = [
        "あくのはどう",
        "はどうだん",
        "みずのはどう",
        "りゅうのはどう",
        "だいちのはどう",
        "こんげんのはどう"
    ]
    # 切る技(きれあじ)
    __slash_moves = [
        "アクアカッター",
        "いあいぎり",
        "エアカッター",
        "エアスラッシュ",
        "がんせきアックス",
        "きょじゅうざん",
        "きりさく",
        "クロスポイズン",
        "サイコカッター",
        "シェルブレード",
        "シザークロス",
        "しんぴのつるぎ",
        "せいなるつるぎ",
        "ソーラーブレード",
        "つじぎり",
        "つばめがえし",
        "ドゲザン",
        "ネズミざん",
        "はっぱカッター",
        "ひけん・ちえなみ",
        "むねんのつるぎ",
        "リーフブレード",
        "れんぞくぎり"
    ]
    # タイプ強化アイテム
    __type_buff_items = {
        "シルクのスカーフ": Types.ノーマル,
        "もくたん": Types.ほのお,
        "しんぴのしずく": Types.みず,
        "じしゃく": Types.でんき,
        "きせきのタネ": Types.くさ,
        "とけないこおり": Types.こおり,
        "くろおび": Types.かくとう,
        "どくバリ": Types.どく,
        "やわからいすな": Types.じめん,
        "するどいくちばし": Types.ひこう,
        "まがったスプーン": Types.エスパー,
        "ぎんのこな": Types.むし,
        "かたいいし": Types.いわ,
        "のろいのおふだ": Types.ゴースト,
        "りゅうのキバ": Types.ドラゴン,
        "くろいメガネ": Types.あく,
        "メタルコード": Types.はがね,
        "せいれいプレート": Types.フェアリー,
        "うしおのおこう": Types.みず,
        "さざなみのおこう": Types.みず,
        "おはなのおこう": Types.くさ,
        "がんせきおこう": Types.いわ,
        "あやしいおこう": Types.エスパー,
        "ようせいのハネ": Types.フェアリー,
    }

    # そうだいしょう倍率
    __soudaisyou_values = {
        "1.0": 4096, "1.1": 4506, "1.2": 4915, "1.3": 5325, "1.4": 5734, "1.5": 6144,
    }

    #とうそうしん倍率
    __tousoushin_values = {
        "1.0": 4096, "1.25": 5120, "0.75": 3072,
    }

    __damages_at_weight = ((10, 20), (25, 40), (50, 60), (100, 80), (200, 100))
    # endregion
