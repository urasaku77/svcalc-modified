import sqlite3
from dataclasses import dataclass

from pokedata.const import Types
from pokedata.exception import remove_pokemon_name_from_party


@dataclass
class TypeEffective:
    at_type: Types
    df_type: Types
    value: float


class DB:
    __db = sqlite3.connect("data/pokemon.db", check_same_thread=False)
    __db.row_factory = sqlite3.Row
    __type_effectives: list[TypeEffective] = []
    __pokemon_namelist: list[str] = []
    __waza_namedict: dict[str, str] = {}

    @staticmethod
    def get_pokemon_data_by_name(name: str):
        sql = "SELECT * FROM pokemon_data where name = '{0}'".format(name)
        result = DB.__select(sql)
        return result[0]

    @staticmethod
    def get_pokemons_name_by_no(no: str):
        sql = "SELECT name FROM pokemon_data where no = '{0}'".format(no)
        result = DB.__select(sql)

        names = []
        for row in result:
            names.append(row["name"])
        return names

    @staticmethod
    def get_pokemon_data_by_pid(pid: str):
        no = pid.split("-")[0]
        form = pid.split("-")[1]
        sql = "SELECT * FROM pokemon_data where no = {0} and form = {1}".format(
            no, form
        )
        result = DB.__select(sql)
        return result[0]

    @staticmethod
    def get_pokemon_names_by_pid(pid: list[str]):
        pids = (
            f"('{pid[0]}', '{pid[1]}', '{pid[2]}', '{pid[3]}', '{pid[4]}', '{pid[5]}')"
        )
        sql = (
            "SELECT no || '-' || form pid, name FROM pokemon_data where pid in " + pids
        )
        result = DB.__select(sql)

        names = []
        for p in pid:
            for row in result:
                if row["pid"] == p:
                    names.append(row["name"])
        return names

    @staticmethod
    def get_pokemon_pid_by_name(name: str) -> str:
        sql = (
            "SELECT no || '-' || form pid FROM pokemon_data where name = '{0}'".format(
                name
            )
        )
        result = DB.__select(sql)
        return result[0]["pid"]

    @staticmethod
    def get_pokemon_namelist(form: bool = False) -> list[str]:
        if len(DB.__pokemon_namelist) == 0:
            sql = "SELECT name FROM pokemon_data"
            for row in DB.__select(sql):
                DB.__pokemon_namelist.append(row["name"])
            if form:
                for pokemon in remove_pokemon_name_from_party:
                    DB.__pokemon_namelist.remove(pokemon)
        return DB.__pokemon_namelist

    @staticmethod
    def get_waza_data_by_name(name: str):
        sql = "SELECT * FROM waza_data where name = '{0}'".format(name)
        result = DB.__select(sql)
        return result[0]

    @staticmethod
    def get_waza_namedict() -> dict[str, str]:
        if len(DB.__waza_namedict) == 0:
            DB.__create_waza_namedict()
        return DB.__waza_namedict

    @staticmethod
    def __create_waza_namedict():
        import jaconv

        if len(DB.__waza_namedict) == 0:
            sql = "SELECT name FROM waza_data"
            for row in DB.__select(sql):
                DB.__waza_namedict[jaconv.hira2kata(row["name"])] = row["name"]

    @staticmethod
    def get_type_effective(
        attack_type: Types, target_type: list[Types]
    ) -> list[TypeEffective]:
        if len(DB.__type_effectives) == 0:
            for row in DB.__select("SELECT * FROM type_effective"):
                DB.__type_effectives.append(
                    TypeEffective(
                        at_type=Types[row["at_type"]],
                        df_type=Types[row["df_type"]],
                        value=row["value"],
                    )
                )
        return list(
            filter(
                lambda x: x.at_type == attack_type and x.df_type in target_type,
                DB.__type_effectives,
            )
        )

    @staticmethod
    def __select(sql: str) -> list:
        result = []
        cur = DB.__db.cursor()
        cur.execute(sql)
        for row in cur:
            result.append(row)
        cur.close()

        return result
