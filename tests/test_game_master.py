"""Testy GameMastera per efekt -- deterministyczne (kontrolowane talie z helpers).

Aserty blokady i wojny odpowiadaja regułom z PR "block + lucky card":
- blokada: 1x4 = 1 tura pauzy (kumulacja łańcucha), bez dobierania,
- szczęśliwa karta: przy wojnie/żądaniach pierwsza dobrana karta jest
  próbą odpowiedzi (nietrafna wraca do ręki i wlicza się do kary).
"""

from unittest.mock import patch

from core.card import Suit, Value
from core.game_master import GameMaster
from tests.helpers import card

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


# war (2/3)


def test_war_effect(basic_state):
    # dobór kontrolowany: kolejne karty NIE są odpowiedzią na wojnę (pasywne)
    drawing = [card(Suit.CLUBS, v) for v in
               (Value.FIVE, Value.SIX, Value.SEVEN, Value.NINE, Value.TEN)]
    basic_state.deck.drawing_cards = list(drawing)

    basic_state.players[0].hand = [card(Suit.HEART, Value.NINE)]  # 9♥ na 8♥
    basic_state.players[1].hand = [card(Suit.HEART, Value.TWO)]   # wojna 2
    basic_state.players[2].hand = [card(Suit.HEART, Value.THREE)]  # wojna 3 -> kara 5

    gm = GameMaster()

    gm.process_turn(basic_state)  # gracz 0: 9♥, brak efektu
    assert not basic_state.effect_active

    gm.process_turn(basic_state)  # gracz 1: 2♥ -> wojna 2
    assert basic_state.effect_active
    assert basic_state.cards_to_draw == 2

    gm.process_turn(basic_state)  # gracz 2: 3♥ z ręki -> kara przechodzi 2+3
    assert basic_state.effect_active
    assert not basic_state.execute_effect
    assert basic_state.cards_to_draw == 5

    initial_hand_size = len(basic_state.players[0].hand)  # 0 kart
    gm.process_turn(basic_state)  # gracz 0 bez odpowiedzi: szczęśliwa karta + reszta kary
    assert not basic_state.effect_active
    assert len(basic_state.players[0].hand) == initial_hand_size + 5
    assert basic_state.cards_to_draw == 0


def test_war_player_draws_when_cannot_respond(basic_state):
    # trial (pop z końca): K♦ -- pasywny król nie jest odpowiedzią na wojnę 3
    basic_state.deck.drawing_cards = [card(Suit.DIAMOND, Value.SEVEN),
                                      card(Suit.DIAMOND, Value.EIGHT),
                                      card(Suit.CLUBS, Value.KING)]

    basic_state.players[0].hand = [card(Suit.HEART, Value.THREE)]  # wojna 3
    basic_state.players[1].hand = [card(Suit.HEART, Value.SEVEN)]   # brak odpowiedzi

    initial_hand_size = len(basic_state.players[1].hand)

    gm = GameMaster()

    gm.process_turn(basic_state)  # gracz 0: 3♥ (pasuje kolorem do 8♥)
    gm.process_turn(basic_state)  # gracz 1: brak odpowiedzi -> trial + reszta kary (2 Karty)

    assert len(basic_state.players[1].hand) == initial_hand_size + 3
    assert basic_state.cards_to_draw == 0


# king war


def test_king_war_heart(basic_state):
    drawing = [card(Suit.CLUBS, v) for v in
               (Value.FIVE, Value.SIX, Value.SEVEN, Value.EIGHT, Value.NINE)]
    drawing += [card(Suit.DIAMOND, v) for v in
                (Value.FIVE, Value.SIX, Value.SEVEN, Value.EIGHT, Value.NINE)]
    basic_state.deck.drawing_cards = drawing  # 10x pasywna, nie-królewska

    basic_state.players[0].hand = [card(Suit.HEART, Value.KING),
                                   card(Suit.HEART, Value.NINE)]
    basic_state.players[1].hand = [card(Suit.SPADES, Value.KING)]  # odpowiedź Królem

    gm = GameMaster()

    gm.process_turn(basic_state)  # gracz 0: K♥ -> wojna 5, kierunek 1
    assert basic_state.effect_active
    assert basic_state.cards_to_draw == 5
    assert basic_state.turn_direction == 1

    gm.process_turn(basic_state)  # gracz 1: K♠ -> wojna 10, kierunek -1
    assert basic_state.effect_active
    assert basic_state.cards_to_draw == 10
    assert basic_state.turn_direction == -1

    initial_hand_size = len(basic_state.players[0].hand)  # [9♥]

    gm.process_turn(basic_state)  # kierunek -1: znowu gracz 0, brak odpowiedzi

    assert len(basic_state.players[0].hand) == initial_hand_size + 10  # trial + 9
    assert basic_state.cards_to_draw == 0
    assert not basic_state.effect_active


