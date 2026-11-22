"""Status quo terminatora partii (pat silnika -- decyzja w trakcie Etapu 1).

Gra kończy się w skończonym czasie dzięki guardowi 1000 ruchów; ~5% seedy
trafia w pre-istniejący pat (pusta talia doboru + stos 1 karta, wtedy
Deck.draw_from_deck zwraca False i tury przelatują) => wynik "error".

Po scaleniu naprawy patu (feat/stalemate-guard) asercja zostanie
wzmocniona: oczekiwany wynik {imię gracza, "stalemate"} zamiast "error".
"""

import random

import pytest

from core.makao_game import MacauGame
from core.player import RandomPlayer
from tests.helpers import NullLogger

PLAYER_NAMES = {"A", "B", "C"}
BOUNDED_RESULTS = PLAYER_NAMES | {"error"}


@pytest.mark.parametrize("seed", range(1000))
def test_game_terminates_with_bounded_result(seed):
    random.seed(seed)
    players = [RandomPlayer("A"), RandomPlayer("B"), RandomPlayer("C")]
    game = MacauGame(players=players, number_of_cards_per_player=5)

    result = game.play(NullLogger())

    assert result is not None
    assert result in BOUNDED_RESULTS
