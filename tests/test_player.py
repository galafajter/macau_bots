"""Testy klasy bazowej Player (oraz pomocniczych Dummy z tests.helpers)."""

from core.card import Suit, Value
from tests.helpers import DummyPlayer, card


def test_draw_card_adds_to_hand():
    player = DummyPlayer("test")
    nine = card(Suit.HEART, Value.NINE)

    player.draw_card(nine)

    assert len(player.hand) == 1
    assert nine in player.hand


def test_make_move_returns_none_when_no_playable_cards():
    player = DummyPlayer("test")
    player.hand = [card(Suit.HEART, Value.NINE)]

    player.evaluate_hand_for_playable_cards([])  # nic nielegalnego

    assert player.make_move() is None


def test_make_move_returns_and_removes_played_card():
    player = DummyPlayer("test")
    card1 = card(Suit.HEART, Value.NINE)
    card2 = card(Suit.HEART, Value.EIGHT)

    player.draw_card(card1)
    player.draw_card(card2)
    player.evaluate_hand_for_playable_cards([card1, card2])  # cała ręka legalna

    player_move = player.make_move()

    assert player_move == card1  # DummyPlayer gra pierwszą legalną
    assert player_move not in player.hand
    assert card2 in player.hand


def test_play_card_rejects_card_not_in_hand():
    player = DummyPlayer("test")

    assert player.play_card(card(Suit.CLUBS, Value.ACE)) is None
    assert player.hand == []
