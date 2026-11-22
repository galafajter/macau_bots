"""Współdzielone helpery testowe (gracze deterministyczni, talie kontrolowane)."""

from typing import Optional

from core.card import Card, Deck, Suit, Value
from core.player import Player


def card(suit: Suit, value: Value) -> Card:
    return Card(suit, value, effect=None)


class DummyPlayer(Player):
    """Deterministyczny gracz: zagra pierwsza karte z playable_hand (albo None)."""

    def make_move(self) -> Optional[Card]:
        if not self.playable_hand:
            return None
        return self.play_card(self.playable_hand[0])


class DecliningPlayer(DummyPlayer):
    """Gracz, który zagra normalnie z reki, ale odrzuci szczesliwa karte
    (drugie pytanie make_move w tej samej turze)."""

    def __init__(self, name):
        super().__init__(name)
        self.decline_lucky = False

    def make_move(self) -> Optional[Card]:
        # pierwsze pytanie: playable_hand puste (brak obrony) -> flaga zostaje;
        # drugie pytanie (po doborze probnym): playable_hand ma Karte i tu rezygnujemy
        if self.playable_hand and self.decline_lucky:
            self.decline_lucky = False
            return None
        return super().make_move()


def make_deck(stack_cards, drawing_cards=()) -> Deck:
    """Talia w pelni kontrolowana przez test.

    UWAGA: Deck.draw_from_deck pobiera z KONCA listy drawing_cards.
    """
    deck = Deck()
    deck.stack_of_placed_cards = list(stack_cards)
    deck.drawing_cards = list(drawing_cards)
    return deck


class NullLogger:
    """Logger-bez-zużycia: MacauGame.play wymaga loggera, testy tego nie potrzebują."""

    def init_log(self, state):
        pass

    def in_game_log_before(self, state, move_num):
        pass

    def in_game_log_after(self, state):
        pass

    def endgame_log(self, winner_pos, total_moves):
        pass
