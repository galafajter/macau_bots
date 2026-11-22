"""Testy reguł z PR "block + lucky card".

A) Blokada 4: gracz, który nie odpowiedział (4/Dama), pauzuje dokładnie
   tyle własnych tur, ile czwórek zagrano w łańcuchu -- bez mnożnika
   (liczba graczy - 1) i bez dobierania kart.
B) "Szczęśliwa karta": pierwsza dobrana karta przy aktywnym efekcie
   (wojna / żądanie wartości / żądanie koloru) jest próbą odpowiedzi;
   jeśli jest legalna, gracz może ją zagrać -- kara przechodzi dalej,
   a przy rezygnacji pobierana jest reszta kary.

Testy są deterministyczne: talie budowane ręcznie (Deck dobiera z KOŃCA
listy drawing_cards, patrz tests.helpers.make_deck).
"""

from core.card import Suit, Value
from core.game_master import GameMaster
from core.game_state import GameState
from tests.helpers import DecliningPlayer, DummyPlayer, card, make_deck


def three_players():
    return DummyPlayer("P1"), DummyPlayer("P2"), DummyPlayer("P3")


# ---------------------------------------------------------------- blokada 4

def test_single_four_blocks_next_player_for_exactly_one_turn():
    gm = GameMaster()
    p1, p2, p3 = three_players()
    # P1 właśnie zagrał 4 pika (efekt blokady aktywny), teraz tura P2
    state = GameState(
        deck=make_deck([card(Suit.SPADES, Value.FOUR)], [card(Suit.HEART, Value.EIGHT)]),
        players=[p1, p2, p3],
        current_player_index=1,
        effect_active=True,
        block_count=1,
    )
    p1.hand = [card(Suit.CLUBS, Value.TEN)]
    p2.hand = [card(Suit.SPADES, Value.SEVEN)]  # brak 4 i Damy -> brak obrony
    p3.hand = [card(Suit.DIAMOND, Value.SIX)]

    action = gm.process_turn(state)

    assert action == {"action": "execute_block"}
    assert state.blocked_turns_per_player == {1: 1}
    assert len(p2.hand) == 1  # blokada: bez dobierania kart
    assert state.current_player_index == 2

    # pierwsza tura P2 po pawzie -- skip
    state.current_player_index = 1
    action = gm.process_turn(state)
    assert action == {"action": "skipped_turn_because_of_block"}
    assert state.blocked_turns_per_player == {}  # wygasła po JEDNEJ turze pauzy
    assert len(p2.hand) == 1  # pauza bez doboru
    assert state.current_player_index == 2

    # kolejna tura P2: już zablokowany nie jest, gra normalnie (7 pika na 4 pika)
    state.current_player_index = 1
    action = gm.process_turn(state)
    assert action == {"action": "play_card", "card": "7 Spades"}
    assert len(p2.hand) == 0


def test_two_fours_chain_pause_two_turns():
    gm = GameMaster()
    p1, p2, p3 = three_players()
    state = GameState(
        deck=make_deck([card(Suit.SPADES, Value.FOUR)], [card(Suit.HEART, Value.EIGHT)]),
        players=[p1, p2, p3],
        current_player_index=1,
        effect_active=True,
        block_count=2,  # dwie czwórki w łańcuchu
    )
    p2.hand = [card(Suit.CLUBS, Value.TEN)]  # brak obrony

    gm.process_turn(state)
    assert state.blocked_turns_per_player == {1: 2}

    # pauza 1
    state.current_player_index = 1
    action = gm.process_turn(state)
    assert action == {"action": "skipped_turn_because_of_block"}
    assert state.blocked_turns_per_player == {1: 1}  # jeszcze nie wygasła

    # pauza 2
    state.current_player_index = 1
    action = gm.process_turn(state)
    assert action == {"action": "skipped_turn_because_of_block"}
    assert state.blocked_turns_per_player == {}


def test_four_defense_passes_block_to_next_player():
    gm = GameMaster()
    p1, p2, p3 = three_players()
    state = GameState(
        deck=make_deck([card(Suit.HEART, Value.FOUR)], [card(Suit.HEART, Value.EIGHT)]),
        players=[p1, p2, p3],
        current_player_index=1,
        effect_active=True,
        block_count=1,
    )
    p2.hand = [card(Suit.SPADES, Value.FOUR)]  # obrona czwórką

    action = gm.process_turn(state)
    assert action == {"action": "block", "card": "4 Spades"}
    assert state.block_count == 2  # łańcuch się kumuluje
    assert state.current_player_index == 2  # teraz bronić się musi P3

    # P3 bez obrony -> pauza 2 tur
    p3.hand = [card(Suit.DIAMOND, Value.SIX)]
    gm.process_turn(state)
    assert state.blocked_turns_per_player == {2: 2}


