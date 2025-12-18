import random
import time
from abc import abstractmethod
from enum import Enum
from itertools import product, cycle
from typing import List, Optional

random.seed(123)

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

    def reinit_deck(self, cards: List[Card]):
        self.drawing_cards.extend(cards)
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.drawing_cards)

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

# TODO refactor idea: make Turn class that will be created in every turn saving data from it
# TODO refactor idea: the Turn class can also check if action drawing_cards were played

class MacauGame:

    NUMBER_OF_CARDS_PER_PLAYER = 5
    def __init__(self, players_num: int):
        self.players_num: int = players_num
        assert players_num >= 2, "Not enough players"
        self.deck: Deck = Deck()

        cards_to_deal, first_card = self.__deal_cards()

        self.deck.stack_of_placed_cards.append(first_card)

        # deal drawing_cards to the moment when passive card is on the table
        while check_effect(first_card.value).has_effect():
            first_card = self.deck.draw_from_deck()


        self.players: List[Player] = [Player(player_cards) for player_cards in cards_to_deal]
        players_names = [str(i) for i in range(self.players_num)]
        for i, name in enumerate(players_names):
            self.players[i].name = name


    def __deal_cards(self):
        cards_to_deal = self.NUMBER_OF_CARDS_PER_PLAYER * self.players_num

        # TODO adjusting number of decks based on `players_number`
        if cards_to_deal > len(self.deck.drawing_cards):
            raise ValueError("Too much players for one deck")

        cards_for_players: List[List[Card]] = [[] for _ in range(self.players_num)]

        for i in range(cards_to_deal):
            cards_for_players[i % self.players_num].append(self.deck.draw_from_deck())

        first_card: Card = self.deck.draw_from_deck()

        return cards_for_players, first_card


    @property
    def top_card(self):
        return self.deck.stack_of_placed_cards[-1]


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





            player_move = player.make_move(self.top_card)
            # TODO add rule of 'lucky card' - first drawn card can be thrown if it fits

            if player_move is None:
                player.draw_card(self.deck.draw_from_deck())
            else:
                self.deck.stack_of_placed_cards.append(player_move)
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
