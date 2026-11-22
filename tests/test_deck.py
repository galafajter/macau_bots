"""Testy talii (Deck): unikalność po tasowaniu, determinizm, mechanika doboru.

UWAGA: Deck.draw_from_deck pobiera kartę z KOŃCA listy drawing_cards;
przy pustej tali doboru przetasowuje stos (z wyłączeniem wierzchniej karty),
a przy stosie <= 1 zwraca False -- to wyżej opisany mechanizm stojący za
"patem" silnika (zob. test_draw_returns_false_when_deck_exhausted).
"""

import random
from itertools import product

from core.card import Deck, Suit, Value
from tests.helpers import card, make_deck

ALL_52 = {(suit, value) for suit, value in product(Suit, Value)}


def test_deck_starts_with_52_cards_without_duplicates():
    """Po tasowaniu: dokładnie 52 unikalne karty (niezależnie od seeda)."""
    for seed in range(10):
        random.seed(seed)
        deck = Deck()

        assert len(deck.drawing_cards) == 52, f"seed={seed}"
        suits_values = {(c.suit, c.value) for c in deck.drawing_cards}
        assert len(suits_values) == 52, f"seed={seed}: duplikaty po tasowaniu"
        assert suits_values == ALL_52, f"seed={seed}: brakujące karty"


def test_same_seed_gives_same_deck_order():
    """Determinizm: ten sam random.seed => identyczna kolejność tasowania."""
    random.seed(2024)
    deck1 = Deck()
    random.seed(2024)
    deck2 = Deck()

    order1 = [(c.suit, c.value) for c in deck1.drawing_cards]
    order2 = [(c.suit, c.value) for c in deck2.drawing_cards]

    assert order1 == order2


def test_different_seeds_give_different_deck_orders():
    random.seed(1)
    deck1 = Deck()
    random.seed(2)
    deck2 = Deck()

    order1 = [(c.suit, c.value) for c in deck1.drawing_cards]
    order2 = [(c.suit, c.value) for c in deck2.drawing_cards]

    assert order1 != order2


def test_draw_from_deck_pops_from_end_of_list():
    """Kontrakt doboru: karta przychodzi z KONCA listy drawing_cards."""
    deck = make_deck([card(Suit.DIAMOND, Value.FIVE)],
                     [card(Suit.CLUBS, Value.SEVEN), card(Suit.HEART, Value.NINE)])

    drawn = deck.draw_from_deck()

    assert drawn == card(Suit.HEART, Value.NINE)
    assert deck.drawing_cards == [card(Suit.CLUBS, Value.SEVEN)]


def test_reshuffle_takes_stack_except_top_card():
    """Pusta talia doboru: stos (poza wierzchnią kartą) wraca do gry."""
    stack_top = card(Suit.HEART, Value.SEVEN)
    stack_lower = card(Suit.CLUBS, Value.TWO)
    deck = make_deck([stack_lower, stack_top], drawing_cards=[])  # top = ostatnia karta listy

    drawn = deck.draw_from_deck()  # wymusza przet tasowanie stosu (poza wierzchnią)

    assert deck.top_stack_card == stack_top  # wierzchnia karta pozostała na stosie
    assert drawn == stack_lower  # dobrana została niższa karta stosu
    assert deck.drawing_cards == []
    assert len(deck.stack_of_placed_cards) == 1


def test_draw_returns_false_when_deck_exhausted():
    """Dokumentacja obecnego mechanizmu wyczerpania (pat silnika!):
    pusta talia + stos 1 karta => brak doboru (False)."""
    deck = make_deck([card(Suit.HEART, Value.SEVEN)], drawing_cards=[])

    assert deck.draw_from_deck() is False
    assert deck.top_stack_card == card(Suit.HEART, Value.SEVEN)


def test_top_stack_card_is_last_put():
    deck = make_deck([], [card(Suit.DIAMOND, Value.TEN)])
    deck.put_on_stack(card(Suit.SPADES, Value.SIX))
    deck.put_on_stack(card(Suit.CLUBS, Value.KING))

    assert deck.top_stack_card == card(Suit.CLUBS, Value.KING)
