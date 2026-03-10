from card import Card
from typing import List, Optional
import random

class Player:
    def __init__(self, name: str, is_bot: bool):
        self.name = name
        self.is_bot = is_bot
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
        for card in self.hand:
            if card in playable_cards:
                self.playable_hand.append(card)


    def make_value_demand(self):
        ...

    def make_suit_demand(self):
        ...

    def make_random_move(self) -> Optional[Card]:
        """
        Method that implements random strategy of a player.
        """
        if len(self.playable_hand) == 0:
            return None
        rnd_card = random.choice(self.playable_hand)
        self.playable_hand.remove(rnd_card)
        return rnd_card

    def make_first_possible_move(self) -> Optional[Card]:
        """
        Method that implements strategy of a player.

        Currently, it is basic strategy - throw first fitting card that you see.
        """
        if len(self.playable_hand) == 0:
            return None

        return self.playable_hand.pop()

    def make_move(self, top_card: Card) -> Optional[Card]:
        """
        Method that implements strategy of a player.

        Currently, it is basic strategy - throw first fitting card that you see.
        """
        # TODO somehow put RL bot here
        for card in self.playable_hand:
            if (card.suit.value == top_card.suit.value) or (card.value.value == top_card.value.value):
                return self.play_card(card)
        else:
            return None

    def play_card(self, card: Card):
        if card in self.hand:
            self.hand.remove(card)
            return card