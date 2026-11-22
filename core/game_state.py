from core.card import Card, Deck, Suit, Value
from core.player import Player
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

    # "szczęśliwa karta": próbny dobór w tej turze (1 karta) i karta zagrana w tej turze
    lucky_drawn: bool = False
    played_card: Card | None = None

    # indeks gracza, który wykonał bieżący ruch (ustawia GameMaster.process_turn);
    # annotate_action porównuje ręce TEGO gracza, a nie "bieżącego" po advance
    last_mover_index: int | None = None

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

    def annotate_action(self, hand_before: list[Card]):
        """Oznacza akcję tury (etykiety zapisywane do SQLite).

        Ręką po ruchu jest ręka gracza, który WYKONAŁ ruch (last_mover_index),
        nie "bieżący" gracz -- process_turn zdążył już przejść dalej.
        Uwaga: GameMaster.eval_action to INNA metoda (słownik akcji silnika).
        """
        if self.last_mover_index is not None:
            mover = self.players[self.last_mover_index]
        else:
            mover = self.current_player

        hand_after = mover.hand
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

        elif self.played_card is not None:
            # "szczęśliwa karta": w tej turze nastąpił próbny dobór i zagranie
            # tej samej karty (długość ręki bez zmian) -- to jest zagranie, nie blokada
            self.action = "play_card"
            self.last_affected_cards.append(self.played_card)

        else:
            self.action = "blocked"