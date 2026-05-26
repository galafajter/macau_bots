from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import json

@dataclass
class Game:
    num_players: int
    initial_cards_num: int
    total_moves: Optional[int] = 0
    winner: Optional[int] = None  # FK do players.id (może być None na początku gry)
    created_at: datetime = datetime.now()
    id: Optional[int] = None

@dataclass
class Strategy:
    name: str
    params: dict  # W bazie zapiszemy jako tekst (JSON), w Pythonie wygodniej jako słownik
    id: Optional[int] = None

    def get_params_json(self) -> str:
        return json.dumps(self.params)

@dataclass
class Player:
    strategy_id: int
    game_id: int
    position: int
    id: Optional[int] = None

@dataclass
class Card:
    suit: str  # np. 'Hearts', 'Spades'
    rank: str  # np. 'A', '10', 'K'
    id: Optional[int] = None

@dataclass
class GameCard:
    game_id: int
    card_id: int
    location: str  # np. 'deck', 'hand', 'stack'
    player_id: Optional[int] = None  # Może być NULL, jeśli karta leży w talii
    move_num: Optional[int] = None   # Kiedy karta trafiła w to miejsce

@dataclass
class Move:
    game_id: int
    player_id: int
    move_num: int
    action: Optional[str] = None  # np. 'play', 'draw', 'pass'
    hand_before: Optional[str] = None
    hand_after: Optional[str] = None
    top_card_before: Optional[int] = None  # FK do cards.id
    top_card_after: Optional[int] = None   # FK do cards.id
    id: Optional[int] = None