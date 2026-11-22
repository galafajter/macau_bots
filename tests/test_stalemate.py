"""Testy pat-guardu: partia nigdy nie wisi w nieskończoność.

Pat = talia doboru pusta, stos ma 1 kartę, nikt nie ma legalnego ruchu
i w silniku nie wisi nic, co samo wygaśnie (blokady/wojny/żądania).
Wtedy gra kończy się wynikiem "stalemate" i Zwykle poprawnym zapisem
w bazie (wiersz games z winner=NULL i pełnymi ruchami).
"""

import sqlite3

from core.card import Suit, Value
from core.game_state import GameState
from core.makao_game import MacauGame
from tests.helpers import DummyPlayer, NullLogger, card, make_deck


def craft_game(hands, stack_top, current_player_index=0, **state_kwargs):
    """MacauGame ze w pełni kontrolowanym stanem (bez rozdania)."""
    players = [DummyPlayer(f"P{i}") for i in range(len(hands))]
    game = MacauGame(players=players, number_of_cards_per_player=1)
    game.game_state = GameState(
        deck=make_deck([stack_top], drawing_cards=[]),
        players=players,
        current_player_index=current_player_index,
        **state_kwargs,
    )
    for player, hand in zip(players, hands):
        player.hand = list(hand)
    return game, players


def test_stalemate_when_noone_can_play_or_draw():
    # stos: 7 pika; ręce bez siódemki, bez pika i bez damy -> nikt nie zagra
    game, players = craft_game(
        hands=[[card(Suit.DIAMOND, Value.NINE), card(Suit.DIAMOND, Value.TEN)],
               [card(Suit.DIAMOND, Value.EIGHT)],
               [card(Suit.CLUBS, Value.SIX)]],
        stack_top=card(Suit.SPADES, Value.SEVEN),
    )

    result = game.play(NullLogger())

    assert result == "stalemate"
    assert [len(p.hand) for p in players] == [2, 1, 1]  # ręce nietknięte


def test_game_continues_when_someone_can_play():
    # P0 ma siódemkę (wartość pasuje do 7 pika), potem 5 karo (kolor do 7 karo);
    # ręce przeciwników nie pasują ani do 7 pika, ani do 7 karo
    game, players = craft_game(
        hands=[[card(Suit.DIAMOND, Value.SEVEN), card(Suit.DIAMOND, Value.FIVE)],
               [card(Suit.CLUBS, Value.EIGHT)],
               [card(Suit.CLUBS, Value.SIX)]],
        stack_top=card(Suit.SPADES, Value.SEVEN),
    )

    result = game.play(NullLogger())

    assert result == "P0"  # P0 wygrywa, pat nie pada
    assert len(players[0].hand) == 0


def test_player_blocked_with_matching_card_does_not_trigger_stalemate():
    """Gracz w pauzie po 4 z pasującą kartą -- pat-mus czeka aż pauza minie.

    P0 zostaje zablokowany na 1 turę, ale trzyma 6 trefl (pasuje kolorem do
    6 pika na stosie) -- po pauzie gra go i wygrywa.
    """
    game, players = craft_game(
        hands=[[card(Suit.SPADES, Value.SIX)],
               [card(Suit.DIAMOND, Value.NINE)],
               [card(Suit.CLUBS, Value.TEN)]],
        stack_top=card(Suit.SPADES, Value.FOUR),
        current_player_index=1,          # to P1 nie może się obronić
        effect_active=True,
        block_count=1,
    )

    result = game.play(NullLogger())

    # pauza P1 mija; P0 na swej turze miał jedyną legalną kartę (6 trefl)
    # -- pat-guard czekał, gra miała postęp, P0 wygrywa
    assert result == "P0"
    assert len(players[0].hand) == 0


def test_pending_war_expires_into_stalemate():
    """Wojna przy wyczerpanej talii: brak odpowiedzi, kary się nie dają dociągnąć
    -- efekt wygasa i dopiero wtedy pada pat."""
    game, players = craft_game(
        hands=[[card(Suit.CLUBS, Value.SIX)],
               [card(Suit.DIAMOND, Value.TEN)],
               [card(Suit.CLUBS, Value.NINE)]],
        stack_top=card(Suit.HEART, Value.TWO),
        effect_active=True,
        cards_to_draw=2,
    )

    result = game.play(NullLogger())

    assert result == "stalemate"


def test_stalemate_is_fully_logged_to_database(tmp_path):
    """Pat ma komplet danych w SQLite: moves zapisane, winner=NULL."""
    from database.database import MacauDatabase
    from logger.game_logger import GameLogger

    db_path = str(tmp_path / "stalemate.db")
    db = MacauDatabase(db_path)
    db.seed_cards()
    logger = GameLogger(db_instance=db)

    game, players = craft_game(
        hands=[[card(Suit.DIAMOND, Value.NINE)],
               [card(Suit.DIAMOND, Value.EIGHT)],
               [card(Suit.CLUBS, Value.SIX)]],
        stack_top=card(Suit.SPADES, Value.SEVEN),
    )

    result = game.play(logger)
    db.close()

    assert result == "stalemate"

    conn = sqlite3.connect(db_path)
    games_row = conn.execute(
        "SELECT id, winner, total_moves FROM games").fetchall()
    assert len(games_row) == 1
    game_id, winner, total_moves = games_row[0]
    assert winner is None                    # pat bez zwycięzcy
    assert total_moves > 0
    moves_count = conn.execute(
        "SELECT COUNT(*) FROM moves WHERE game_id = ?", (game_id,)).fetchone()[0]
    assert moves_count > 0                   # ruchy zapisane (stary "error" tego nie robił)
    conn.close()
