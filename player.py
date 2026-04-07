from card import Card, Value, Suit
from typing import List, Optional
import random


class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand: List[Card] = []
        self.playable_hand: List[Card] = []

    def __str__(self):
        return f"Player: {self.name}"

    def __repr__(self):
        return f"Player: {self.name}"

    def draw_card(self, card: Card):
        self.hand.append(card)

    def evaluate_hand_for_playable_cards(self, playable_cards: List[Card]):
        """Choose cards that player can throw on top_stack_card"""
        self.playable_hand = []

        for card in self.hand:
            if card in playable_cards:
                self.playable_hand.append(card)


    def make_value_demand(self) -> Value:
        return random.choice(list(Value))

    def make_suit_demand(self) -> Suit:
        return random.choice(list(Suit))


    def make_move(self) -> Optional[Card]:
        """
        Method that implements strategy of a player.

        Currently, it is basic strategy - throw first fitting card that you see.
        """
        if not self.playable_hand:
            return None
        return self.play_card(self.playable_hand[0])

    def play_card(self, card: Card) -> Optional[Card]:
        if card in self.hand:
            self.hand.remove(card)
            return card
        else:
            return None
        

class RandomPlayer(Player):
    """
    Class that implements a player who makes random moves.
    """
    def __init__(self, name):
        super().__init__(name)
    
    def __str__(self):
        return f"Random player: {self.name}"

    def __repr__(self):
        return f"Random player: {self.name}"
    
    def play_card(self, card: Card) -> Optional[Card]:
        if card in self.hand:
            self.hand.remove(card)
            return card
        else:
            return None

    def draw_card(self, card: Card):
        self.hand.append(card)

    def evaluate_hand_for_playable_cards(self, playable_cards: List[Card]):
        """Choose cards that player can throw on top_stack_card"""
        self.playable_hand = []

        for card in self.hand:
            if card in playable_cards:
                self.playable_hand.append(card)


    def make_value_demand(self) -> Value:
        return random.choice(list(Value))

    def make_suit_demand(self) -> Suit:
        return random.choice(list(Suit))
    

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

    def __str__(self):
        return f"Aggressive player: {self.name}"

    def __repr__(self):
        return f"Aggressive player: {self.name}"

    def draw_card(self, card: Card):
        self.hand.append(card)

    def evaluate_hand_for_playable_cards(self, playable_cards: List[Card]):
        """Choose cards that player can throw on top_stack_card"""
        self.playable_hand = []

        for card in self.hand:
            if card in playable_cards:
                self.playable_hand.append(card)


    def make_value_demand(self) -> Value:
        return random.choice(list(Value))

    def make_suit_demand(self) -> Suit:
        return random.choice(list(Suit))


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

    def __str__(self):
        return f"Cautious player: {self.name}"

    def __repr__(self):
        return f"Cautious player: {self.name}"

    def draw_card(self, card: Card):
        self.hand.append(card)

    def evaluate_hand_for_playable_cards(self, playable_cards: List[Card]):
        """Choose cards that player can throw on top_stack_card"""
        self.playable_hand = []

        for card in self.hand:
            if card in playable_cards:
                self.playable_hand.append(card)


    def make_value_demand(self) -> Value:
        return random.choice(list(Value))

    def make_suit_demand(self) -> Suit:
        return random.choice(list(Suit))


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

class MCTSPlayer(Player):
    """
    Class that implements Monte Carlo Search Trees strategy.
    """
    pass


