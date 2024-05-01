import dataclasses
import datetime
import sqlite3
from time import time
from typing import Optional

from component.frames.common import ChosenFrame, PartyFrame
from component.frames.whole import RecordFrame


@dataclasses.dataclass
class Battle:
    id: Optional[int]
    date: Optional[int]
    result: Optional[int]
    favorite: Optional[int]
    opponent_tn: Optional[str]
    opponent_rank: Optional[int]
    battle_memo: Optional[str]
    player_party_num: Optional[int]
    player_party_subnum: Optional[int]
    player_pokemon1: Optional[str]
    player_pokemon2: Optional[str]
    player_pokemon3: Optional[str]
    player_pokemon4: Optional[str]
    player_pokemon5: Optional[str]
    player_pokemon6: Optional[str]
    opponent_pokemon1: Optional[str]
    opponent_pokemon2: Optional[str]
    opponent_pokemon3: Optional[str]
    opponent_pokemon4: Optional[str]
    opponent_pokemon5: Optional[str]
    opponent_pokemon6: Optional[str]
    player_choice1: Optional[str]
    player_choice2: Optional[str]
    player_choice3: Optional[str]
    opponent_choice1: Optional[str]
    opponent_choice2: Optional[str]
    opponent_choice3: Optional[str]

    def set_battle(
        record_frame: RecordFrame,
        party_frames: list[PartyFrame],
        chosen_frames: list[ChosenFrame],
    ):
        from pokedata.loader import get_party_csv

        file = get_party_csv().split("party/csv/")[1]

        return Battle(
            None,
            int(time()),
            record_frame.result,
            record_frame.favo.get(),
            record_frame.tn.get(),
            record_frame.rank.get(),
            record_frame.memo.get("1.0", "end-1c"),
            file.split("-")[0],
            file.split("-")[1].split("_")[0],
            party_frames[0]._pokemon_list[0].pid,
            party_frames[0]._pokemon_list[1].pid,
            party_frames[0]._pokemon_list[2].pid,
            party_frames[0]._pokemon_list[3].pid,
            party_frames[0]._pokemon_list[4].pid,
            party_frames[0]._pokemon_list[5].pid,
            party_frames[1]._pokemon_list[0].pid,
            party_frames[1]._pokemon_list[1].pid,
            party_frames[1]._pokemon_list[2].pid,
            party_frames[1]._pokemon_list[3].pid,
            party_frames[1]._pokemon_list[4].pid,
            party_frames[1]._pokemon_list[5].pid,
            chosen_frames[0]._pokemon_list[0],
            chosen_frames[0]._pokemon_list[1],
            chosen_frames[0]._pokemon_list[2],
            chosen_frames[1]._pokemon_list[0],
            chosen_frames[1]._pokemon_list[1],
            chosen_frames[1]._pokemon_list[2],
        )


