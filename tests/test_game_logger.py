"""Testy GameLoggera: ręka "po ruchu" zawsze należy do gracza, który robił ruch.

Pre-istniejący bug: in_game_log_after liczył rękę jako
state.players[state.current_player_index - 1] -- po odwróceniu kierunku gry
(Król pik, turn_direction=-1) wskazywał INNEGO gracza i do bazy trafiała
ręka złej osoby (tworząc fałszywe dane dla EDA).
"""

import json
import sqlite3

from core.card import Suit, Value
from core.game_state import GameState
from core.macau_game import MacauGame
from tests.helpers import DummyPlayer, card, make_deck


def _logged_moves(tmp_path, database_factory, logger_factory, state, game):
    """Wykonuje jedną turę z pełnym logowaniem i zwraca wiersz moves z bazy."""
    logger = logger_factory
    logger.init_log(state)

    logger.in_game_log_before(state, move_num=1)
    hand_before = list(state.current_player.hand)
    game.game_master.process_turn(state)
    state.annotate_action(hand_before)
    logger.in_game_log_after(state)

    logger.endgame_log(winner_pos=None, total_moves=2)
    db_path = database_factory
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT action, hand_before, hand_after FROM moves ORDER BY move_num LIMIT 1"
    ).fetchone()
    conn.close()
    return row


def _fresh_stack(tmp_path):
    from database.database import MacauDatabase
    from logger.game_logger import GameLogger

    db_path = str(tmp_path / "logger.db")
    db = MacauDatabase(db_path)
    db.seed_cards()
    logger = GameLogger(db_instance=db)
    return db_path, db, logger


def test_hand_after_belongs_to_mover_with_reversed_direction(tmp_path):
    """P0 gra 9 kier przy odwróconym kierunku -- hand_after = [Król trefl].

    Stary kod: (0 - 1) wsteczne przejście wskazywałoby P2 (a ręka
    hand_after trafia do bazy z ręki P1/P2 w zależności od indeksu).
    """
    db_path, db, logger = _fresh_stack(tmp_path)

    players = [DummyPlayer("P0"), DummyPlayer("P1"), DummyPlayer("P2")]
    game = MacauGame(players=players, number_of_cards_per_player=1)
    state = GameState(
        deck=make_deck([card(Suit.HEART, Value.EIGHT)]),
        players=players,
        current_player_index=0,
        turn_direction=-1,  # gra wstecz -- tu stary kod się mylił
    )
    game.game_state = state
    players[0].hand = [card(Suit.HEART, Value.NINE), card(Suit.CLUBS, Value.KING)]
    players[1].hand = [card(Suit.SPADES, Value.QUEEN)]  # wyraźnie inna ręka
    players[2].hand = [card(Suit.DIAMOND, Value.SEVEN)]  # wyraźnie inna ręka

    row = _logged_moves(tmp_path, db_path, logger, state, game)
    db.close()

    action, hand_before_str, hand_after_str = row
    assert action == "play_card"
    assert json.loads(hand_before_str) == ["NINE_HEART", "KING_CLUBS"]
    # ręką po ruchu jest ręka P0 (został Krol Trefl), nie P1/P2
    assert json.loads(hand_after_str) == ["KING_CLUBS"]


def test_hand_after_belongs_to_mover_on_draw_reversed(tmp_path):
    """P0 nie ma zagrania, dobiera -- hand_after to ręka P0 (dobrana karta)."""
    db_path, db, logger = _fresh_stack(tmp_path)

    players = [DummyPlayer("P0"), DummyPlayer("P1"), DummyPlayer("P2")]
    game = MacauGame(players=players, number_of_cards_per_player=1)
    state = GameState(
        deck=make_deck([card(Suit.HEART, Value.EIGHT)],
                       [card(Suit.DIAMOND, Value.SEVEN)]),
        players=players,
        current_player_index=0,
        turn_direction=-1,
    )
    game.game_state = state
    players[0].hand = [card(Suit.SPADES, Value.KING)]  # nie pasuje do 8 kier
    players[1].hand = [card(Suit.SPADES, Value.QUEEN)]
    players[2].hand = [card(Suit.CLUBS, Value.TEN)]

    row = _logged_moves(tmp_path, db_path, logger, state, game)
    db.close()

    action, hand_before_str, hand_after_str = row
    assert action == "draw_card"
    assert json.loads(hand_before_str) == ["KING_SPADES"]
    # P0 dobrał 7 karo: ręka po ruchu = [K pik, 7 karo] -- starego bonusu indeks-1 tu nie ma
    assert json.loads(hand_after_str) == ["KING_SPADES", "SEVEN_DIAMOND"]


def test_action_label_uses_moving_players_hand(tmp_path):
    """Etykieta akcji liczona z ręki gracza ruchu, nie następnego gracza.

    Pre-istniejący bug (integracyjny): annotate_action czytał rękę
    "biežącego" gracza PO advance tury -- czyli następnego gracza.
    Przy różnej wielkości rąk etykiety były losowe (np. zwykłe zagranie
    z graczem o większej ręce dalej zapisane jako draw_more_cards).
    """
    db_path, db, logger = _fresh_stack(tmp_path)

    players = [DummyPlayer("P0"), DummyPlayer("P1"), DummyPlayer("P2")]
    game = MacauGame(players=players, number_of_cards_per_player=1)
    state = GameState(
        deck=make_deck([card(Suit.HEART, Value.EIGHT)]),
        players=players,
        current_player_index=0,  # kierunek +1 -- po P0 tura idzie na P1
    )
    game.game_state = state
    # P0 ma 5 kart i zagra 9 kier (zostanie 4): zwykłe zagranie
    players[0].hand = [card(Suit.HEART, Value.NINE),
                       card(Suit.CLUBS, Value.KING),
                       card(Suit.DIAMOND, Value.FIVE),
                       card(Suit.CLUBS, Value.SEVEN),
                       card(Suit.SPADES, Value.TEN)]
    # P1 (NASTĘPNY gracz) ma dużo większą rękę: stare porównanie 5-vs-8
    # oznaczałoby akcję jako "draw_more_cards" (fałsz)
    players[1].hand = [card(Suit.SPADES, Value.JACK), card(Suit.CLUBS, Value.JACK),
                       card(Suit.HEART, Value.SEVEN), card(Suit.CLUBS, Value.EIGHT),
                       card(Suit.HEART, Value.SIX), card(Suit.DIAMOND, Value.SIX),
                       card(Suit.SPADES, Value.SIX), card(Suit.SPADES, Value.NINE)]
    players[2].hand = [card(Suit.HEART, Value.FIVE)]

    row = _logged_moves(tmp_path, db_path, logger, state, game)
    db.close()

    action, hand_before_str, hand_after_str = row
    assert action == "play_card"  # P0 zagrał kartę (5 -> 4); NIE draw_more_cards
    assert len(json.loads(hand_after_str)) == 4  # ręka P0 po zagrania, nie P1 (8)
