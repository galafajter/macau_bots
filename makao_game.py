import random
from enum import Enum
from itertools import product
from typing import List


class Suit(Enum):
    HEART = "Heart"
    DIAMOND = "Diamond"
    CLUBS = "Clubs"
    SPADES = "Spades"


class Value(Enum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"


# TODO think about Enum Effect instead of class
class Effect:
    def __init__(self):
        ...


class WarEffect(Effect):
    def __init__(self):
        super().__init__()


class BlockEffect(Effect):
    def __init__(self):
        super().__init__()


class DemandValueEffect(Effect):
    def __init__(self):
        super().__init__()


class DemandSuitEffect(Effect):
    def __init__(self):
        super().__init__()


class SkipEffect(Effect):
    def __init__(self):
        super().__init__()


class NoneEffect(Effect):
    def __init__(self):
        super().__init__()


class Card:
    def __init__(self, suit, value, effect):
        self.suit: Suit = suit
        self.value: Value = value
        self.effect: Effect = effect

    def __str__(self):
        return f"{self.value.value} {self.suit.value}"

    def __repr__(self):
        return f"{self.value.value} {self.suit.value}"


def check_effect(card_value: Value):
    if card_value in [Value.TWO, Value.THREE, Value.KING]:
        return WarEffect()
    elif card_value == Value.FOUR:
        return BlockEffect()
    elif card_value == Value.JACK:
        return DemandValueEffect()
    elif card_value == Value.QUEEN:
        return SkipEffect()
    elif card_value == Value.ACE:
        return DemandSuitEffect()
    else:
        return NoneEffect()

class Deck:
    def __init__(self):
        self.cards: List[Card] = []
        self.__init_deck()
        self.shuffle()

    def __init_deck(self):

        for card in product(Value, Suit):
            effect = check_effect(card[0])
            self.cards.append(Card(*card, effect))

    @property
    def top_card(self):
        return self.cards[-1]

    def shuffle(self):
        random.shuffle(self.cards)

class Player:
    def __init__(self, hand: List[Card], name: str):
        self.hand: List[Card] = hand
        self.name: str = name

    def __str__(self):
        return f"Player: {self.name}"

    def __repr__(self):
        return f"Player: {self.name}"

    def draw_card(self, card: Card):
        self.hand.append(card)

    def make_move(self, top_card):
        """Method that implements strategy of a player"""
        for card in self.hand:
            if (card.suit == top_card.suit) or (card.value == top_card.value):
                return self.play_card(card)
        else:
            return None

    def play_card(self, card: Card):
        if card in self.hand:
            return self.hand.remove(card)


class MacauGame:

    NUMBER_OF_CARDS_PER_PLAYER = 5
    def __init__(self, players_num: int):
        self.players_num: int = players_num
        self.deck: Deck = Deck()
        self.stack: List[Card] = []

        self.players: List[Player] = []

    def __deal_cards(self):
        cards_to_deal = self.NUMBER_OF_CARDS_PER_PLAYER * self.players_num

        cards_for_players: List[List[Card]] = [[] for _ in range(self.players_num)]

        for _ in range(cards_to_deal):





if __name__ == "__main__":
    ...
