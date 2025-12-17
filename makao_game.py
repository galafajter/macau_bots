import random
import time
from abc import abstractmethod
from enum import Enum
from itertools import product, cycle
from typing import List, Optional


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

    @staticmethod
    @abstractmethod
    def has_effect():
        return NotImplemented

class WarEffect(Effect):
    CARDS_VALUES = {
            Value.TWO: 2,
            Value.THREE: 3,
            Value.KING: 5,
        }

    def __init__(self):
        super().__init__()
        
        

    @staticmethod
    def has_effect():
        return True

class BlockEffect(Effect):
    def __init__(self):
        super().__init__()

    @staticmethod
    def has_effect():
        return True

class DemandValueEffect(Effect):
    def __init__(self):
        super().__init__()

    @staticmethod
    def has_effect():
        return True

class DemandSuitEffect(Effect):
    def __init__(self):
        super().__init__()

    @staticmethod
    def has_effect():
        return True

class SkipEffect(Effect):
    def __init__(self):
        super().__init__()

    @staticmethod
    def has_effect():
        return True

class NoneEffect(Effect):
    def __init__(self):
        super().__init__()

    @staticmethod
    def has_effect():
        return False

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

    def __str__(self):
        return f'{self.cards}'

    def __repr__(self):
        return f'{self.cards}'

    def __len__(self):
        return len(self.cards)

    def __init_deck(self):

        for card in product(Suit, Value):
            effect = check_effect(card[0])
            self.cards.append(Card(*card, effect))

    def reinit_deck(self, cards: List[Card]):
        self.cards.extend(cards)
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()

class Player:
    def __init__(self, hand: List[Card]):
        self.hand: List[Card] = hand
        self.name = None # TODO do this in a proper way

    def __str__(self):
        return f"Player: {self.name}"

    def __repr__(self):
        return f"Player: {self.name}"

    def draw_card(self, card: Card):
        self.hand.append(card)

    def make_move(self, top_card):
        """
        Method that implements strategy of a player.

        Currently, it is basic strategy - throw first fitting card that you see.
        """
        # TODO somehow put RL bot here
        for card in self.hand:
            if (card.suit.value == top_card.suit.value) or (card.value.value == top_card.value.value):
                return self.play_card(card)
        else:
            return None

    ###### REFACTOR
    def make_demand_move(self, demand_type, demanded_value_suit):
        if demand_type == 'suit':
            for card in self.hand:
                if card.suit == demanded_value_suit:
                    return self.play_card(card)
            else:
                return None
        elif demand_type == 'value':
            for card in self.hand:
                if card.value == demanded_value_suit:
                    return self.play_card(card)
            else:
                return None

    ######
    def play_card(self, card: Card):
        if card in self.hand:
            self.hand.remove(card)
            return card


class MacauGame:

    NUMBER_OF_CARDS_PER_PLAYER = 5
    def __init__(self, players_num: int):
        self.players_num: int = players_num
        assert players_num >= 2, "Not enough players"
        self.deck: Deck = Deck()
        self.stack: List[Card] = []

        cards_to_deal, first_card = self.__deal_cards()

        self.stack.append(first_card)

        # deal cards to the moment when passive card is on the table
        while check_effect(first_card.value).has_effect():
            first_card = self.deck.deal()
            self.stack.append(first_card)

        self.players: List[Player] = [Player(player_cards) for player_cards in cards_to_deal]
        players_names = [str(i) for i in range(self.players_num)]
        for i, name in enumerate(players_names):
            self.players[i].name = name


    def __deal_cards(self):
        cards_to_deal = self.NUMBER_OF_CARDS_PER_PLAYER * self.players_num

        # TODO adjusting number of decks based on `players_number`
        if cards_to_deal > len(self.deck.cards):
            raise ValueError("Too much players for one deck")

        cards_for_players: List[List[Card]] = [[] for _ in range(self.players_num)]

        for i in range(cards_to_deal):
            cards_for_players[i % self.players_num].append(self.deck.deal())

        first_card: Card = self.deck.deal()

        return cards_for_players, first_card

    def check_if_reshuffle_is_needed(self, number_of_cards_needed):
        # IF there is no cards to draw from THAN get all cards from stack except top card
        # IF there is no cards to draw from AND also no cards on stack to take skip turn
        # TODO is above condition even possible? Probably it is; How often would that occur?
        if len(self.deck) == number_of_cards_needed:
            if self.stack == 0:
                return None
            else:
                cards_to_reshuffle = self.stack[:-1]
                self.stack = self.stack[-1:]
                self.deck.reinit_deck(cards_to_reshuffle)
                return True
        else:
            return False

    @property
    def top_card(self):
        return self.stack[-1]


    def play(self):
        ###### REFACTOR
        # effect = None
        #
        # demand_value_active = False
        # demand_value_counter = 0
        # demand_value = None
        #
        # demand_suit_active = False
        # demand_suit_counter = 0
        # demand_suit = None
        ######
        for player in cycle(self.players):

            print(f'Player {player.name} hand before move: {player.hand}, top card {self.top_card}')
            ###### REFACTOR
            # if demand_value_active:
            #     player.make_demand_move('value', demand_value)
            #     if demand_value_counter == self.players_num:
            #         demand_value_active = False
            #     else:
            #         demand_value_counter += 1
            #
            # elif demand_suit_active:
            #     player.make_demand_move('suit', demand_suit)
            #     if demand_suit_counter == self.players_num:
            #         demand_suit_active = False
            #     else:
            #         demand_suit_counter += 1
            ######
            # condition for situation when there are no cards to draw from
            if self.check_if_reshuffle_is_needed(0) is None:
                continue

            # if len(self.deck) == 0:
            #     if self.stack == 0:
            #         continue
            #     else:
            #         cards_to_reshuffle = self.stack[:-1]
            #         self.stack = self.stack[-1:]
            #         self.deck.reinit_deck(cards_to_reshuffle)


            player_move = player.make_move(self.top_card)
            # TODO add rule of 'lucky card' - first drawn card can be thrown if it fits

            if player_move is None:
                player.draw_card(self.deck.deal())
            else:
                self.stack.append(player_move)
                # effect = check_effect(player_move.value)
            ###### REFACTOR
            # if effect is not None:
            #
            #     if effect == WarEffect:
            #         number_of_cards_to_draw = WarEffect.CARDS_VALUES[self.top_card.value]
            #
            #         self.check_if_reshuffle_is_needed(number_of_cards_to_draw)
            #
            #         for _ in range(number_of_cards_to_draw):
            #             player.draw_card(self.deck.deal())
            #
            #     elif effect == BlockEffect:
            #         continue
            #
            #     elif effect == DemandSuitEffect:
            #         demand_suit_active = True
            #         demand_suit_counter = 0
            #         demand_suit = random.choice(list(Suit))
            #         print(f'Demanded suit is {demand_suit}')
            #
            #     elif effect == DemandValueEffect:
            #         demand_value_active = True
            #         demand_value_counter = 0
            #         demand_value = random.choice(list(Value))
            #         print(f'Demanded value is {demand_value}')
            #
            #     elif effect == SkipEffect:
            #         ...  # TODO think about Queen behaviour
            #
            #     effect = None
            ######
            print(f'Player {player.name} hand after move: {player.hand}, top card {self.top_card}')

            if len(player.hand) == 0:
                print(f"Player {player.name} won!")
                break

            # time.sleep(5)


if __name__ == "__main__":
    game = MacauGame(players_num=3)
    game.play()