def test_queen_defense_resets_block():
    gm = GameMaster()
    p1, p2, p3 = three_players()
    state = GameState(
        deck=make_deck([card(Suit.SPADES, Value.FOUR)], [card(Suit.HEART, Value.EIGHT)]),
        players=[p1, p2, p3],
        current_player_index=1,
        effect_active=True,
        block_count=1,
    )
    p2.hand = [card(Suit.HEART, Value.QUEEN)]  # obrona Damą

    action = gm.process_turn(state)
    assert action == {"action": "skip", "card": "Q Heart"}
    assert state.block_count == 0
    assert state.effect_active is False
    assert state.blocked_turns_per_player == {}  # nikt nie pauzuje


# ------------------------------------------------------- szczęśliwa karta: wojna

def test_war_defense_from_hand_beats_lucky_path():
    """Odpowiedź z ręki ma pierwszeństwo: szczęśliwa karta to ścieżka awaryjna."""
    gm = GameMaster()
    p1, p2, p3 = three_players()
    state = GameState(
        deck=make_deck([card(Suit.HEART, Value.TWO)], [card(Suit.SPADES, Value.THREE)]),
        players=[p1, p2, p3],
        current_player_index=1,
        effect_active=True,
        cards_to_draw=2,
    )
    p2.hand = [card(Suit.HEART, Value.THREE)]  # wojenna trójka W RĘCE

    action = gm.process_turn(state)
    assert action == {"action": "war", "card": "3 Heart"}
    assert state.cards_to_draw == 5
    assert state.lucky_drawn is False  # ścieżka szczęśliwej karty nie ruszyła
    assert len(p2.hand) == 0
    assert state.deck.drawing_cards == [card(Suit.SPADES, Value.THREE)]  # nic nie ubyło z talii


def test_war_lucky_card_transfers_penalty_to_next_player():
    gm = GameMaster()
    p1, p2, p3 = three_players()
    state = GameState(
        deck=make_deck([card(Suit.HEART, Value.TWO)],
                       [card(Suit.CLUBS, Value.SIX), card(Suit.SPADES, Value.THREE)]),
        players=[p1, p2, p3],
        current_player_index=1,
        effect_active=True,
        cards_to_draw=2,
    )
    p2.hand = [card(Suit.CLUBS, Value.KING)]  # pasywny Król -- brak odpowiedzi w ręce

    action = gm.process_turn(state)

    # próbny dobór = 3 pika (KONIEC listy drawing_cards) -- karta wojenna, zagrana
    assert action == {"action": "war", "card": "3 Spades"}
    assert state.cards_to_draw == 5  # kara 2 + 3 przechodzi na następnego
    assert len(p2.hand) == 1  # dobrał 1 i ją zagrał (ręka bez zmiany rozmiaru)
    assert state.deck.top_stack_card == card(Suit.SPADES, Value.THREE)
    assert state.current_player_index == 2
    assert state.effect_active is True  # wojna wciąż aktywna -- dla P3
    # reszta kary (6 trefl) zostaje w talii -- jej P2 już nie dobiera
    assert state.deck.drawing_cards == [card(Suit.CLUBS, Value.SIX)]


def test_king_war_lucky_card_transfers_and_flips_direction():
    gm = GameMaster()
    p1, p2, p3 = three_players()
    state = GameState(
        deck=make_deck([card(Suit.HEART, Value.KING)], [card(Suit.SPADES, Value.KING)]),
        players=[p1, p2, p3],
        current_player_index=1,
        effect_active=True,
        cards_to_draw=5,
    )
    p2.hand = [card(Suit.DIAMOND, Value.SIX)]

    action = gm.process_turn(state)

    assert action == {"action": "war", "card": "K Spades"}
    assert state.cards_to_draw == 10  # 5 + 5 dalej
    assert state.turn_direction == -1  # pikowy Król odwraca kierunek
    assert len(p2.hand) == 1


