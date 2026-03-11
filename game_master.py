from card import Card, Value, Suit
from game_state import GameState
from typing import List, Callable


class GameMaster:

    def __init__(self):

        self.functional_cards: List[Card] = [Card(s, v, effect=None) for s in Suit for v in (Value.TWO, Value.THREE,
                                                                                             Value.FOUR, Value.JACK,
                                                                                             Value.QUEEN, Value.KING,
                                                                                             Value.ACE)]
        self.nonfunctional_cards: List[Card] = [Card(s, v, effect=None) for s in Suit for v in (Value.FIVE, Value.SIX,
                                                                                                Value.SEVEN, Value.EIGHT,
                                                                                                Value.NINE, Value.TEN)]
        self.all_cards = self.functional_cards + self.nonfunctional_cards

        self._effect_handlers: dict[Value, Callable[[GameState, Card], GameState]] = {
            Value.TWO: self._handle_war,
            Value.THREE: self._handle_war,
            Value.FOUR: self._handle_block,
            Value.JACK: self._handle_value_demand,
            Value.QUEEN: self._handle_skip,
            Value.KING: self._handle_king_war,
            Value.ACE: self._handle_suit_demand,
        }

        self._playable_cards_handlers: dict[Value, Callable[[GameState], List[Card]]] = {
            Value.TWO: self._playable_war,
            Value.THREE: self._playable_war,
            Value.FOUR: self._playable_block,
            Value.JACK: self._playable_value_demand,
            Value.QUEEN: self._playable_queen,
            Value.KING: self._playable_king_war,
            Value.ACE: self._playable_suit_demand,
        }

    def process_turn(self, state: GameState, card: Card | None) -> GameState:
        ...

    def get_playable_card(self, state: GameState) -> List[Card]:

        top_card = state.deck.top_stack_card

        if state.demanded_suit:
            return self._playable_cards_handlers[Value.ACE](state)
        elif state.demanded_value:
            return self._playable_cards_handlers[Value.JACK](state)

        handler = self._playable_cards_handlers.get(top_card.value)

        if handler:
            return handler(state)

        return self._playable_normal(state)

    def apply_effect(self, state: GameState, card: Card) -> GameState:
        handler = self._effect_handlers.get(card.value)

        if handler:
            return handler(state, card)
        return state


    @staticmethod
    def _handle_war(state: GameState, card: Card) -> GameState:
        state.cards_to_draw += int(card.value.value)
        return state

    @staticmethod
    def _handle_block(state: GameState, card: Card) -> GameState:
        state.turns_being_blocked += 1
        return state

    @staticmethod
    def _handle_value_demand(state: GameState, card: Card) -> GameState:
        state.demanded_value = card.value
        return state

    @staticmethod
    def _handle_suit_demand(state: GameState, card: Card) -> GameState:
        state.demanded_suit = card.suit
        return state

    @staticmethod
    def _handle_skip(state: GameState, card: Card) -> GameState:
        state.reset_active_effect()
        return state

    @staticmethod
    def _handle_king_war(state: GameState, card: Card) -> GameState:

        if card.suit == Suit.HEART:
            state.cards_to_draw += 5

        elif card.suit == Suit.SPADES:
            state.cards_to_draw += 5
            state.turn_direction *= -1

        return state

    def _playable_war(self, state: GameState) -> List[Card]:
        return [card for card in self.functional_cards if card.value in (Value.TWO, Value.THREE) or card.value == Value.QUEEN]

    def _playable_block(self, state: GameState) -> List[Card]:
        return [card for card in self.functional_cards if card.value == Value.FOUR or card.value == Value.QUEEN]

    def _playable_value_demand(self, state: GameState) -> List[Card]:
        return [card for card in self.nonfunctional_cards if card.value == state.demanded_value] # TODO think about queen role in ending demand effect

    def _playable_queen(self, state: GameState) -> List[Card]:
        return self.all_cards

    def _playable_king_war(self, state: GameState) -> List[Card]:
        return [card for card in self.functional_cards if card.value == Value.KING and card.suit in [Suit.HEART, Suit.SPADES]]

    def _playable_suit_demand(self, state: GameState) -> List[Card]:
        return [card for card in self.all_cards if card.suit == state.demanded_suit]


    def _playable_normal(self, state: GameState):
        return [card for card in self.all_cards if (card.value == state.deck.top_stack_card.value) \
                               or (card.suit == state.deck.top_stack_card.suit) or (card.value == Value.QUEEN)]




