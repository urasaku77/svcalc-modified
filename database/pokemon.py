import sqlite3
from dataclasses import dataclass

from pokedata.const import Types
from pokedata.exception import remove_pokemon_name_from_party


@dataclass
class TypeEffective:
    at_type: Types
    df_type: Types
    value: float


class DB_pokemon:
    __db = sqlite3.connect("database/pokemon.db", check_same_thread=False)
    __db.row_factory = sqlite3.Row
    __type_effectives: list[TypeEffective] = []
    __pokemon_namelist: list[str] = []
    __waza_namedict: dict[str, str] = {}

    @staticmethod
    def get_pokemon_data_by_name(name: str):
        sql = "SELECT * FROM pokemon_data where name = '{0}'".format(name)
        result = DB_pokemon.__select(sql)
        return result[0]

    @staticmethod
    def get_pokemons_name_by_no(no: str):
        sql = "SELECT name FROM pokemon_data where no = '{0}'".format(no)
        result = DB_pokemon.__select(sql)

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
        result = DB_pokemon.__select(sql)
        return result[0]

    @staticmethod
    def get_pokemon_name_by_pid(pid: str):
        no = pid.split("-")[0]
        form = pid.split("-")[1]
        sql = "SELECT name FROM pokemon_data where no = {0} and form = {1}".format(
            no, form
        )
        result = DB_pokemon.__select(sql)
        return result[0]["name"]

    @staticmethod
    def get_pokemon_pid_by_name(name: str) -> str:
        sql = (
            "SELECT no || '-' || form pid FROM pokemon_data where name = '{0}'".format(
                name
            )
        )
        result = DB_pokemon.__select(sql)
        return result[0]["pid"]

    @staticmethod
    def get_pokemon_namelist(form: bool = False) -> list[str]:
        if len(DB_pokemon.__pokemon_namelist) == 0:
            sql = "SELECT name FROM pokemon_data"
            for row in DB_pokemon.__select(sql):
                DB_pokemon.__pokemon_namelist.append(row["name"])
            if form:
                for pokemon in remove_pokemon_name_from_party:
                    DB_pokemon.__pokemon_namelist.remove(pokemon)
        return DB_pokemon.__pokemon_namelist

    @staticmethod
    def get_waza_data_by_name(name: str):
        sql = "SELECT * FROM waza_data where name = '{0}'".format(name)
        result = DB_pokemon.__select(sql)
        return result[0]

    @staticmethod
    def get_waza_namedict() -> dict[str, str]:
        if len(DB_pokemon.__waza_namedict) == 0:
            DB_pokemon.__create_waza_namedict()
        return DB_pokemon.__waza_namedict

    @staticmethod
    def __create_waza_namedict():
        import jaconv

        if len(DB_pokemon.__waza_namedict) == 0:
            sql = "SELECT name FROM waza_data"
            for row in DB_pokemon.__select(sql):
                DB_pokemon.__waza_namedict[jaconv.hira2kata(row["name"])] = row["name"]

    @staticmethod
    def get_type_effective(
        attack_type: Types, target_type: list[Types]
    ) -> list[TypeEffective]:
        if len(DB_pokemon.__type_effectives) == 0:
            for row in DB_pokemon.__select("SELECT * FROM type_effective"):
                DB_pokemon.__type_effectives.append(
                    TypeEffective(
                        at_type=Types[row["at_type"]],
                        df_type=Types[row["df_type"]],
                        value=row["value"],
                    )
                )
        return list(
            filter(
                lambda x: x.at_type == attack_type and x.df_type in target_type,
                DB_pokemon.__type_effectives,
            )
        )

    @staticmethod
    def __select(sql: str) -> list:
        result = []
        cur = DB_pokemon.__db.cursor()
        cur.execute(sql)
        for row in cur:
            result.append(row)
        cur.close()

        return result