def test_war_lucky_declined_draws_full_penalty():
    gm = GameMaster()
    p1, p2, p3 = three_players()
    p2 = DecliningPlayer("P2")
    p2.decline_lucky = True
    state = GameState(
        deck=make_deck([card(Suit.HEART, Value.TWO)],
                       [card(Suit.DIAMOND, Value.NINE), card(Suit.SPADES, Value.THREE)]),
        players=[p1, p2, p3],
        current_player_index=1,
        effect_active=True,
        cards_to_draw=2,
    )
    p2.hand = [card(Suit.CLUBS, Value.KING)]

    action = gm.process_turn(state)

    assert action == {"action": "execute_war"}
    # odrzucona szczęśliwa (3 pika) zostaje w ręce + reszta kary (1 karta: 9 karo)
    assert len(p2.hand) == 3
    assert card(Suit.SPADES, Value.THREE) in p2.hand
    assert card(Suit.DIAMOND, Value.NINE) in p2.hand
    assert state.cards_to_draw == 0  # wojna wygasła
    assert state.effect_active is False


def test_war_without_lucky_draws_full_penalty():
    gm = GameMaster()
    p1, p2, p3 = three_players()
    state = GameState(
        deck=make_deck([card(Suit.HEART, Value.TWO)],
                       [card(Suit.CLUBS, Value.SEVEN), card(Suit.HEART, Value.EIGHT)]),
        players=[p1, p2, p3],
        current_player_index=1,
        effect_active=True,
        cards_to_draw=2,
    )
    p2.hand = [card(Suit.DIAMOND, Value.SIX)]

    action = gm.process_turn(state)

    assert action == {"action": "execute_war"}
    # próbna (8 kier, nie-wojenna) + reszta kary (1 karta: 7 trefl) = komplet
    assert len(p2.hand) == 3
    assert card(Suit.HEART, Value.EIGHT) in p2.hand
    assert card(Suit.CLUBS, Value.SEVEN) in p2.hand
    assert state.cards_to_draw == 0
    assert state.effect_active is False


def test_war_trial_queen_negates_war():
    """Dama jako próbna karta niweluje wojnę (jest legalną odpowiedzią)."""
    gm = GameMaster()
    p1, p2, p3 = three_players()
    state = GameState(
        deck=make_deck([card(Suit.HEART, Value.TWO)], [card(Suit.SPADES, Value.QUEEN)]),
        players=[p1, p2, p3],
        current_player_index=1,
        effect_active=True,
        cards_to_draw=2,
    )
    p2.hand = [card(Suit.DIAMOND, Value.SIX)]

    action = gm.process_turn(state)

    assert action == {"action": "skip", "card": "Q Spades"}
    assert state.cards_to_draw == 0
    assert state.effect_active is False
    assert len(p2.hand) == 1  # dobrał Damę i ją zagrał


# ------------------------------------------ szczęśliwa karta: żądania (Walet/As)

def test_value_demand_miss_draws_exactly_one_card():
    """NOWOŚĆ: nieudana odpowiedź na żądanie wartości = 1 dobrana karta
    (wcześniej gracz nie dobierał nic)."""
    gm = GameMaster()
    p1, p2, p3 = three_players()
    state = GameState(
        deck=make_deck([card(Suit.HEART, Value.JACK)], [card(Suit.DIAMOND, Value.NINE)]),
        players=[p1, p2, p3],
        current_player_index=1,
        effect_active=True,
        demanded_value=Value.FIVE,
        demand_turns_left=4,
    )
    p2.hand = [card(Suit.HEART, Value.SEVEN)]

    action = gm.process_turn(state)

    assert action == {"action": "draw_card_because_dont_have_value"}
    assert len(p2.hand) == 2  # próbna 9 karo nie jest piątką -> zostaje, koniec tury
    assert state.demanded_value is Value.FIVE  # żądanie żyje dalej
    assert state.effect_active is True
    assert state.demand_turns_left == 3  # nieudana tura zużywa "życie" żądania


def test_value_demand_lucky_card_satisfies_demand():
    gm = GameMaster()
    p1, p2, p3 = three_players()
    state = GameState(
        deck=make_deck([card(Suit.HEART, Value.JACK)], [card(Suit.CLUBS, Value.FIVE)]),
        players=[p1, p2, p3],
        current_player_index=1,
        effect_active=True,
        demanded_value=Value.FIVE,
        demand_turns_left=4,
    )
    p2.hand = [card(Suit.HEART, Value.SEVEN)]

    action = gm.process_turn(state)

    assert action == {"action": "play_demanded_value", "card": "5 Clubs"}
    assert len(p2.hand) == 1  # dobrał piątkę i ją zagrał
    assert state.deck.top_stack_card == card(Suit.CLUBS, Value.FIVE)
    assert state.demanded_value is Value.FIVE  # żądanie nadal dotyczy kolejnych graczy


