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
        # TODO refactor using a dict?
        self.aggressive_cards: List[Card] = [Card(s, v, effect=None) for s in Suit for v in (Value.TWO, Value.THREE,
                                                                                             Value.FOUR, Value.JACK,
                                                                                             Value.QUEEN, Value.KING,
                                                                                             Value.ACE)]
        self.aggressive_cards.remove(Card(suit=Suit.CLUBS, value=Value.KING, effect=None))
        self.aggressive_cards.remove(Card(suit=Suit.DIAMOND, value=Value.KING, effect=None))


    def make_move(self) -> Optional[Card]:
        """
        Method that implements strategy of a player.
        """
        if not self.playable_hand:
            return None

        matching_aggressive_cards = [c for c in self.playable_hand if c in self.aggressive_cards]
        if matching_aggressive_cards:
            return self.play_card(random.choice(matching_aggressive_cards))

        return self.play_card(random.choice(self.playable_hand))



class CautiousPlayer(Player):
    """
    Class that implements a player who keeps cards with effects to the end.
    """

    def __init__(self, name):
        super().__init__(name)
        self.cautious_cards: List[Card] = [Card(s, v, effect=None) for s in Suit for v in (Value.FIVE, Value.SIX,
                                                                                           Value.SEVEN,
                                                                                           Value.EIGHT,
                                                                                           Value.NINE, Value.TEN)]
        self.cautious_cards.append(Card(suit=Suit.CLUBS, value=Value.KING, effect=None))
        self.cautious_cards.append(Card(suit=Suit.DIAMOND, value=Value.KING, effect=None))

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
        matching_cautious_cards = [c for c in self.playable_hand if c in self.cautious_cards]
        if matching_cautious_cards:
            return self.play_card(random.choice(matching_cautious_cards))

        return self.play_card(random.choice(self.playable_hand))

class ThresholdPlayer(Player):
    def __init__(self, name, threshold=3):
        super().__init__(name)
        self.threshold = threshold
        self.aggressive = AggressivePlayer(name + "_aggressive")
        self.cautious = CautiousPlayer(name + "_cautious")

    def make_move(self):
        if not self.playable_hand:
            return None

        self.aggressive.playable_hand = self.playable_hand
        self.cautious.playable_hand = self.playable_hand

        if len(self.hand) <= self.threshold:
            return self.aggressive.make_move()
        else:
            return self.cautious.make_move()

class DualThresholdPlayer(Player):
    def __init__(self, name, threshold_lb=3, threshold_ub=10):
        super().__init__(name)
        self.threshold_lb = threshold_lb
        self.threshold_ub = threshold_ub
        if self.threshold_lb > self.threshold_ub:
            raise ValueError("Upper bound threshold must be larger than lower bound threshold")
        self.aggressive = AggressivePlayer(name + "_aggressive")
        self.cautious = CautiousPlayer(name + "_cautious")

    def make_move(self):
        if not self.playable_hand:
            return None

        self.aggressive.playable_hand = self.playable_hand
        self.cautious.playable_hand = self.playable_hand

        if len(self.hand) <= self.threshold_lb or len(self.hand) >= self.threshold_ub:
            return self.aggressive.make_move()
        else:
            return self.cautious.make_move()

class BalancingPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

        from collections import Counter
        self.suit_frequency = Counter()

    def make_move(self) -> Optional[Card]:
        self.suit_frequency.clear()
        self.suit_frequency.update(c.suit for c in self.playable_hand)

        most_common = self.suit_frequency.most_common()

        for common_suit, _ in most_common:
            matching_suits = [c for c in self.playable_hand if c.suit == common_suit]
            if matching_suits:
                return self.play_card(random.choice(matching_suits))


class ChangeSuitPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.card_values = list(Value)
        # TODO should queen be in that list?
    def make_move(self) -> Optional[Card]:
        if not self.playable_hand:
            return None

        matched_values = [c for c in self.playable_hand if c.value in self.card_values]
        if matched_values:
            return self.play_card(random.choice(matched_values))
        else:
            return self.play_card(random.choice(self.playable_hand))

# ---- ADVANCED STRATEGIES ----

class BayesianPlayer(Player):

    def __init__(self, name):
        super().__init__(name)

    def make_move(self) -> Optional[Card]:
        pass

class GeneticPlayer(Player):

    def __init__(self, name):
        super().__init__(name)

    def make_move(self) -> Optional[Card]:
        pass

class MCTSPlayer(Player):
    """
    Class that implements Monte Carlo Search Trees strategy.
    """
    def __init__(self, name):
        super().__init__(name)
        pass

    def make_move(self) -> Optional[Card]:
        pass

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



