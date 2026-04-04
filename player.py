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
        # TODO somehow put RL bot here
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
    def __init__(self, name):
        super().__init__(name)
    
    def __str__(self):
        return f"Player: {self.name}"

    def __repr__(self):
        return f"Player: {self.name}"
    
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
    

    def make_move(self) -> Card:

        if not self.playable_hand:
            return None
        
        return self.play_card(random.choice(self.playable_hand))
