from card import Card, Value, Suit
from game_state import GameState
from typing import List, Callable


class GameMaster:

    def __init__(self):

        self.functional_cards: List[Card] = [Card(s, v, effect=None) for s in Suit for v in (Value.TWO, Value.THREE,
                                                                                             Value.FOUR, Value.JACK,
                                                                                             Value.QUEEN, Value.KING,
                                                                                             Value.ACE)]
        self.functional_cards.remove(Card(suit=Suit.CLUBS, value=Value.KING, effect=None))
        self.functional_cards.remove(Card(suit=Suit.DIAMOND, value=Value.KING, effect=None))
        self.nonfunctional_cards: List[Card] = [Card(s, v, effect=None) for s in Suit for v in (Value.FIVE, Value.SIX,
                                                                                                Value.SEVEN, Value.EIGHT,
                                                                                                Value.NINE, Value.TEN)]
        self.nonfunctional_cards.append(Card(suit=Suit.CLUBS, value=Value.KING, effect=None))
        self.nonfunctional_cards.append(Card(suit=Suit.DIAMOND, value=Value.KING, effect=None))
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

    def eval_action(self, move: Card | None, state: GameState) -> dict:
        if move is None and state.execute_effect:
            if state.block_count:
                return {"action": "execute_block"}
            elif state.cards_to_draw:
                return {"action": "execute_war"}
            elif state.demanded_suit is not None:
                return {"action": "draw_card_because_dont_have_suit"}
            elif state.demanded_value is not None:
                return {"action": "draw_card_because_dont_have_value"}
            else:
                return {"action": "unknown_none_action"}

        elif move is None and not state.execute_effect:
            return {"action": "draw_card"}


        if move in self.functional_cards:
            if move.value == Value.ACE:
                return {"action": "suit_demand", "card": str(move)}

            elif move.value in [Value.TWO, Value.THREE]:
                return {"action": "war", "card": str(move)}

            elif move in [Card(suit=Suit.SPADES, value=Value.KING, effect=None), Card(suit=Suit.HEART, value=Value.KING, effect=None)]:
                return {"action": "war", "card": str(move)}
            elif move.value == Value.QUEEN:
                return {"action": "skip", "card": str(move)}

            elif move.value == Value.JACK:
                return {"action": "value_demand", "card": str(move)}
            elif move.value == Value.FOUR:
                return {"action": "block", "card": str(move)}
            else:
                return {"action": "unknown_functional_action", "card": str(move)}


        elif move in self.nonfunctional_cards:
            if not state.effect_active:
                return {"action": "play_card", "card": str(move)}
            elif state.effect_active and state.demanded_value is not None:
                return {"action": "play_demanded_value", "card": str(move)}

            elif state.effect_active and state.demanded_suit is not None:
                return {"action": "play_demanded_suit", "card": str(move)}
            else:
                return {"action": "unknown_nonfunctional_action", "card": str(move)}



    def process_turn(self, state: GameState) -> dict:

        if state.current_player_index in state.blocked_turns_per_player:
            state.blocked_turns_per_player[state.current_player_index] -= 1
            if state.blocked_turns_per_player[state.current_player_index] == 0:
                del state.blocked_turns_per_player[state.current_player_index]
            self._advance_turn(state)
            return {"action": "skipped_turn_because_of_block"}


        playable_cards = self.get_playable_card(state)

        state.current_player.evaluate_hand_for_playable_cards(playable_cards)

        move = state.current_player.make_move()

        state = self._handle_move(state, move)

        action = self.eval_action(move, state)

        if state.execute_effect:
            state = self._handle_pending_effects(state)
            self._advance_turn(state)
            return action

        state = self._advance_turn(state)

        if state.demand_turns_left > 0:
            state.demand_turns_left -= 1
            if state.demand_turns_left == 0:
                state.effect_active = False
                state.demanded_value = None
                state.demanded_suit = None

        return action

    @staticmethod
    def _handle_pending_effects(state: GameState) -> GameState:

        state.execute_effect = False
        state.effect_active = False

        if state.block_count:
            # quick fix for actual blocking logic # TODO make better handling of block rule
            state.blocked_turns_per_player[state.current_player_index] = state.block_count * (len(state.players) - 1)
            state.reset_active_effect()

        if state.cards_to_draw: # TODO 'lucky card' rule implementation
            for _ in range(state.cards_to_draw):
                drawn_card = state.deck.draw_from_deck()
                if drawn_card:
                    state.current_player.draw_card(drawn_card)

            state.reset_active_effect()

        return state

    def _handle_move(self, state: GameState, move: Card | None) -> GameState:

        if not state.effect_active and move is None:
            drawn_card = state.deck.draw_from_deck()
            if drawn_card:
                state.current_player.draw_card(drawn_card)
                return state
            else:
                return state

        if state.effect_active and move is None:
            state.execute_effect = True
            return state

        state = self.apply_effect(state, move)
        state.deck.put_on_stack(move)
        return state

    @staticmethod
    def _advance_turn(state: GameState) -> GameState:

        state.current_player_index = (state.current_player_index + state.turn_direction) % len(state.players)
        return state

    def get_playable_card(self, state: GameState) -> List[Card]:

        top_card = state.deck.top_stack_card

        if state.demanded_suit:
            return self._playable_cards_handlers[Value.ACE](state)
        elif state.demanded_value:
            return self._playable_cards_handlers[Value.JACK](state)

        if state.effect_active:
            handler = self._playable_cards_handlers.get(top_card.value)
            if handler:
                return handler(state)

        return self._playable_normal(state)

    def apply_effect(self, state: GameState, card: Card) -> GameState:
        handler = self._effect_handlers.get(card.value)

        if handler:
            state.effect_active = True
            return handler(state, card)
        return state

    @staticmethod
    def _handle_war(state: GameState, card: Card) -> GameState:
        state.cards_to_draw += int(card.value.value)
        state.reset_suit_demand()
        return state

    @staticmethod
    def _handle_block(state: GameState, card: Card) -> GameState:
        state.block_count += 1
        return state

    @staticmethod
    def _handle_value_demand(state: GameState, card: Card) -> GameState:
        demanded_value = state.current_player.make_value_demand()
        state.demanded_value = demanded_value
        state.demand_turns_left = len(state.players) + 1
        return state

    @staticmethod
    def _handle_suit_demand(state: GameState, card: Card) -> GameState:
        demanded_suit = state.current_player.make_suit_demand()
        state.demanded_suit = demanded_suit
        state.demand_turns_left = len(state.players) + 1
        return state

    @staticmethod
    def _handle_skip(state: GameState, card: Card) -> GameState:
        state.reset_active_effect()
        return state

    @staticmethod
    def _handle_king_war(state: GameState, card: Card) -> GameState:

        if card.suit == Suit.HEART:
            state.cards_to_draw += 5
            if state.turn_direction < 0:
                state.turn_direction *= -1
            state.reset_suit_demand()

        elif card.suit == Suit.SPADES:
            state.cards_to_draw += 5
            state.turn_direction *= -1
            state.reset_suit_demand()

        else:
            state.effect_active = False

        return state

    def _playable_war(self, state: GameState) -> List[Card]:
        return [card for card in self.functional_cards if card.value in (Value.TWO, Value.THREE) or card.value == Value.QUEEN]

    def _playable_block(self, state: GameState) -> List[Card]:
        return [card for card in self.functional_cards if card.value == Value.FOUR or card.value == Value.QUEEN]

    def _playable_value_demand(self, state: GameState) -> List[Card]:
        demand_cards = [card for card in self.nonfunctional_cards if card.value == state.demanded_value]
        queen_cards = [card for card in self.functional_cards if card.value == Value.QUEEN]
        return demand_cards + queen_cards

    def _playable_queen(self, state: GameState) -> List[Card]:
        return self.all_cards

    def _playable_king_war(self, state: GameState) -> List[Card]:
        return [card for card in self.functional_cards if card.value == Value.KING and card.suit in [Suit.HEART, Suit.SPADES]]

    def _playable_suit_demand(self, state: GameState) -> List[Card]:
        return [card for card in self.all_cards if card.suit == state.demanded_suit]

    def _playable_normal(self, state: GameState):
        return [card for card in self.all_cards if (card.value == state.deck.top_stack_card.value) \
                               or (card.suit == state.deck.top_stack_card.suit) or (card.value == Value.QUEEN)]




