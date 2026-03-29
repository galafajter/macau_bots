from makao_game import MacauGame
import random

def test_game_always_ends():
    for seed in range(100):
        random.seed(seed)
        game = MacauGame(players_num=3)
        res = game.play()
        assert res != "error"
        assert res is not None