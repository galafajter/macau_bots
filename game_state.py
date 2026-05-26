from card import Card, Deck, Effect, Suit, Value
from player import Player
from typing import List
from dataclasses import dataclass, field


@dataclass
class GameState:

    deck: Deck
    players: List[Player]
    current_player_index: int

    demanded_suit: Suit | None = None
    demanded_value: Value | None = None
    demand_turns_left: int = 0

    cards_to_draw: int = 0

    blocked_turns_per_player: dict[int, int] = field(default_factory=dict)
    block_count: int = 0

    effect_active: bool = False
    execute_effect: bool = False

    turn_direction: int = 1

    skip_turn: bool = False

    action: str = ""
    last_affected_cards: list[Card] = field(default_factory=list)

    def reset_active_effect(self):
        self.cards_to_draw = 0
        self.block_count = 0
        self.demanded_suit = None
        self.demanded_value = None
        self.demand_turns_left = 0
        self.effect_active = False
        self.execute_effect = False


    def reset_suit_demand(self):
        self.demanded_suit = None
        self.demand_turns_left = 0


    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    def eval_action(self, hand_before: list[Card]):
            hand_after = self.current_player.hand
            top_card_after = self.deck.top_stack_card

            self.last_affected_cards.clear()

            if len(hand_before) > len(hand_after):
                self.action = "play_card"
                self.last_affected_cards.append(top_card_after)
                
            elif len(hand_before) + 1 == len(hand_after):
                self.action = "draw_card"
                drawn_card = [c for c in hand_after if c not in hand_before][0]
                self.last_affected_cards.append(drawn_card)

            elif len(hand_before) < len(hand_after):
                self.action = "draw_more_cards"
                drawn_cards = [c for c in hand_after if c not in hand_before]
                self.last_affected_cards.extend(drawn_cards)

            else:
                self.action = "blocked"