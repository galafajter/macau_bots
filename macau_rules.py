from card import Card, Value, Suit
from player import Player
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
        self.all_cards = self.functional_cards + self.nonfunctional_cards

        self.ruleset = []

        self.war_flag = False
        self.block_flag = False
        self.value_demand_flag = False
        self.queen_flag = False
        self.king_war_flag = False
        self.suit_demand_flag = False


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

    # TODO or Value.ACE
    def get_ace_playable(self, demanded_suit):
        self.playable_cards = [card for card in self.all_cards if card.suit == demanded_suit]

    def get_nonfunctional_playable(self, top_card):
        self.playable_cards = [card for card in self.all_cards if (card.value == top_card.value) \
                               or (card.suit == top_card.suit) or (card.value == Value.QUEEN)]

class GameMaster:
    def __init__(self):
        self.rules = Rules()
        self.cards_to_draw = 0
        self.turns_to_wait = 0
        self.evaluated_game_state = {}
        self.current_player: Player | None = None

    def set_current_player(self, player: Player):
        self.current_player = player

    def evaluate_game_state(self, top_card: Card):
        game_state = self.rules.get_game_state(top_card)
        if game_state["war"]:
            self.cards_to_draw += top_card.value.value
            self.rules.get_two_three_playable()
        elif game_state["block"]:
            self.turns_to_wait += 1 # plus one waiting turn for one card
            self.rules.get_four_playable()
        elif game_state["value_demand"]:
            value_demand = self.current_player.make_value_demand()
            self.evaluate_demand("value", value_demand)
        elif game_state["skip"]:
            ...
            self.rules.get_queen_playable()
        elif game_state["king_war"]:
            # TODO add war ending with clubs and diamonds and reversing with spades
            self.cards_to_draw += 5 # TODO think how to avoid magic numbers
            self.rules.get_king_playable()
        elif game_state["suit_demand"]:
            suit_demand = self.current_player.make_suit_demand()
            self.evaluate_demand("suit", suit_demand)
        else:
            # normal card was played
            self.rules.get_nonfunctional_playable(top_card)

        return {
            "war": self.rules.war_flag,
            "block": self.rules.block_flag,
            "value_demand": self.rules.value_demand_flag,
            "skip": self.rules.queen_flag,
            "king_war": self.rules.king_war_flag,
            "suit_demand": self.rules.suit_demand_flag,
            "playable_cards": self.rules.playable_cards,
            "cards_to_draw": self.cards_to_draw,
            "turns_to_wait": self.turns_to_wait,
        }

    # TODO how to implement function of block and card drawing

    def reset_war(self):
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



