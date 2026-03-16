from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List
from itertools import product
import random

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


@dataclass
class Effect:
    war: bool = False
    block: bool = False
    demand_value: bool = False
    demand_suit: bool = None


class Card:
    def __init__(self, suit, value, effect):
        self.suit: Suit = suit
        self.value: Value = value
        # self.effect: Effect = effect

    def __eq__(self, other):
        return self.value == other.value and self.suit == other.suit

    def __hash__(self):
        return hash((self.suit, self.value))

    def __str__(self):
        return f"{self.value.value} {self.suit.value}"

    def __repr__(self):
        return f"{self.value.value} {self.suit.value}"


class Deck:
    def __init__(self):
        self.drawing_cards: List[Card] = []
        self.stack_of_placed_cards: List[Card] = []
        self.__init_deck()
        self.shuffle()

    def __str__(self):
        return f'{self.drawing_cards}'

    def __repr__(self):
        return f'{self.drawing_cards}'

    def __len__(self):
        return len(self.drawing_cards)

    def __init_deck(self):
        for card in product(Suit, Value):
            effect = check_effect(card[0])
            self.drawing_cards.append(Card(*card, effect))

    @property
    def top_stack_card(self):
        return self.stack_of_placed_cards[-1]

    def reinit_deck(self, cards: List[Card]):
        self.drawing_cards.extend(cards)
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.drawing_cards)

    def put_on_stack(self, card: Card):
        self.stack_of_placed_cards.append(card)

    def draw_from_deck(self):
        """
        Method from drawing a card from deck. It also checks if there are drawing_cards to draw from. If there is not it
        shuffles the discarded drawing_cards and adds them back to the deck.
        """

        if len(self.drawing_cards) == 0:
            if len(self.stack_of_placed_cards) == 0:
                # IF there is no drawing_cards to draw from AND also no drawing_cards on stack_of_placed_cards to take skip turn
                # TODO is this condition even possible? Probably it is; How often would that occur?
                return False
            else:
                # IF there is no drawing_cards than take all cards from placed cards except top card, shuffle them and add to drawing_cards
                cards_to_reshuffle = self.stack_of_placed_cards[:-1]
                self.stack_of_placed_cards = self.stack_of_placed_cards[-1:]
                self.reinit_deck(cards_to_reshuffle)
                return self.drawing_cards.pop()
        else:
            return self.drawing_cards.pop()


def check_effect(*args) -> Effect:
    ...