def test_king_war_spades(basic_state):
    basic_state.deck.drawing_cards = [card(Suit.CLUBS, v) for v in
                                       (Value.FIVE, Value.SIX, Value.SEVEN)]
    basic_state.deck.drawing_cards += [card(Suit.DIAMOND, v) for v in
                                        (Value.FIVE, Value.SIX, Value.SEVEN, Value.EIGHT)]
    basic_state.deck.drawing_cards.append(card(Suit.CLUBS, Value.TEN))  # trial z końca

    basic_state.players[0].hand = [card(Suit.SPADES, Value.KING)]
    basic_state.players[2].hand = [card(Suit.HEART, Value.KING)]  # gracz 2 bo kierunek się odwraca
    basic_state.players[1].hand = [card(Suit.HEART, Value.NINE)]

    basic_state.deck.put_on_stack(card(Suit.SPADES, Value.EIGHT))

    gm = GameMaster()

    gm.process_turn(basic_state)  # gracz 0 kładzie króla pik
    assert basic_state.effect_active
    assert basic_state.cards_to_draw == 5
    assert basic_state.turn_direction == -1

    gm.process_turn(basic_state)  # gracz 2 (kierunek -1): K♥ -> kara 10, kierunek 1
    assert basic_state.cards_to_draw == 10
    assert basic_state.turn_direction == 1  # kier z powrotem odwraca

    initial_hand_size = len(basic_state.players[0].hand)  # 0 -- gracz 0 następny (kier. +1)

    gm.process_turn(basic_state)  # gracz 0: brak odpowiedzi -> trial + reszta kary (9)

    assert len(basic_state.players[0].hand) == initial_hand_size + 10
    assert len(basic_state.players[1].hand) == 1  # gracz 1 nie uczestniczył w karze
    assert basic_state.cards_to_draw == 0


# --- block (reguła: 1x4 = 1 tura pauzy) ---


def test_block_player_loses_turn(basic_state):
    basic_state.players[0].hand = [card(Suit.HEART, Value.FOUR)]  # 4♥ na 8♥ (kolor)

    gm = GameMaster()
    gm.process_turn(basic_state)  # gracz 0: 4 -> blokada 1 czekającego

    # gracz 1 (pusta ręka) nie ma obrony -> pauza dokładnie 1 tury
    index_before_block_turn = basic_state.current_player_index
    action = gm.process_turn(basic_state)

    assert basic_state.blocked_turns_per_player == {1: 1}
    assert action == {"action": "execute_block"}
    assert basic_state.current_player_index != index_before_block_turn
    assert len(basic_state.players[1].hand) == 0  # bez dobierania

    # pominięta tura gracza 1
    basic_state.current_player_index = 1
    action = gm.process_turn(basic_state)
    assert action == {"action": "skipped_turn_because_of_block"}
    assert basic_state.blocked_turns_per_player == {}  # wygasła po JEDNEJ turze


def test_block_accumulates(basic_state):
    basic_state.players[0].hand = [card(Suit.HEART, Value.FOUR)]    # 1. czwórka
    basic_state.players[1].hand = [card(Suit.SPADES, Value.FOUR)]   # obrona czwórką
    basic_state.players[2].hand = [card(Suit.CLUBS, Value.EIGHT)]   # brak obrony (kierunek dalej: gracz 2 po P1)

    gm = GameMaster()

    gm.process_turn(basic_state)  # gracz 0: 4♥
    gm.process_turn(basic_state)  # gracz 1: 4♠ (łańcuch -> blokada 2)

    assert basic_state.block_count == 2
    # gracz 2 nie może odpowiedzieć (8♣), blokada 2 tur:
    gm.process_turn(basic_state)
    assert basic_state.blocked_turns_per_player == {2: 2}


