import dataclasses
import datetime
from typing import Optional

@dataclasses.dataclass
class Battle:
    id: Optional[int]
    date: Optional[str]
    result: Optional[int]
    evaluation: Optional[int]
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
    player_choice1_waza1: Optional[str]
    player_choice1_waza2: Optional[str]
    player_choice1_waza3: Optional[str]
    player_choice1_waza4: Optional[str]
    player_choice1_waza1_check: Optional[int]
    player_choice1_waza2_check: Optional[int]
    player_choice1_waza3_check: Optional[int]
    player_choice1_waza4_check: Optional[int]
    player_choice2: Optional[str]
    player_choice2_waza1: Optional[str]
    player_choice2_waza2: Optional[str]
    player_choice2_waza3: Optional[str]
    player_choice2_waza4: Optional[str]
    player_choice2_waza1_check: Optional[int]
    player_choice2_waza2_check: Optional[int]
    player_choice2_waza3_check: Optional[int]
    player_choice2_waza4_check: Optional[int]
    player_choice3: Optional[str]
    player_choice3_waza1: Optional[str]
    player_choice3_waza2: Optional[str]
    player_choice3_waza3: Optional[str]
    player_choice3_waza4: Optional[str]
    player_choice3_waza1_check: Optional[int]
    player_choice3_waza2_check: Optional[int]
    player_choice3_waza3_check: Optional[int]
    player_choice3_waza4_check: Optional[int]
    opponent_choice1: Optional[str]
    opponent_choice2: Optional[str]
    opponent_choice3: Optional[str]

    def set_battle(name, rank, battle_memo, party, playerChosenPokemonPanels, opponentChosenPokemonPanels, result, evaluation, favorite):
        from pokedata.loader import get_party_csv
        file = get_party_csv().split('party\\csv\\')[1]

        return Battle(
            None,
            str(datetime.datetime.now()),
            result,
            evaluation,
            favorite,
            name,
            rank,
            battle_memo,
            file.split("-")[0],
            file.split("-")[1].split("_")[0],
            party[0][0].no if party[0][0] is not None else "",
            party[0][1].no if party[0][1] is not None else "",
            party[0][2].no if party[0][2] is not None else "",
            party[0][3].no if party[0][3] is not None else "",
            party[0][4].no if party[0][4] is not None else "",
            party[0][5].no if party[0][5] is not None else "",
            party[1][0].no if party[1][0] is not None else "",
            party[1][1].no if party[1][1] is not None else "",
            party[1][2].no if party[1][2] is not None else "",
            party[1][3].no if party[1][3] is not None else "",
            party[1][4].no if party[1][4] is not None else "",
            party[1][5].no if party[1][5] is not None else "",
            playerChosenPokemonPanels.no[0],
            playerChosenPokemonPanels.waza_list[0][0] if playerChosenPokemonPanels.name[0] != "" else "",
            playerChosenPokemonPanels.waza_list[0][1] if playerChosenPokemonPanels.name[0] != "" else "",
            playerChosenPokemonPanels.waza_list[0][2] if playerChosenPokemonPanels.name[0] != "" else "",
            playerChosenPokemonPanels.waza_list[0][3] if playerChosenPokemonPanels.name[0] != "" else "",
            playerChosenPokemonPanels.waza_check_list[0][0] if playerChosenPokemonPanels.name[0] != "" else "",
            playerChosenPokemonPanels.waza_check_list[0][1] if playerChosenPokemonPanels.name[0] != "" else "",
            playerChosenPokemonPanels.waza_check_list[0][2] if playerChosenPokemonPanels.name[0] != "" else "",
            playerChosenPokemonPanels.waza_check_list[0][3] if playerChosenPokemonPanels.name[0] != "" else "",
            playerChosenPokemonPanels.no[1],
            playerChosenPokemonPanels.waza_list[1][0] if playerChosenPokemonPanels.name[1] != "" else "",
            playerChosenPokemonPanels.waza_list[1][1] if playerChosenPokemonPanels.name[1] != "" else "",
            playerChosenPokemonPanels.waza_list[1][2] if playerChosenPokemonPanels.name[1] != "" else "",
            playerChosenPokemonPanels.waza_list[1][3] if playerChosenPokemonPanels.name[1] != "" else "",
            playerChosenPokemonPanels.waza_check_list[1][0] if playerChosenPokemonPanels.name[1] != "" else "",
            playerChosenPokemonPanels.waza_check_list[1][1] if playerChosenPokemonPanels.name[1] != "" else "",
            playerChosenPokemonPanels.waza_check_list[1][2] if playerChosenPokemonPanels.name[1] != "" else "",
            playerChosenPokemonPanels.waza_check_list[1][3] if playerChosenPokemonPanels.name[1] != "" else "",
            playerChosenPokemonPanels.no[2],
            playerChosenPokemonPanels.waza_list[2][0] if playerChosenPokemonPanels.name[2] != "" else "",
            playerChosenPokemonPanels.waza_list[2][1] if playerChosenPokemonPanels.name[2] != "" else "",
            playerChosenPokemonPanels.waza_list[2][2] if playerChosenPokemonPanels.name[2] != "" else "",
            playerChosenPokemonPanels.waza_list[2][3] if playerChosenPokemonPanels.name[2] != "" else "",
            playerChosenPokemonPanels.waza_check_list[2][0] if playerChosenPokemonPanels.name[2] != "" else "",
            playerChosenPokemonPanels.waza_check_list[2][1] if playerChosenPokemonPanels.name[2] != "" else "",
            playerChosenPokemonPanels.waza_check_list[2][2] if playerChosenPokemonPanels.name[2] != "" else "",
            playerChosenPokemonPanels.waza_check_list[2][3] if playerChosenPokemonPanels.name[2] != "" else "",
            opponentChosenPokemonPanels.no[0],
            opponentChosenPokemonPanels.no[1],
            opponentChosenPokemonPanels.no[2],
        )