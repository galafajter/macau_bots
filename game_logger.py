from game_state import GameState
from card import Card
import pandas as pd


class GameLogger:

    def __init__(self):
        self.logs: list = []
        self.game_results: list = []

    def log_turn_before_move(self, state: GameState, player_index: int,
                  move_num: int, game_id: int):
        self.logs.append({
            'game_id': game_id,
            'move_num': move_num,
            'player': player_index,
            'cards_in_hand_before': list(state.players[player_index].hand),
            'top_card_before': state.deck.top_stack_card,
            'effect_active': state.effect_active
        })
    # TOOD add more log data
    def log_turn_after_move(self, state: GameState, player_index: int, action_made: str):
        self.logs[-1].update({
            'cards_in_hand_after': list(state.players[player_index].hand),
            'top_card_after': state.deck.top_stack_card,
            'action_made': action_made,
            'deck_remaining': len(state.deck.drawing_cards)
        })


    def log_winner(self, winner_name: str, moves: int, game_id: int):
        self.game_results.append({
            'game_id': game_id,
            'winner': winner_name,
            'total_moves': moves
        })

    def save_logs_to_csv(self, filename: str):
        pd.DataFrame(self.logs).to_csv(filename, index=False)
        pd.DataFrame(self.game_results).to_csv(
            filename.replace('.csv', '_results.csv') ,
            index=False
        )