def test_suit_demand_miss_draws_exactly_one_card():
    gm = GameMaster()
    p1, p2, p3 = three_players()
    state = GameState(
        deck=make_deck([card(Suit.HEART, Value.ACE)], [card(Suit.CLUBS, Value.NINE)]),
        players=[p1, p2, p3],
        current_player_index=1,
        effect_active=True,
        demanded_suit=Suit.SPADES,
        demand_turns_left=4,
    )
    p2.hand = [card(Suit.HEART, Value.SEVEN)]

    action = gm.process_turn(state)

    assert action == {"action": "draw_card_because_dont_have_suit"}
    assert len(p2.hand) == 2
    assert state.demanded_suit is Suit.SPADES
    assert state.demand_turns_left == 3


def test_suit_demand_lucky_card_satisfies_demand():
    gm = GameMaster()
    p1, p2, p3 = three_players()
    state = GameState(
        deck=make_deck([card(Suit.HEART, Value.ACE)], [card(Suit.SPADES, Value.NINE)]),
        players=[p1, p2, p3],
        current_player_index=1,
        effect_active=True,
        demanded_suit=Suit.SPADES,
        demand_turns_left=4,
    )
    p2.hand = [card(Suit.HEART, Value.SEVEN)]

    action = gm.process_turn(state)

    assert action == {"action": "play_demanded_suit", "card": "9 Spades"}
    assert len(p2.hand) == 1
    assert state.deck.top_stack_card == card(Suit.SPADES, Value.NINE)


def test_value_demand_expires_when_lives_run_out():
    gm = GameMaster()
    p1, p2, p3 = three_players()
    state = GameState(
        deck=make_deck([card(Suit.HEART, Value.JACK)], [card(Suit.DIAMOND, Value.NINE)]),
        players=[p1, p2, p3],
        current_player_index=1,
        effect_active=True,
        demanded_value=Value.FIVE,
        demand_turns_left=1,  # ostatnie "życie"
    )
    p2.hand = [card(Suit.HEART, Value.SEVEN)]

    action = gm.process_turn(state)

    assert action == {"action": "draw_card_because_dont_have_value"}
    assert state.demand_turns_left == 0
    assert state.demanded_value is None  # żądanie wygasło
    assert state.effect_active is False


# --------------------------------------------------------------- pozostałe

def test_block_does_not_use_lucky_path():
    """Blokada nie jest rozliczana dobieraniem -- próbna karta nie jest brana."""
    gm = GameMaster()
    p1, p2, p3 = three_players()
    state = GameState(
        deck=make_deck([card(Suit.SPADES, Value.FOUR)], [card(Suit.HEART, Value.EIGHT)]),
        players=[p1, p2, p3],
        current_player_index=1,
        effect_active=True,
        block_count=1,
    )
    p2.hand = [card(Suit.DIAMOND, Value.SIX)]

    gm.process_turn(state)

    assert state.lucky_drawn is False
    assert len(p2.hand) == 1  # nic nie dobrał
    assert state.blocked_turns_per_player == {1: 1}


def test_normal_miss_without_effect_draws_single_card():
    """Bez aktywnego efektu nic się nie zmienia: zwykłe dobranie 1 karty."""
    gm = GameMaster()
    p1, p2, p3 = three_players()
    state = GameState(
        deck=make_deck([card(Suit.HEART, Value.SEVEN)], [card(Suit.CLUBS, Value.EIGHT)]),
        players=[p1, p2, p3],
        current_player_index=1,
    )
    p2.hand = [card(Suit.DIAMOND, Value.SIX)]

    action = gm.process_turn(state)

    assert action == {"action": "draw_card"}
    assert len(p2.hand) == 2
    assert state.lucky_drawn is False


def test_lucky_play_is_labelled_play_card_for_logger():
    """GameState.annotate_action (logowanie do SQLite) ma klasyfikować zagraną
    szczęśliwą kartę (dobór + zagranie w jednej turze) jako play_card,
    a nie "blocked" (ręka bez zmiany długości)."""
    gm = GameMaster()
    p1, p2, p3 = three_players()
    state = GameState(
        deck=make_deck([card(Suit.HEART, Value.TWO)], [card(Suit.SPADES, Value.THREE)]),
        players=[p1, p2, p3],
        current_player_index=1,
        effect_active=True,
        cards_to_draw=2,
    )
    p2.hand = [card(Suit.CLUBS, Value.KING)]
    hand_before = list(p2.hand)

    gm.process_turn(state)
    state.annotate_action(hand_before)

    assert state.action == "play_card"
    assert state.last_affected_cards == [card(Suit.SPADES, Value.THREE)]
