import pytest
from game_master import GameMaster
from game_state import GameState
from player import Player
from card import Suit, Value, Card, Deck


@pytest.fixture
def basic_state():
    player1 = Player("test1")
    player2 = Player("test2")
    player3 = Player("test3")

    deck = Deck()

    card = Card(Suit.HEART, Value.EIGHT, effect=None)

    deck.put_on_stack(card)

    state = GameState(deck=deck,
                      players=[player1, player2, player3],
                      current_player_index=0
                      )

    return state


def test_war_effect(basic_state):

    card1 = Card(Suit.HEART, Value.THREE, effect=None)
    card2 = Card(Suit.HEART, Value.TWO, effect=None)
    card3 = Card(Suit.HEART, Value.NINE, effect=None)

    basic_state.players[0].draw_card(card3)
    basic_state.players[1].draw_card(card2)
    basic_state.players[2].draw_card(card1)

    gm = GameMaster()

    gm.process_turn(basic_state)

    assert not basic_state.effect_active

    gm.process_turn(basic_state)

    assert basic_state.effect_active
    assert not basic_state.execute_effect
    assert basic_state.cards_to_draw == 2

    gm.process_turn(basic_state)

    assert basic_state.effect_active
    assert not basic_state.execute_effect
    assert basic_state.cards_to_draw == 5

    gm.process_turn(basic_state)

    assert not basic_state.effect_active
    assert len(basic_state.players[0].hand) == 5


def test_king_war_heart_starts(basic_state):
    card1 = Card(Suit.HEART, Value.KING, effect=None)
    card2 = Card(Suit.SPADES, Value.KING, effect=None)
    card3 = Card(Suit.HEART, Value.NINE, effect=None)

    basic_state.players[0].draw_card(card3)
    basic_state.players[1].draw_card(card1)
    basic_state.players[2].draw_card(card2)

    gm = GameMaster()

    gm.process_turn(basic_state)

    assert not basic_state.effect_active

    print(basic_state.deck.top_stack_card)

    gm.process_turn(basic_state)

    assert basic_state.effect_active
    assert basic_state.cards_to_draw == 5
    assert basic_state.turn_direction == 1

    gm.process_turn(basic_state)

    assert basic_state.effect_active
    assert basic_state.cards_to_draw == 10
    assert basic_state.turn_direction == -1

    gm.process_turn(basic_state)

    assert len(basic_state.players[1].hand) == 10


def test_war_effect_spades_starts(basic_state):
    card1 = Card(Suit.HEART, Value.KING, effect=None)
    card2 = Card(Suit.SPADES, Value.KING, effect=None)
    card3 = Card(Suit.SPADES, Value.EIGHT, effect=None)
    # TODO in this case one player should have more cards
    basic_state.players[0].draw_card(card3)
    basic_state.players[1].draw_card(card2)
    basic_state.players[2].draw_card(card1)

    gm = GameMaster()

    print("1", basic_state.deck.top_stack_card)

    gm.process_turn(basic_state)

    print("2", basic_state.deck.top_stack_card)

    assert not basic_state.effect_active

    gm.process_turn(basic_state)

    print("3", basic_state.deck.top_stack_card)

    assert basic_state.effect_active
    assert basic_state.cards_to_draw == 5
    assert basic_state.turn_direction == -1

    gm.process_turn(basic_state)

    print("4", basic_state.deck.top_stack_card)

    assert basic_state.effect_active
    assert basic_state.cards_to_draw == 10
    assert basic_state.turn_direction == 1

    gm.process_turn(basic_state)

    print("5", basic_state.deck.top_stack_card)

    assert len(basic_state.players[1].hand) == 10


def test_block_effect(basic_state):
    ...


def test_value_demand(basic_state):
    ...

def test_suit_demand(basic_state):
    ...

def test_advance_turn(basic_state):

    curr_index = basic_state.current_player_index
    gm = GameMaster()
    next_state = gm._advance_turn(basic_state)

    next_index = next_state.current_player_index

    assert curr_index + 1 == next_state.current_player_index

