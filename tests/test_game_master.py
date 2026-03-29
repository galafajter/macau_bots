import pytest
from unittest.mock import patch
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

    return GameState(deck=deck,
                      players=[player1, player2, player3],
                      current_player_index=0)

# advance turn

def test_advance_turn(basic_state):

    curr_index = basic_state.current_player_index
    gm = GameMaster()
    next_state = gm._advance_turn(basic_state)

    assert curr_index + 1 == next_state.current_player_index

def test_advance_turn_wraps_around(basic_state):

    basic_state.current_player_index = len(basic_state.players) - 1
    gm = GameMaster()
    next_state = gm._advance_turn(basic_state)

    assert next_state.current_player_index == 0


def test_advance_turn_reversed(basic_state):

    basic_state.current_player_index = 0
    basic_state.turn_direction = -1
    gm = GameMaster()
    next_state = gm._advance_turn(basic_state)

    assert next_state.current_player_index == len(basic_state.players) - 1

# war

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

    initial_hand_size = len(basic_state.players[0].hand)
    gm.process_turn(basic_state)
    assert not basic_state.effect_active
    assert len(basic_state.players[0].hand) == initial_hand_size + 5
    assert basic_state.cards_to_draw == 0


def test_war_player_draws_when_cannot_respond(basic_state):

    gm = GameMaster()

    basic_state.players[0].hand = [Card(Suit.HEART, Value.THREE, effect=None)]
    basic_state.players[1].hand = [Card(Suit.HEART, Value.SEVEN, effect=None)]

    initial_hand_size = len(basic_state.players[1].hand)

    gm.process_turn(basic_state)

    gm.process_turn(basic_state)

    assert len(basic_state.players[1].hand) == initial_hand_size + 3
    assert basic_state.cards_to_draw == 0

# king war

def test_king_war_heart(basic_state):
    king_heart = Card(Suit.HEART, Value.KING, effect=None)
    king_spades = Card(Suit.SPADES, Value.KING, effect=None)
    nine_heart = Card(Suit.HEART, Value.NINE, effect=None)

    basic_state.players[0].hand = [king_heart, nine_heart]
    basic_state.players[1].hand = [king_spades]

    gm = GameMaster()

    gm.process_turn(basic_state)

    assert basic_state.effect_active
    assert basic_state.cards_to_draw == 5
    assert basic_state.turn_direction == 1

    gm.process_turn(basic_state)

    assert basic_state.effect_active
    assert basic_state.cards_to_draw == 10
    assert basic_state.turn_direction == -1

    initial_hand_size = len(basic_state.players[0].hand)

    gm.process_turn(basic_state)

    assert len(basic_state.players[0].hand) == initial_hand_size + 10
    assert basic_state.cards_to_draw == 0


def test_king_war_spades(basic_state):
    king_spades = Card(Suit.SPADES, Value.KING, effect=None)
    king_heart = Card(Suit.HEART, Value.KING, effect=None)

    basic_state.players[0].hand = [king_spades]
    basic_state.players[2].hand = [king_heart]  # gracz 2 bo kierunek się odwraca
    basic_state.players[1].hand = [Card(Suit.HEART, Value.NINE, effect=None)]

    basic_state.deck.put_on_stack(Card(Suit.SPADES, Value.EIGHT, effect=None))

    gm = GameMaster()

    gm.process_turn(basic_state)  # gracz 0 kładzie króla pik
    assert basic_state.effect_active
    assert basic_state.cards_to_draw == 5
    assert basic_state.turn_direction == -1

    gm.process_turn(basic_state)  # gracz 2 dokłada króla kier
    assert basic_state.effect_active
    assert basic_state.cards_to_draw == 10
    assert basic_state.turn_direction == 1  # pik znowu odwraca

    initial_hand_size = len(basic_state.players[0].hand)

    gm.process_turn(basic_state)

    assert len(basic_state.players[0].hand) == initial_hand_size + 10
    assert basic_state.cards_to_draw == 0

# --- block ---

def test_block_player_loses_turn(basic_state):
    four_card = Card(Suit.HEART, Value.FOUR, effect=None)
    basic_state.players[0].hand = [four_card]

    gm = GameMaster()
    gm.process_turn(basic_state)

    # gracz 1 powinien być zablokowany — jego tura powinna zostać pominięta
    index_before_block_turn = basic_state.current_player_index
    gm.process_turn(basic_state)

    assert basic_state.current_player_index != index_before_block_turn


