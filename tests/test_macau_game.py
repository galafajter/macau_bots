"""Terminacja partii: każda partia kończy się zwycięzcą albo patem.

Historycznie ~5% seedy 5-osobowych padało w pat (odziedziczony po main
silnik: pusta talia doboru + stos 1 karta); do tej pory była to pętla
w nieskończoność / guard "error" bez zapisu do bazy. Pat-guard kończy
taką grę wynikiem "stalemate" z pełnym logiem.
"""

import random

import pytest

from core.macau_game import MacauGame
from core.player import RandomPlayer
from tests.helpers import NullLogger

PLAYER_NAMES = {"A", "B", "C"}
TERMINAL_RESULTS = PLAYER_NAMES | {"stalemate"}


@pytest.mark.parametrize("seed", range(1000))
def test_game_terminates_with_winner_or_stalemate(seed):
    random.seed(seed)
    players = [RandomPlayer("A"), RandomPlayer("B"), RandomPlayer("C")]
    game = MacauGame(players=players, number_of_cards_per_player=5)

    result = game.play(NullLogger())

    assert result in TERMINAL_RESULTS
