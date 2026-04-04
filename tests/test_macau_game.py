from makao_game import MacauGame
import random
import pytest


@pytest.mark.parametrize("seed", range(1000))
def test_game_always_ends(seed):
    random.seed(seed)
    game = MacauGame(players_num=3)
    res = game.play()
    assert res != "error"
    assert res is not None