def test_block_accumulates(basic_state):
    card1 = Card(Suit.HEART, Value.FOUR, effect=None)
    card2 = Card(Suit.SPADES, Value.FOUR, effect=None)
    card3 = Card(Suit.CLUBS, Value.EIGHT, effect=None)

    basic_state.players[0].draw_card(card1)
    basic_state.players[1].draw_card(card2)
    basic_state.players[2].draw_card(card3)

    gm = GameMaster()

    gm.process_turn(basic_state)
    gm.process_turn(basic_state)

    # gracz 2 dołożył ósemkę więc nie może odpowiedzieć czwórką
    # gracz 0 powinien być zablokowany na 2 tury
    assert basic_state.current_player_index != 0 or 0 in basic_state.blocked_turns_per_player

# --- queen ---

def test_queen_resets_war(basic_state):
    basic_state.cards_to_draw = 4
    basic_state.effect_active = True
    queen_card = Card(Suit.HEART, Value.QUEEN, effect=None)
    basic_state.players[0].hand = [queen_card]

    gm = GameMaster()
    gm.process_turn(basic_state)

    assert basic_state.cards_to_draw == 0
    assert not basic_state.effect_active


def test_queen_resets_demand(basic_state):
    basic_state.demanded_value = Value.NINE
    basic_state.demand_turns_left = 2
    queen_card = Card(Suit.HEART, Value.QUEEN, effect=None)
    basic_state.players[0].hand = [queen_card]

    gm = GameMaster()
    gm.process_turn(basic_state)

    assert basic_state.demanded_value is None

def test_queen_resets_block(basic_state):
    ...


# --- value demand ---

def test_value_demand_sets_state(basic_state):
    jack_card = Card(Suit.HEART, Value.JACK, effect=None)
    basic_state.players[0].hand = [jack_card]

    gm = GameMaster()
    with patch.object(basic_state.players[0], 'make_value_demand', return_value=Value.NINE):
        gm.process_turn(basic_state)

    assert basic_state.demanded_value == Value.NINE
    assert basic_state.demand_turns_left > 0


def test_value_demand_expires_after_all_players(basic_state):
    jack_card = Card(Suit.HEART, Value.JACK, effect=None)
    nine_heart = Card(Suit.HEART, Value.NINE, effect=None)
    nine_spades = Card(Suit.SPADES, Value.NINE, effect=None)

    basic_state.players[0].hand = [jack_card]
    basic_state.players[1].hand = [nine_heart]
    basic_state.players[2].hand = [nine_spades]

    gm = GameMaster()
    with patch.object(basic_state.players[0], 'make_value_demand', return_value=Value.NINE):
        gm.process_turn(basic_state)  # gracz 0 kładzie waleta, żąda dziewiątki
        gm.process_turn(basic_state)  # gracz 1 spełnia żądanie
        gm.process_turn(basic_state)  # gracz 2 spełnia żądanie

    assert basic_state.demanded_value is None


# --- suit demand ---

def test_suit_demand_sets_state(basic_state):
    ace_card = Card(Suit.HEART, Value.ACE, effect=None)
    basic_state.players[0].hand = [ace_card]

    gm = GameMaster()
    with patch.object(basic_state.players[0], 'make_suit_demand', return_value=Suit.SPADES):
        gm.process_turn(basic_state)

    assert basic_state.demanded_suit == Suit.SPADES
    assert basic_state.demand_turns_left > 0


def test_suit_demand_restricts_playable_cards(basic_state):
    basic_state.demanded_suit = Suit.SPADES
    basic_state.demand_turns_left = 2

    gm = GameMaster()
    playable = gm.get_playable_card(basic_state)

    assert all(card.suit == Suit.SPADES for card in playable)


# --- playable hand ---

def test_playable_hand_cleared_between_turns(basic_state):
    card1 = Card(Suit.HEART, Value.EIGHT, effect=None)
    card2 = Card(Suit.SPADES, Value.FIVE, effect=None)
    basic_state.players[0].hand = [card1]
    basic_state.players[0].playable_hand = [card2]  # stara zawartość z poprzedniej tury

    gm = GameMaster()
    gm.process_turn(basic_state)

    assert card2 not in basic_state.players[0].playable_hand