class DB_battle:
    __db = sqlite3.connect("database/battle.db", check_same_thread=False)

    def register_battle(battle):
        cur = DB_battle.__db.cursor()

        cur.executemany(
            "INSERT INTO battle values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (battle,),
        )
        cur.close()
        DB_battle.__db.commit()

    @staticmethod
    def get_all_battle_data():
        sql = "SELECT * FROM battle".format()
        result = DB_battle.__select(sql)
        return result

    @staticmethod
    def get_battle_data_by_date(from_date: int, to_date: int):
        sql = "SELECT * FROM battle where date BETWEEN {0} and {1}".format(
            from_date, to_date
        )
        result = DB_battle.__select(sql)
        return result

    @staticmethod
    def get_battle_data_by_date_and_party_num(from_date: int, to_date: int, party_num):
        sql = "SELECT * FROM battle where player_party_num={0} and date BETWEEN {1} and {2}".format(
            party_num, from_date, to_date
        )
        result = DB_battle.__select(sql)
        return result

    @staticmethod
    def get_battle_data_by_date_and_party_subnum(
        from_date: int, to_date: int, party_num, party_subnum
    ):
        sql = "SELECT * FROM battle where player_party_num={0} and player_party_subnum={1} and date BETWEEN {2} and {3}".format(
            party_num, party_subnum, from_date, to_date
        )
        result = DB_battle.__select(sql)
        return result

    @staticmethod
    def calc_kp(from_date, to_date):
        sql = "select pokemon,count(*) as kp From (select opponent_pokemon1 as pokemon from battle where date >= {0} and date <= {1} union ALL select opponent_pokemon2 as pokemon from battle where date >= {2} and date <= {3} union ALL select opponent_pokemon3 as pokemon from battle where date >= {4} and date <= {5} union ALL select opponent_pokemon4 as pokemon from battle where date >= {6} and date <= {7} union ALL select opponent_pokemon5 as pokemon from battle where date >= {8} and date <= {9} union ALL select opponent_pokemon6 as pokemon from battle where date >= {10} and date <= {11}) GROUP by pokemon ORDER by kp DESC".format(
            from_date,
            to_date,
            from_date,
            to_date,
            from_date,
            to_date,
            from_date,
            to_date,
            from_date,
            to_date,
            from_date,
            to_date,
        )
        result = DB_battle.__select(sql)
        return result

    @staticmethod
    def calc_kp_for_party_num(from_date, to_date, party_num):
        sql = "select pokemon,count(*) as kp From (select opponent_pokemon1 as pokemon from battle where date >= {0} and date <= {1} and player_party_num={2} union ALL select opponent_pokemon2 as pokemon from battle where date >= {3} and date <= {4} and player_party_num={5} union ALL select opponent_pokemon3 as pokemon from battle where date >= {6} and date <= {7} and player_party_num={8} union ALL select opponent_pokemon4 as pokemon from battle where date >= {9} and date <= {10} and player_party_num={11} union ALL select opponent_pokemon5 as pokemon from battle where date >= {12} and date <= {13} and player_party_num={14} union ALL select opponent_pokemon6 as pokemon from battle where date >= {15} and date <= {16} and player_party_num={17}) GROUP by pokemon ORDER by kp DESC".format(
            from_date,
            to_date,
            party_num,
            from_date,
            to_date,
            party_num,
            from_date,
            to_date,
            party_num,
            from_date,
            to_date,
            party_num,
            from_date,
            to_date,
            party_num,
            from_date,
            to_date,
            party_num,
        )
        result = DB_battle.__select(sql)
        return result

    @staticmethod
    def calc_kp_for_party_subnum(from_date, to_date, party_num, party_subnum):
        sql = "select pokemon,count(*) as kp From (select opponent_pokemon1 as pokemon from battle where date >= {0} and date <= {1} and player_party_num={2} and player_party_subnum={3} union ALL select opponent_pokemon2 as pokemon from battle where date >= {4} and date <= {5} and player_party_num={6} and player_party_subnum={7} union ALL select opponent_pokemon3 as pokemon from battle where date >= {8} and date <= {9} and player_party_num={10} and player_party_subnum={11} union ALL select opponent_pokemon4 as pokemon from battle where date >= {12} and date <= {13} and player_party_num={14} and player_party_subnum={15} union ALL select opponent_pokemon5 as pokemon from battle where date >= {16} and date <= {17} and player_party_num={18} and player_party_subnum={19} union ALL select opponent_pokemon6 as pokemon from battle where date >= {20} and date <= {21} and player_party_num={22} and player_party_subnum={23}) GROUP by pokemon ORDER by kp DESC".format(
            from_date,
            to_date,
            party_num,
            party_subnum,
            from_date,
            to_date,
            party_num,
            party_subnum,
            from_date,
            to_date,
            party_num,
            party_subnum,
            from_date,
            to_date,
            party_num,
            party_subnum,
            from_date,
            to_date,
            party_num,
            party_subnum,
            from_date,
            to_date,
            party_num,
            party_subnum,
        )
        result = DB_battle.__select(sql)
        return result

    @staticmethod
    def count_record(from_date, to_date):
        sql = "select count(*) From battle where date >= {0} and date <= {1} ".format(
            from_date, to_date
        )
        result = DB_battle.__select(sql)
        return result[0]

    @staticmethod
    def count_record_for_party_num(from_date, to_date, partyNum):
        sql = "select count(*) From battle where date >= {0} and date <= {1} and player_party_num={2}".format(
            from_date, to_date, partyNum
        )
        result = DB_battle.__select(sql)
        return result[0]

    @staticmethod
    def count_record_for_party_subnum(from_date, to_date, partyNum, partySubNum):
        sql = "select count(*) From battle where date >= {0} and date <= {1} and player_party_num={2} and player_party_subnum={3}".format(
            from_date, to_date, partyNum, partySubNum
        )
        result = DB_battle.__select(sql)
        return result[0]

    @staticmethod
    def count_win(from_date, to_date):
        sql = "select count(*) From battle where date >= {0} and date <= {1} and result=1 ".format(
            from_date, to_date
        )
        result = DB_battle.__select(sql)
        return result[0]

    @staticmethod
    def count_win_for_party_num(from_date, to_date, partyNum):
        sql = "select count(*) From battle where date >= {0} and date <= {1} and result=1 and player_party_num={2}".format(
            from_date, to_date, partyNum
        )
        result = DB_battle.__select(sql)
        return result[0]

    @staticmethod
    def count_win_for_party_subnum(from_date, to_date, partyNum, partySubNum):
        sql = "select count(*) From battle where date >= {0} and date <= {1} and result=1 and player_party_num={2} and player_party_subnum={3}".format(
            from_date, to_date, partyNum, partySubNum
        )
        result = DB_battle.__select(sql)
        return result[0]

    @staticmethod
    def get_recent_date():
        sql = "select Max(date) From battle "
        result = DB_battle.__select(sql)
        return result[0]

    @staticmethod
    def get_my_party():
        sql = "select player_pokemon1, player_pokemon2, player_pokemon3, player_pokemon4, player_pokemon5, player_pokemon6, player_party_num, player_party_subnum from battle where date in(select MAX(date) from battle group by player_pokemon1, player_pokemon2, player_pokemon3, player_pokemon4, player_pokemon5, player_pokemon6) order by date desc"
        result = DB_battle.__select(sql)
        del result[9:]
        return result

    @staticmethod
    def get_my_party_for_party_num(party_num):
        sql = "select player_pokemon1, player_pokemon2, player_pokemon3, player_pokemon4, player_pokemon5, player_pokemon6 from battle where player_party_num={0}".format(
            party_num
        )
        result = DB_battle.__select(sql)
        sorted_sesult = set(tuple(sorted(t)) for t in result)
        result_list = list(sorted_sesult)
        if len(result_list) == 1:
            return result_list
        else:
            return -1

    @staticmethod
    def get_my_party_for_party_subnum(party_num, party_subnum):
        sql = "select player_pokemon1, player_pokemon2, player_pokemon3, player_pokemon4, player_pokemon5, player_pokemon6 from battle where player_party_num={0} and player_party_subnum={1}".format(
            party_num, party_subnum
        )
        result = DB_battle.__select(sql)
        sorted_sesult = set(tuple(sorted(t)) for t in result)
        result_list = list(sorted_sesult)
        if len(result_list) == 1:
            return result_list
        else:
            return -1

    @staticmethod
    def get_win_rate(kpList: list, from_date, to_date):
        cur = DB_battle.__db.cursor()
        winRateList = []
        for pokeName in kpList:
            paramList = (
                from_date,
                to_date,
                pokeName[0],
                pokeName[0],
                pokeName[0],
                pokeName[0],
                pokeName[0],
                pokeName[0],
            )
            sql = "select count(*) from battle where date >=? and date <=? and (opponent_pokemon1=? or opponent_pokemon2=? or opponent_pokemon3=? or opponent_pokemon4=? or opponent_pokemon5=? or opponent_pokemon6=?)"
            cur.execute(sql, paramList)
            matchNum = cur.fetchone()
            sql = "select count(*) from battle where date >=? and date <=? and result = 1 and (opponent_pokemon1=? or opponent_pokemon2=? or opponent_pokemon3=? or opponent_pokemon4=? or opponent_pokemon5=? or opponent_pokemon6=?)"
            cur.execute(sql, paramList)
            winNum = cur.fetchone()
            if matchNum[0] == 0:
                winRateList.append(0)
            else:
                winRateList.append(winNum[0] / matchNum[0])
        return winRateList

    @staticmethod
    def get_win_rate_for_party_num(kpList, from_date, to_date, partyNum):
        cur = DB_battle.__db.cursor()
        winRateList = []
        for pokeName in kpList:
            paramList = (
                from_date,
                to_date,
                partyNum,
                pokeName[0],
                pokeName[0],
                pokeName[0],
                pokeName[0],
                pokeName[0],
                pokeName[0],
            )
            sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and (opponent_pokemon1=? or opponent_pokemon2=? or opponent_pokemon3=? or opponent_pokemon4=? or opponent_pokemon5=? or opponent_pokemon6=?)"
            cur.execute(sql, paramList)
            matchNum = cur.fetchone()
            sql = "select count(*) from battle where date >=? and date <=? and result = 1 and player_party_num=? and (opponent_pokemon1=? or opponent_pokemon2=? or opponent_pokemon3=? or opponent_pokemon4=? or opponent_pokemon5=? or opponent_pokemon6=?)"
            cur.execute(sql, paramList)
            winNum = cur.fetchone()
            if matchNum[0] == 0:
                winRateList.append(0)
            else:
                winRateList.append(winNum[0] / matchNum[0])
        return winRateList

    @staticmethod
    def get_win_rate_for_party_subnum(
        kpList, from_date, to_date, partyNum, partySubNum
    ):
        cur = DB_battle.__db.cursor()
        winRateList = []
        for pokeName in kpList:
            paramList = (
                from_date,
                to_date,
                partyNum,
                partySubNum,
                pokeName[0],
                pokeName[0],
                pokeName[0],
                pokeName[0],
                pokeName[0],
                pokeName[0],
            )
            sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and player_party_subnum=? and (opponent_pokemon1=? or opponent_pokemon2=? or opponent_pokemon3=? or opponent_pokemon4=? or opponent_pokemon5=? or opponent_pokemon6=?)"
            cur.execute(sql, paramList)
            matchNum = cur.fetchone()
            sql = "select count(*) from battle where date >=? and date <=? and result = 1 and player_party_num=? and player_party_subnum=? and (opponent_pokemon1=? or opponent_pokemon2=? or opponent_pokemon3=? or opponent_pokemon4=? or opponent_pokemon5=? or opponent_pokemon6=?)"
            cur.execute(sql, paramList)
            winNum = cur.fetchone()
            if matchNum[0] == 0:
                winRateList.append(0)
            else:
                winRateList.append(winNum[0] / matchNum[0])
        return winRateList

    @staticmethod
    def get_oppo_chosen_rate_for_party_num(kpList, from_date, to_date, partyNum):
        cur = DB_battle.__db.cursor()
        sensyutuRateList = []
        for pokeName in kpList:
            paramList = (
                from_date,
                to_date,
                partyNum,
                pokeName[0],
                pokeName[0],
                pokeName[0],
            )
            sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and (opponent_choice1=? or opponent_choice2=? or opponent_choice3=?)"
            cur.execute(sql, paramList)
            sensyutuCount = cur.fetchone()
            sensyutuRateList.append(sensyutuCount[0] / pokeName[1])
        return sensyutuRateList

    @staticmethod
    def get_oppo_chosen_rate_for_party_subnum(
        kpList, from_date, to_date, partyNum, partySubNum
    ):
        cur = DB_battle.__db.cursor()
        sensyutuRateList = []
        for pokeName in kpList:
            paramList = (
                from_date,
                to_date,
                partyNum,
                partySubNum,
                pokeName[0],
                pokeName[0],
                pokeName[0],
            )
            sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and player_party_subnum=? and (opponent_choice1=? or opponent_choice2=? or opponent_choice3=?)"
            cur.execute(sql, paramList)
            sensyutuCount = cur.fetchone()
            sensyutuRateList.append(sensyutuCount[0] / pokeName[1])
        return sensyutuRateList

    @staticmethod
    def get_oppo_first_chosen_rate_for_party_num(kpList, from_date, to_date, partyNum):
        cur = DB_battle.__db.cursor()
        sensyutuRateList = []
        for pokeName in kpList:
            paramList = (
                from_date,
                to_date,
                partyNum,
                pokeName[0],
            )
            sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and opponent_choice1=?"
            cur.execute(sql, paramList)
            sensyutuCount = cur.fetchone()
            sensyutuRateList.append(sensyutuCount[0] / pokeName[1])
        return sensyutuRateList

    @staticmethod
    def get_oppo_first_chosen_rate_for_party_subnum(
        kpList, from_date, to_date, partyNum, partySubNum
    ):
        cur = DB_battle.__db.cursor()
        sensyutuRateList = []
        for pokeName in kpList:
            paramList = (
                from_date,
                to_date,
                partyNum,
                partySubNum,
                pokeName[0],
            )
            sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and player_party_subnum=? and opponent_choice1=?"
            cur.execute(sql, paramList)
            sensyutuCount = cur.fetchone()
            sensyutuRateList.append(sensyutuCount[0] / pokeName[1])
        return sensyutuRateList

    @staticmethod
    def get_oppo_chosen_and_win_rate_for_party_num(
        kpList, from_date, to_date, partyNum
    ):
        cur = DB_battle.__db.cursor()
        winRateList = []
        for pokeName in kpList:
            paramList = (
                from_date,
                to_date,
                partyNum,
                pokeName[0],
                pokeName[0],
                pokeName[0],
            )
            sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and (opponent_choice1=? or opponent_choice2=? or opponent_choice3=?)"
            cur.execute(sql, paramList)
            matchNum = cur.fetchone()
            sql = "select count(*) from battle where date >=? and date <=? and result=1 and player_party_num=? and (opponent_choice1=? or opponent_choice2=? or opponent_choice3=?)"
            cur.execute(sql, paramList)
            winNum = cur.fetchone()
            if matchNum[0] == 0:
                winRateList.append(0)
            else:
                winRateList.append(winNum[0] / matchNum[0])
        return winRateList

    @staticmethod
    def get_oppo_chosen_and_win_rate_for_party_subnum(
        kpList, from_date, to_date, partyNum, partySubNum
    ):
        cur = DB_battle.__db.cursor()
        winRateList = []
        for pokeName in kpList:
            paramList = (
                from_date,
                to_date,
                partyNum,
                partySubNum,
                pokeName[0],
                pokeName[0],
                pokeName[0],
            )
            sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and player_party_subnum=? and (opponent_choice1=? or opponent_choice2=? or opponent_choice3=?)"
            cur.execute(sql, paramList)
            matchNum = cur.fetchone()
            sql = "select count(*) from battle where date >=? and date <=? and result=1 and player_party_num=? and player_party_subnum=? and (opponent_choice1=? or opponent_choice2=? or opponent_choice3=?)"
            cur.execute(sql, paramList)
            winNum = cur.fetchone()
            if matchNum[0] == 0:
                winRateList.append(0)
            else:
                winRateList.append(winNum[0] / matchNum[0])
        return winRateList

    @staticmethod
    def get_oppo_first_chosen_and_win_rate_for_party_num(
        kpList, from_date, to_date, partyNum
    ):
        cur = DB_battle.__db.cursor()
        winRateList = []
        for pokeName in kpList:
            paramList = (
                from_date,
                to_date,
                partyNum,
                pokeName[0],
            )
            sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and opponent_choice1=?"
            cur.execute(sql, paramList)
            matchNum = cur.fetchone()
            sql = "select count(*) from battle where date >=? and date <=? and result=1 and player_party_num=? and opponent_choice1=?"
            cur.execute(sql, paramList)
            winNum = cur.fetchone()
            if matchNum[0] == 0:
                winRateList.append(0)
            else:
                winRateList.append(winNum[0] / matchNum[0])
        return winRateList

    @staticmethod
    def get_oppo_first_chosen_and_win_rate_for_party_subnum(
        kpList, from_date, to_date, partyNum, partySubNum
    ):
        cur = DB_battle.__db.cursor()
        winRateList = []
        for pokeName in kpList:
            paramList = (
                from_date,
                to_date,
                partyNum,
                partySubNum,
                pokeName[0],
            )
            sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and player_party_subnum=? and opponent_choice1=?"
            cur.execute(sql, paramList)
            matchNum = cur.fetchone()
            sql = "select count(*) from battle where date >=? and date <=? and result=1 and player_party_num=? and player_party_subnum=? and opponent_choice1=?"
            cur.execute(sql, paramList)
            winNum = cur.fetchone()
            if matchNum[0] == 0:
                winRateList.append(0)
            else:
                winRateList.append(winNum[0] / matchNum[0])
        return winRateList

    @staticmethod
    def get_win_rate_per_pokemon_for_party_num(
        party_list, from_date, to_date, partyNum
    ):
        cur = DB_battle.__db.cursor()
        winRateList = []
        for pokeName in party_list:
            paramList = (
                from_date,
                to_date,
                partyNum,
                pokeName,
                pokeName,
                pokeName,
            )
            sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and (player_choice1=? or player_choice2=? or player_choice3=?)"
            cur.execute(sql, paramList)
            matchNum = cur.fetchone()
            sql = "select count(*) from battle where date >=? and date <=? and result=1 and player_party_num=? and (player_choice1=? or player_choice2=? or player_choice3=?)"
            cur.execute(sql, paramList)
            winNum = cur.fetchone()
            if matchNum[0] == 0:
                winRateList.append(0)
            else:
                winRateList.append(winNum[0] / matchNum[0])
        return winRateList

    @staticmethod
    def get_win_rate_per_pokemon_for_party_subnum(
        party_list, from_date, to_date, partyNum, partySubnum
    ):
        cur = DB_battle.__db.cursor()
        winRateList = []
        for pokeName in party_list:
            paramList = (
                from_date,
                to_date,
                partyNum,
                partySubnum,
                pokeName,
                pokeName,
                pokeName,
            )
            sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and player_party_subnum=? and (player_choice1=? or player_choice2=? or player_choice3=?)"
            cur.execute(sql, paramList)
            matchNum = cur.fetchone()
            sql = "select count(*) from battle where date >=? and date <=? and result=1 and player_party_num=? and player_party_subnum=? and (player_choice1=? or player_choice2=? or player_choice3=?)"
            cur.execute(sql, paramList)
            winNum = cur.fetchone()
            if matchNum[0] == 0:
                winRateList.append(0)
            else:
                winRateList.append(winNum[0] / matchNum[0])
        return winRateList

    @staticmethod
    def get_chosen_rate_for_party_num(party_list, from_date, to_date, partyNum):
        cur = DB_battle.__db.cursor()
        paramList = (from_date, to_date, partyNum)
        sql = "select count(*) from battle where date >=? and date <=? and player_party_num=?"
        cur.execute(sql, paramList)
        battleCount = cur.fetchone()
        sensyutuRateList = []
        for pokeName in party_list:
            paramList = (
                from_date,
                to_date,
                partyNum,
                pokeName,
                pokeName,
                pokeName,
            )
            sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and (player_choice1=? or player_choice2=? or player_choice3=?)"
            cur.execute(sql, paramList)
            sensyutuCount = cur.fetchone()
            if battleCount[0] == 0:
                return (0, 0, 0, 0, 0, 0)
            sensyutuRateList.append(sensyutuCount[0] / battleCount[0])
        return sensyutuRateList

    @staticmethod
    def get_chosen_rate_for_party_subnum(
        party_list, from_date, to_date, partyNum, partySubNum
    ):
        cur = DB_battle.__db.cursor()
        paramList = (from_date, to_date, partyNum, partySubNum)
        sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and player_party_subnum=?"
        cur.execute(sql, paramList)
        battleCount = cur.fetchone()
        sensyutuRateList = []
        for pokeName in party_list:
            paramList = (
                from_date,
                to_date,
                partyNum,
                partySubNum,
                pokeName,
                pokeName,
                pokeName,
            )
            sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and player_party_subnum=? and (player_choice1=? or player_choice2=? or player_choice3=?)"
            cur.execute(sql, paramList)
            sensyutuCount = cur.fetchone()
            if battleCount[0] == 0:
                return (0, 0, 0, 0, 0, 0)
            sensyutuRateList.append(sensyutuCount[0] / battleCount[0])
        return sensyutuRateList

    @staticmethod
    def get_chosen_and_win_rate_for_party_num(party_list, from_date, to_date, partyNum):
        cur = DB_battle.__db.cursor()
        winRateList = []
        for pokeName in party_list:
            paramList = (
                from_date,
                to_date,
                partyNum,
                pokeName,
                pokeName,
                pokeName,
            )
            sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and (player_choice1=? or player_choice2=? or player_choice3=?)"
            cur.execute(sql, paramList)
            matchNum = cur.fetchone()
            sql = "select count(*) from battle where date >=? and date <=? and result = 1 and player_party_num=? and (player_choice1=? or player_choice2=? or player_choice3=?)"
            cur.execute(sql, paramList)
            winNum = cur.fetchone()
            if matchNum[0] == 0:
                winRateList.append(0)
            else:
                winRateList.append(winNum[0] / matchNum[0])
        return winRateList

    @staticmethod
    def get_chosen_and_win_rate_for_party_subnum(
        party_list, from_date, to_date, partyNum, partySubNum
    ):
        cur = DB_battle.__db.cursor()
        winRateList = []
        for pokeName in party_list:
            paramList = (
                from_date,
                to_date,
                partyNum,
                partySubNum,
                pokeName,
                pokeName,
                pokeName,
            )
            sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and player_party_subnum=? and (player_choice1=? or player_choice2=? or player_choice3=?)"
            cur.execute(sql, paramList)
            matchNum = cur.fetchone()
            sql = "select count(*) from battle where date >=? and date <=? and result = 1 and player_party_num=? and player_party_subnum=? and (player_choice1=? or player_choice2=? or player_choice3=?)"
            cur.execute(sql, paramList)
            winNum = cur.fetchone()
            if matchNum[0] == 0:
                winRateList.append(0)
            else:
                winRateList.append(winNum[0] / matchNum[0])
        return winRateList

    @staticmethod
    def get_first_chosen_rate_for_party_num(party_list, from_date, to_date, partyNum):
        cur = DB_battle.__db.cursor()
        paramList = (from_date, to_date, partyNum)
        sql = "select count(*) from battle where date >=? and date <=? and player_party_num=?"
        cur.execute(sql, paramList)
        battleCount = cur.fetchone()
        sensyutuRateList = []
        for pokeName in party_list:
            paramList = (
                from_date,
                to_date,
                partyNum,
                pokeName,
            )
            sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and player_choice1=?"
            cur.execute(sql, paramList)
            sensyutuCount = cur.fetchone()
            if battleCount[0] == 0:
                return (0, 0, 0, 0, 0, 0)
            sensyutuRateList.append(sensyutuCount[0] / battleCount[0])
        return sensyutuRateList

    @staticmethod
    def get_first_chosen_rate_for_party_subnum(
        party_list, from_date, to_date, partyNum, partySubNum
    ):
        cur = DB_battle.__db.cursor()
        paramList = (from_date, to_date, partyNum, partySubNum)
        sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and player_party_subnum=?"
        cur.execute(sql, paramList)
        battleCount = cur.fetchone()
        sensyutuRateList = []
        for pokeName in party_list:
            paramList = (
                from_date,
                to_date,
                partyNum,
                partySubNum,
                pokeName,
            )
            sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and player_party_subnum=? and player_choice1=?"
            cur.execute(sql, paramList)
            sensyutuCount = cur.fetchone()
            if battleCount[0] == 0:
                return (0, 0, 0, 0, 0, 0)
            sensyutuRateList.append(sensyutuCount[0] / battleCount[0])
        return sensyutuRateList

    @staticmethod
    def get_first_chosen_and_win_rate_for_party_num(
        party_list, from_date, to_date, partyNum
    ):
        cur = DB_battle.__db.cursor()
        winRateList = []
        for pokeName in party_list:
            paramList = (
                from_date,
                to_date,
                partyNum,
                pokeName,
            )
            sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and player_choice1=?"
            cur.execute(sql, paramList)
            matchNum = cur.fetchone()
            sql = "select count(*) from battle where date >=? and date <=? and result = 1 and player_party_num=? and player_choice1=?"
            cur.execute(sql, paramList)
            winNum = cur.fetchone()
            if matchNum[0] == 0:
                winRateList.append(0)
            else:
                winRateList.append(winNum[0] / matchNum[0])
        return winRateList

    @staticmethod
    def get_first_chosen_and_win_rate_for_party_subnum(
        party_list, from_date, to_date, partyNum, partySubNum
    ):
        cur = DB_battle.__db.cursor()
        winRateList = []
        for pokeName in party_list:
            paramList = (
                from_date,
                to_date,
                partyNum,
                partySubNum,
                pokeName,
            )
            sql = "select count(*) from battle where date >=? and date <=? and player_party_num=? and player_party_subnum=? and player_choice1=?"
            cur.execute(sql, paramList)
            matchNum = cur.fetchone()
            sql = "select count(*) from battle where date >=? and date <=? and result = 1 and player_party_num=? and player_party_subnum=? and player_choice1=?"
            cur.execute(sql, paramList)
            winNum = cur.fetchone()
            if matchNum[0] == 0:
                winRateList.append(0)
            else:
                winRateList.append(winNum[0] / matchNum[0])
        return winRateList

    @staticmethod
    def chenge_date_from_datetime_to_unix(
        fromYear: int,
        fromMonth: int,
        fromDate: int,
        toYear: int,
        toMonth: int,
        toDate: int,
        time9Bl: bool,
    ):
        if time9Bl:
            from_date = int(
                datetime.datetime(fromYear, fromMonth, fromDate, 9, 0, 0).timestamp()
            )
        else:
            from_date = int(
                datetime.datetime(fromYear, fromMonth, fromDate).timestamp()
            )
        to_date = int(
            datetime.datetime(toYear, toMonth, toDate, 23, 59, 59).timestamp()
        )
        return from_date, to_date

    @staticmethod
    def __select(sql: str) -> list:
        result = []
        cur = DB_battle.__db.cursor()
        cur.execute(sql)
        for row in cur:
            result.append(row)
        return result