# --- queen ---


def test_queen_resets_war(basic_state):
    basic_state.cards_to_draw = 4
    basic_state.effect_active = True
    basic_state.players[0].hand = [card(Suit.HEART, Value.QUEEN)]

    gm = GameMaster()
    gm.process_turn(basic_state)

    assert basic_state.cards_to_draw == 0
    assert not basic_state.effect_active


def test_queen_resets_demand(basic_state):
    basic_state.demanded_value = Value.NINE
    basic_state.demand_turns_left = 2
    basic_state.players[0].hand = [card(Suit.HEART, Value.QUEEN)]

    gm = GameMaster()
    gm.process_turn(basic_state)

    assert basic_state.demanded_value is None


def test_queen_resets_block(basic_state):
    basic_state.block_count = 3
    basic_state.effect_active = True
    basic_state.players[0].hand = [card(Suit.HEART, Value.QUEEN)]  # Dama na 8♥ pasuje kolorem

    gm = GameMaster()
    action = gm.process_turn(basic_state)

    assert action == {"action": "skip", "card": "Q Heart"}
    assert basic_state.block_count == 0
    assert basic_state.blocked_turns_per_player == {}
    assert not basic_state.effect_active


# --- value demand (Walet) ---


def test_value_demand_sets_state(basic_state):
    basic_state.players[0].hand = [card(Suit.HEART, Value.JACK)]  # J♥ na 8♥

    gm = GameMaster()
    with patch.object(basic_state.players[0], "make_value_demand", return_value=Value.NINE):
        gm.process_turn(basic_state)

    assert basic_state.demanded_value == Value.NINE
    assert basic_state.demand_turns_left > 0


def test_value_demand_expires_after_all_players(basic_state):
    # trial gracza 0 (ostatnia tura): 5♦ -- nie dziewiątka
    basic_state.deck.drawing_cards = [card(Suit.DIAMOND, Value.FIVE)]

    basic_state.players[0].hand = [card(Suit.HEART, Value.JACK)]
    basic_state.players[1].hand = [card(Suit.HEART, Value.NINE)]
    basic_state.players[2].hand = [card(Suit.SPADES, Value.NINE)]

    gm = GameMaster()
    with patch.object(basic_state.players[0], "make_value_demand", return_value=Value.NINE):
        gm.process_turn(basic_state)  # gracz 0 kładzie waleta, żąda dziewiątki
        gm.process_turn(basic_state)  # gracz 1 spełnia żądanie
        gm.process_turn(basic_state)  # gracz 2 spełnia żądanie
        gm.process_turn(basic_state)  # gracz 0: brak odpowiedzi -> trial, żądanie wygasa

    assert basic_state.demanded_value is None
    assert basic_state.demand_turns_left == 0
    assert not basic_state.effect_active
    assert len(basic_state.players[0].hand) == 1  # próbna karta zostaje w ręce


# --- suit demand (As) ---


def test_suit_demand_sets_state(basic_state):
    basic_state.players[0].hand = [card(Suit.HEART, Value.ACE)]  # A♥ na 8♥

    gm = GameMaster()
    with patch.object(basic_state.players[0], "make_suit_demand", return_value=Suit.SPADES):
        gm.process_turn(basic_state)

    assert basic_state.demanded_suit == Suit.SPADES
    assert basic_state.demand_turns_left > 0


def test_suit_demand_restricts_playable_cards(basic_state):
    basic_state.demanded_suit = Suit.SPADES
    basic_state.demand_turns_left = 2

    gm = GameMaster()
    playable = gm.get_playable_card(basic_state)

    assert playable
    assert all(c.suit == Suit.SPADES for c in playable)


# --- playable hand ---


def test_playable_hand_cleared_between_turns(basic_state):
    card1 = card(Suit.HEART, Value.EIGHT)
    card2 = card(Suit.SPADES, Value.FIVE)
    basic_state.players[0].hand = [card1]
    basic_state.players[0].playable_hand = [card2]  # stara zawartość z poprzedniej tury

    gm = GameMaster()
    gm.process_turn(basic_state)

    assert card2 not in basic_state.players[0].playable_hand
