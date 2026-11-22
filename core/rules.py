"""
Jedno źródło prawdy o klasyfikacji kart w Makao.

Karty funkcyjne (z efektami):
- 2, 3        -- wojna (kara dobierania, kumuluje się),
- 4           -- blokada następnej tury (obrona: 4 lub Dama),
- Walet (J)   -- żądanie wartości nie-funkcyjnej,
- Dama (Q)    -- karta "wszystko", niweluje aktywny efekt,
- Król Kier/Pik -- wojna +5 (Król Karo/Trefl są pasywne),
- As (A)      -- żądanie koloru.

Karty pasywne: 5-10 oraz Król Karo/Trefl.

Moduł jest wyłącznym miejscem, w którym definiuje się, które karty
są funkcyjne/pasywne. GameMaster, gracze i rozdanie pierwszej karty
korzystają z tych helperów -- aby dodać nowe zasady, zmienia się je tutaj.
"""

from core.card import Card, Suit, Value
from typing import List

# Tylko Króle w tych kolorach mają efekt wojny; pozostali Królowie są pasywni.
KING_WAR_SUITS: tuple[Suit, ...] = (Suit.HEART, Suit.SPADES)

FUNCTIONAL_VALUES: tuple[Value, ...] = (
    Value.TWO,
    Value.THREE,
    Value.FOUR,
    Value.JACK,
    Value.QUEEN,
    Value.KING,
    Value.ACE,
)

NONFUNCTIONAL_VALUES: tuple[Value, ...] = (
    Value.FIVE,
    Value.SIX,
    Value.SEVEN,
    Value.EIGHT,
    Value.NINE,
    Value.TEN,
)


def functional_cards() -> List[Card]:
    """Karty z efektami: 2, 3, 4, J, Q, K, A (28) bez pasywnych Króli Karo/Trefl (26)."""
    return [
        Card(suit, value, effect=None)
        for suit in Suit
        for value in FUNCTIONAL_VALUES
        if not (value == Value.KING and suit not in KING_WAR_SUITS)
    ]


def nonfunctional_cards() -> List[Card]:
    """Karty pasywne: 5-10 (24) plus pasywni Królowie Karo/Trefl (razem 26)."""
    cards: List[Card] = [
        Card(suit, value, effect=None)
        for suit in Suit
        for value in NONFUNCTIONAL_VALUES
    ]
    cards.extend(
        Card(suit, Value.KING, effect=None)
        for suit in Suit
        if suit not in KING_WAR_SUITS
    )
    return cards


def all_cards() -> List[Card]:
    """Pełna talia 52 kart."""
    return functional_cards() + nonfunctional_cards()


def is_functional(card: Card) -> bool:
    """Czy karta ma efekt (wchodzi w grę zasad GameMastera)?"""
    if card.value not in FUNCTIONAL_VALUES:
        return False
    return not (card.value == Value.KING and card.suit not in KING_WAR_SUITS)


def is_first_card_allowed(card: Card) -> bool:
    """Pierwsza karta na stosie musi być pasywna (bez efektu)."""
    return not is_functional(card)
