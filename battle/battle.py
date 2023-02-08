import dataclasses
import datetime
from typing import Optional

@dataclasses.dataclass
class Battle:
    id: Optional[int]
    date: Optional[str]
    time: Optional[int]
    result: Optional[int]
    player_tn: Optional[str]
    opponent_tn: Optional[str]
    player_rank: Optional[int]
    opponent_rank: Optional[int]
    player_memo: Optional[str]
    opponent_memo: Optional[str]
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
    player_choice1_character: Optional[str]
    player_choice1_item: Optional[str]
    player_choice1_ability: Optional[str]
    player_choice1_tesasu: Optional[str]
    player_choice1_waza1: Optional[str]
    player_choice1_waza2: Optional[str]
    player_choice1_waza3: Optional[str]
    player_choice1_waza4: Optional[str]
    player_choice2: Optional[str]
    player_choice2_character: Optional[str]
    player_choice2_item: Optional[str]
    player_choice2_ability: Optional[str]
    player_choice2_tesasu: Optional[str]
    player_choice2_waza1: Optional[str]
    player_choice2_waza2: Optional[str]
    player_choice2_waza3: Optional[str]
    player_choice2_waza4: Optional[str]
    player_choice3: Optional[str]
    player_choice3_character: Optional[str]
    player_choice3_item: Optional[str]
    player_choice3_ability: Optional[str]
    player_choice3_tesasu: Optional[str]
    player_choice3_waza1: Optional[str]
    player_choice3_waza2: Optional[str]
    player_choice3_waza3: Optional[str]
    player_choice3_waza4: Optional[str]
    opponent_choice1: Optional[str]
    opponent_choice1_character: Optional[str]
    opponent_choice1_item: Optional[str]
    opponent_choice1_ability: Optional[str]
    opponent_choice1_tesasu: Optional[str]
    opponent_choice1_waza1: Optional[str]
    opponent_choice1_waza2: Optional[str]
    opponent_choice1_waza3: Optional[str]
    opponent_choice1_waza4: Optional[str]
    opponent_choice2: Optional[str]
    opponent_choice2_character: Optional[str]
    opponent_choice2_item: Optional[str]
    opponent_choice2_ability: Optional[str]
    opponent_choice2_tesasu: Optional[str]
    opponent_choice2_waza1: Optional[str]
    opponent_choice2_waza2: Optional[str]
    opponent_choice2_waza3: Optional[str]
    opponent_choice2_waza4: Optional[str]
    opponent_choice3: Optional[str]
    opponent_choice3_character: Optional[str]
    opponent_choice3_item: Optional[str]
    opponent_choice3_ability: Optional[str]
    opponent_choice3_tesasu: Optional[str]
    opponent_choice3_waza1: Optional[str]
    opponent_choice3_waza2: Optional[str]
    opponent_choice3_waza3: Optional[str]
    opponent_choice3_waza4: Optional[str]

    def set_battle(trainerInfoPanels, party, playerChosenPokemonPanels, opponentChosenPokemonPanels, time, result):
        return Battle(
            None, 
            str(datetime.datetime.now()), 
            time, 
            result,
            trainerInfoPanels[0].name, 
            trainerInfoPanels[1].name, 
            trainerInfoPanels[0].rank, 
            trainerInfoPanels[1].rank, 
            trainerInfoPanels[0].memo, 
            trainerInfoPanels[1].memo, 
            party[0][0].name if party[0][0] is not None else "", 
            party[0][1].name if party[0][1] is not None else "", 
            party[0][2].name if party[0][2] is not None else "", 
            party[0][3].name if party[0][3] is not None else "", 
            party[0][4].name if party[0][4] is not None else "", 
            party[0][5].name if party[0][5] is not None else "", 
            party[1][0].name if party[1][0] is not None else "", 
            party[1][1].name if party[1][1] is not None else "", 
            party[1][2].name if party[1][2] is not None else "", 
            party[1][3].name if party[1][3] is not None else "", 
            party[1][4].name if party[1][4] is not None else "", 
            party[1][5].name if party[1][5] is not None else "", 
            playerChosenPokemonPanels.name[0], 
            playerChosenPokemonPanels.doryoku[0], 
            playerChosenPokemonPanels.item[0], 
            playerChosenPokemonPanels.ability[0], 
            playerChosenPokemonPanels.terastype[0].name, 
            playerChosenPokemonPanels.waza_list[0][0] if playerChosenPokemonPanels.name[0] != "" else "", 
            playerChosenPokemonPanels.waza_list[0][1] if playerChosenPokemonPanels.name[0] != "" else "", 
            playerChosenPokemonPanels.waza_list[0][2] if playerChosenPokemonPanels.name[0] != "" else "", 
            playerChosenPokemonPanels.waza_list[0][3] if playerChosenPokemonPanels.name[0] != "" else "", 
            playerChosenPokemonPanels.name[1], 
            playerChosenPokemonPanels.doryoku[1], 
            playerChosenPokemonPanels.item[1], 
            playerChosenPokemonPanels.ability[1], 
            playerChosenPokemonPanels.terastype[1].name, 
            playerChosenPokemonPanels.waza_list[1][0] if playerChosenPokemonPanels.name[1] != "" else "", 
            playerChosenPokemonPanels.waza_list[1][1] if playerChosenPokemonPanels.name[1] != "" else "", 
            playerChosenPokemonPanels.waza_list[1][2] if playerChosenPokemonPanels.name[1] != "" else "", 
            playerChosenPokemonPanels.waza_list[1][3] if playerChosenPokemonPanels.name[1] != "" else "", 
            playerChosenPokemonPanels.name[2], 
            playerChosenPokemonPanels.doryoku[2], 
            playerChosenPokemonPanels.item[2], 
            playerChosenPokemonPanels.ability[2], 
            playerChosenPokemonPanels.terastype[2].name, 
            playerChosenPokemonPanels.waza_list[2][0] if playerChosenPokemonPanels.name[2] != "" else "", 
            playerChosenPokemonPanels.waza_list[2][1] if playerChosenPokemonPanels.name[2] != "" else "", 
            playerChosenPokemonPanels.waza_list[2][2] if playerChosenPokemonPanels.name[2] != "" else "", 
            playerChosenPokemonPanels.waza_list[2][3] if playerChosenPokemonPanels.name[2] != "" else "", 
            opponentChosenPokemonPanels[0].name, 
            opponentChosenPokemonPanels[0].doryoku, 
            opponentChosenPokemonPanels[0].item, 
            opponentChosenPokemonPanels[0].ability, 
            opponentChosenPokemonPanels[0].terastype.name, 
            opponentChosenPokemonPanels[0].chosenWazaListPanel.wazapanel_list[0].waza if opponentChosenPokemonPanels[0].name != "" else "", 
            opponentChosenPokemonPanels[0].chosenWazaListPanel.wazapanel_list[1].waza if opponentChosenPokemonPanels[0].name != "" else "", 
            opponentChosenPokemonPanels[0].chosenWazaListPanel.wazapanel_list[2].waza if opponentChosenPokemonPanels[0].name != "" else "", 
            opponentChosenPokemonPanels[0].chosenWazaListPanel.wazapanel_list[3].waza if opponentChosenPokemonPanels[0].name != "" else "", 
            opponentChosenPokemonPanels[1].name, 
            opponentChosenPokemonPanels[1].doryoku, 
            opponentChosenPokemonPanels[1].item, 
            opponentChosenPokemonPanels[1].ability, 
            opponentChosenPokemonPanels[1].terastype.name, 
            opponentChosenPokemonPanels[1].chosenWazaListPanel.wazapanel_list[0].waza if opponentChosenPokemonPanels[1].name != "" else "", 
            opponentChosenPokemonPanels[1].chosenWazaListPanel.wazapanel_list[1].waza if opponentChosenPokemonPanels[1].name != "" else "", 
            opponentChosenPokemonPanels[1].chosenWazaListPanel.wazapanel_list[2].waza if opponentChosenPokemonPanels[1].name != "" else "", 
            opponentChosenPokemonPanels[1].chosenWazaListPanel.wazapanel_list[3].waza if opponentChosenPokemonPanels[1].name != "" else "", 
            opponentChosenPokemonPanels[2].name, 
            opponentChosenPokemonPanels[2].doryoku, 
            opponentChosenPokemonPanels[2].item, 
            opponentChosenPokemonPanels[2].ability, 
            opponentChosenPokemonPanels[2].terastype.name, 
            opponentChosenPokemonPanels[2].chosenWazaListPanel.wazapanel_list[0].waza if opponentChosenPokemonPanels[2].name != "" else "", 
            opponentChosenPokemonPanels[2].chosenWazaListPanel.wazapanel_list[1].waza if opponentChosenPokemonPanels[2].name != "" else "", 
            opponentChosenPokemonPanels[2].chosenWazaListPanel.wazapanel_list[2].waza if opponentChosenPokemonPanels[2].name != "" else "", 
            opponentChosenPokemonPanels[2].chosenWazaListPanel.wazapanel_list[3].waza if opponentChosenPokemonPanels[2].name != "" else ""
        )