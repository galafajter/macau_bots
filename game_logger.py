from game_state import GameState
from card import Card
import pandas as pd


class GameLogger:

    def __init__(self):
        self.logs: list = []
        self.columns: list = []

    def log_turn_before_move(self, state: GameState, player_index: int,
                  move: Card, turn_num: int, game_id: int):
        self.logs.append({
            'game_id': game_id,
            'turn': turn_num,
            'player': player_index,
            'cards_in_hand_before': state.player[player_index].hand,
            'top_card_before': state.deck.top_stack_card,
            'effect_active': state.effect_active
        })
    # TOOD add more log data
    def log_turn_after_move(self, state: GameState, player_index: int, action_made: str):
        self.logs[-1].update({
            'cards_in_hand_after': state.players[player_index].hand,
            'top_card_after': state.deck.top_stack_card,
            'action_made': action_made,
            'deck_remaining': len(state.deck.drawing_cards)
        })

    def save_logs_to_csv(self, filename: str):
        pd.DataFrame(self.logs).to_csv(filename, index=False)
