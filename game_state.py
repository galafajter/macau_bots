from card import Card, Deck, Effect, Suit, Value
from player import Player
from typing import List
from dataclasses import dataclass


@dataclass
class GameState:
    

    deck: Deck
    players: List[Player]
    current_player_index: int

    playable_cards: List[Card]

    active_effect: Effect | None = None

    demanded_suit: Suit | None = None
    demanded_value: Value | None = None

    cards_to_draw: int = 0
    turns_to_skip: int = 0
