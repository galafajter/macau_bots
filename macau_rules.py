from makao_game import Card, Value, Suit
from typing import List

class Rules:
    def __init__(self):
        self.playable_cards = []
        self.functional_cards: List[Card] = [Card(s, v, effect=None) for s in Suit for v in [Value.TWO, Value.THREE,
                                                                                             Value.FOUR, Value.JACK,
                                                                                             Value.QUEEN, Value.KING,
                                                                                             Value.ACE]]
        self.nonfunctional_cards: List[Card] = [Card(s, v, effect=None) for s in Suit for v in [Value.FIVE, Value.SIX,
                                                                                                Value.SEVEN, Value.EIGHT,
                                                                                                Value.NINE, Value.TEN]]
        self.all_cards = self.playable_cards + self.nonfunctional_cards

        self.ruleset = []

        self.war_flag = False
        self.block_flag = False
        self.value_demand_flag = False
        self.queen_flag = False
        self.king_war_flag = False
        self.suit_demand_flag = False

    def get_game_state(self, top_card: Card):
        if top_card.value in [Value.TWO, Value.THREE]:
            # self.get_two_three_playable()
            self.war_flag = True
        elif top_card.value  == Value.FOUR:
            # self.get_four_playable()
            self.block_flag = True
        elif top_card.value == Value.JACK:
            # self.get_jack_playable(optional_demand)
            self.value_demand_flag = True
        elif top_card.value == Value.QUEEN:
            # self.get_queen_playable()
            self.queen_flag = True
        elif top_card.value == Value.KING:
            # self.get_king_playable()
            self.king_war_flag = True
        elif top_card.value == Value.ACE:
            # self.get_ace_playable(optional_demand)
            self.suit_demand_flag = True

        return {
            "war": self.war_flag,
            "block": self.block_flag,
            "value_demand": self.value_demand_flag,
            "skip": self.queen_flag,
            "king_war": self.king_war_flag,
            "suit_demand": self.suit_demand_flag,
            # "playable_cards": self.playable_cards
        }

    def get_two_three_playable(self):
        self.playable_cards = [card for card in self.functional_cards if card.value in [Value.TWO, Value.THREE]]

    def get_four_playable(self):
        self.playable_cards = [card for card in self.functional_cards if card.value == Value.FOUR]

    def get_jack_playable(self, demanded_value):
        self.playable_cards = [card for card in self.nonfunctional_cards if card.value == demanded_value]

    def get_queen_playable(self):
        self.playable_cards = self.all_cards

    def get_king_playable(self):
        self.playable_cards = [card for card in self.functional_cards if card.value == Value.KING]

    def get_ace_playable(self, demanded_suit):
        self.playable_cards = [card for card in self.all_cards if card.suit == demanded_suit]
        # TODO or Value.ACE

class GameMaster:
    def __init__(self):
        self.rules = Rules()
        self.cards_to_draw = 0
        self.turns_to_wait = 0

    def evaluate_game_state(self, top_card: Card):
        game_state = self.rules.get_game_state(top_card)
        if game_state["war"]:
            self.cards_to_draw += top_card.value.value
            self.rules.get_two_three_playable()
        elif game_state["block"]:
            self.turns_to_wait += 1
            self.rules.get_four_playable()
        elif game_state["value_demand"]:
            ...
        elif game_state["skip"]:
            ...
            self.rules.get_queen_playable()
        elif game_state["king_war"]:
            self.cards_to_draw += 5
            self.rules.get_king_playable()
        elif game_state["suit_demand"]:
            ...
        else:
            # normal card was played
            # self.rules.get_nonfunctional_playable(top_card)
            ...

    def evaluate_demand(self, demand_type: str, demand: Suit | Value):
        if demand_type == "value":
            ...
            self.rules.get_ace_playable(demand)
        elif demand_type == "suit":
            ...
            self.rules.get_ace_playable(demand)
        else:
            raise (NotImplementedError, "Such demand type doesn't exist")



