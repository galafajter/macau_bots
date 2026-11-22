"""Deterministyczne scenariusze na poziomie PARTII.

1) Odtwarzalność: ten sam seed => identyczny przebieg i wynik partii.
2) Pierwsza karta na stosie jest zawsze pasywna (reguła z core/rules.py).
"""

import random

import pytest

from core import rules
from core.macau_game import MacauGame
from core.player import AggressivePlayer, CautiousPlayer, RandomPlayer
from tests.helpers import DummyPlayer, NullLogger


def _run_game(seed: int):
    """Partia z logowaniem-pustką; zwraca pełny "odcisk palca" końcowego stanu."""
    random.seed(seed)
    players = [RandomPlayer("R"), AggressivePlayer("A"), CautiousPlayer("C")]
    game = MacauGame(players=players, number_of_cards_per_player=5)
    winner = game.play(NullLogger())
    state = game.game_state

    return {
        "winner": winner,
        "drawing": [str(c) for c in state.deck.drawing_cards],
        "stack": [str(c) for c in state.deck.stack_of_placed_cards],
        "hands": [[str(c) for c in p.hand] for p in state.players],
        "pending": (state.cards_to_draw, state.block_count, str(state.demanded_value),
                    str(state.demanded_suit), state.demand_turns_left),
    }


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 5, 8, 13, 21, 34, 55])
def test_same_seed_replays_identical_game(seed):
    """random.seed w pełni determinuje rozdanie, ruchy botów i wynik."""
    run1 = _run_game(seed)
    run2 = _run_game(seed)

    assert run1 == run2, f"seed={seed}: partia nie jest odtwarzalna"


@pytest.mark.parametrize("seed", range(50))
def test_first_card_on_stack_is_never_functional(seed):
    """Wierzchnia karta otwierająca partię zawsze pasywna (core/rules)."""
    random.seed(seed)
    players = [RandomPlayer("R"), AggressivePlayer("A"), CautiousPlayer("C")]
    game = MacauGame(players=players, number_of_cards_per_player=5)

    first = game.game_state.deck.top_stack_card

    assert rules.is_first_card_allowed(first), f"seed={seed}: pierwsza karta {first}"


def test_manual_deck_yields_deterministic_game():
    """Scenariusz "golden": kontrolana talia doboru dająca zaplanowane zakończenie."""
    random.seed(7)
    p1 = DummyPlayer("D1")
    p2 = DummyPlayer("D2")
    p3 = DummyPlayer("D3")
    game = MacauGame(players=[p1, p2, p3], number_of_cards_per_player=1)
    state = game.game_state

    # ręcznie: każdy gracz zostaje z jedną pasywną kartą pasującą do wierzchniej,
    # wygrywa ten, kto zagra pierwszy
    top = state.deck.top_stack_card
    for player in state.players:
        matching = rules.nonfunctional_cards()
        player.hand = [card for card in matching if card != top][:1]
    p1.hand = [card for card in rules.nonfunctional_cards()
               if card.value == top.value or card.suit == top.suit][:1]

    winner = game.play(NullLogger())

    assert winner == "D1"  # DummyPlayer natychmiast zagra jedyną legalną kartę
    assert len(p1.hand) == 0
