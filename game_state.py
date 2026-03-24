from card import Card, Deck, Effect, Suit, Value
from player import Player
from typing import List
from dataclasses import dataclass, field


@dataclass
class GameState:

    deck: Deck
    players: List[Player]
    current_player_index: int

    demanded_suit: Suit = None
    demanded_value: Value = None
    demand_turns_left: int = 0

    cards_to_draw: int = 0

    blocked_turns_per_player: dict[int, int] = field(default_factory=dict)
    block_count: int = 0

    effect_active: bool = False
    execute_effect: bool = False

    turn_direction: int = 1

    skip_turn: bool = False

    def reset_active_effect(self):
        self.cards_to_draw = 0
        self.block_count = 0
        self.demanded_suit = None
        self.demanded_value = None

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]

