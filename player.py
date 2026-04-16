from abc import abstractmethod, ABC

from card import Card, Value, Suit
from typing import List, Optional
import random


class Player(ABC):
    def __init__(self, name: str):
        self.name = name
        self.hand: List[Card] = []
        self.playable_hand: List[Card] = []

    def __str__(self):
        return f"{self.__class__.__name__}: {self.name}"

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.name}"

    def draw_card(self, card: Card):
        self.hand.append(card)

    def evaluate_hand_for_playable_cards(self, playable_cards: List[Card]):
        """Choose cards that player can throw on top_stack_card"""
        self.playable_hand = []

        for card in self.hand:
            if card in playable_cards:
                self.playable_hand.append(card)

    @staticmethod
    def make_value_demand() -> Value:
        return random.choice([Value.FIVE, Value.SIX, Value.SEVEN, Value.EIGHT, Value.NINE, Value.TEN])

    @staticmethod
    def make_suit_demand() -> Suit:
        return random.choice(list(Suit))

    def play_card(self, card: Card) -> Optional[Card]:
        if card in self.hand:
            self.hand.remove(card)
            return card
        else:
            return None

    @abstractmethod
    def make_move(self) -> Optional[Card]:
        """
        Method that implements strategy of a player.

        Currently, it is basic strategy - throw first fitting card that you see.
        """
        raise NotImplementedError


class RandomPlayer(Player):
    """
    Class that implements a player who makes random moves.
    """
    def __init__(self, name):
        super().__init__(name)


    def make_move(self) -> Optional[Card]:

        if not self.playable_hand:
            return None
        
        return self.play_card(random.choice(self.playable_hand))


class AggressivePlayer(Player):
    """
    Class that implements a player who uses cards with effects only if he has them.
    """

    def __init__(self, name):
        super().__init__(name)
        # TODO should I consider queen in this list? # TODO refactor using a dict?
        self.first_cards_to_throw: List[Value] = [Value.ACE, Value.TWO, Value.THREE, Value.FOUR, Value.JACK, Value.QUEEN, Value.KING]


    def make_move(self) -> Optional[Card]:
        """
        Method that implements strategy of a player.
        """
        if not self.playable_hand:
            return None

        for val in self.first_cards_to_throw:
            matching_cards = list(filter(lambda cls: cls.value == val, self.playable_hand))
            if matching_cards:
                return self.play_card(matching_cards[0])

        return self.play_card(random.choice(self.playable_hand))



class CautiousPlayer(Player):
    """
    Class that implements a player who keeps cards with effects to the end.
    """

    def __init__(self, name):
        super().__init__(name)
        self.first_cards_to_throw: List[Value] = [Value.FIVE, Value.SIX, Value.SEVEN, Value.EIGHT, Value.NINE, Value.TEN]

    def make_move(self) -> Optional[Card]:
        """
        Method that implements strategy of a player.
        """
        if not self.playable_hand:
            return None

        for val in self.first_cards_to_throw:
            matching_cards = list(filter(lambda cls: cls.value == val, self.playable_hand))
            if matching_cards:
                return self.play_card(matching_cards[0])

        return self.play_card(random.choice(self.playable_hand))


class RLPlayer(Player):

    def __init__(self, name):
        super().__init__(name)
        self._pending_action: int = 0

    def set_action(self, action: int):
        self._pending_action = action

    def make_move(self) -> Optional[Card]:

        if not self.playable_hand or self._pending_action >= len(self.playable_hand):
            return None
        return self.play_card(self.playable_hand[self._pending_action])


class MCTSPlayer(Player):
    """
    Class that implements Monte Carlo Search Trees strategy.
    """
    def __init__(self, name):
        super().__init__(name)
        pass

    def make_move(self) -> Optional[Card]:
        pass


