import pytest
from player import Player
from card import Card, Suit, Value

def test_draw_card_adds_to_hand():
    player = Player("test")
    card = Card(Suit.HEART, Value.NINE, effect=None)

    player.draw_card(card)

    assert len(player.hand) == 1
    assert card in player.hand


def test_make_move_returns_none():
    player = Player("test")

    player.hand = [Card(Suit.HEART, Value.NINE, effect=None)]

    player.evaluate_hand_for_playable_cards([])

    player_move = player.make_move()

    assert player_move is None


def test_make_move_returns_card():
    player = Player("test")
    card1 = Card(Suit.HEART, Value.NINE, effect=None)
    card2 = Card(Suit.HEART, Value.EIGHT, effect=None)
    card3 = Card(Suit.HEART, Value.TEN, effect=None)
    card4 = Card(Suit.HEART, Value.JACK, effect=None)


    player.draw_card(card1)
    player.draw_card(card2)

    playable_cards = [card1, card2, card3, card4]
    player.evaluate_hand_for_playable_cards(playable_cards)

    player_move = player.make_move()


    assert isinstance(player_move, Card)
    assert player_move in [card1, card2]
    assert player_move not in player.hand

