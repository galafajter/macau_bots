import pytest

from core.card import Suit, Value
from core.game_state import GameState
from tests.helpers import DummyPlayer, card, make_deck


@pytest.fixture
def basic_state():
    """Stan 3 graczy przy stole 8-kier, talia doboru PUSTA (pełna determinizm).

    Testy, które potrzebują kart do dobrania, nadpisują desk.drawing_cards.
    """
    players = [DummyPlayer("test1"), DummyPlayer("test2"), DummyPlayer("test3")]
    deck = make_deck([card(Suit.HEART, Value.EIGHT)])
    return GameState(deck=deck, players=players, current_player_index=0)
