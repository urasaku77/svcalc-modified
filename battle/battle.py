import dataclasses
import datetime
from typing import Optional

from component.frame.common import ChosenFrame, PartyFrame
from component.frame.whole import RecordFrame


@dataclasses.dataclass
class Battle:
    id: Optional[int]
    date: Optional[str]
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
            str(datetime.datetime.now()),
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
