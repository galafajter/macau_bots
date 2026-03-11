from card import Card, Deck, Effect, Suit, Value
from player import Player
from typing import List
from dataclasses import dataclass


@dataclass
class GameState:

    deck: Deck
    players: List[Player]
    current_player_index: int

    active_effect: Effect | None = None

    demanded_suit: Suit | None = None
    demanded_value: Value | None = None

    cards_to_draw: int = 0
    turns_being_blocked: int = 0

    turn_direction: int = 1

    def reset_active_effect(self):
        self.cards_to_draw = 0
        self.turns_being_blocked = 0
        self.demanded_suit = None
        self.demanded_value = None


