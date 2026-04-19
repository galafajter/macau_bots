from game_state import GameState
from card import Card
import pandas as pd
import json


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
            'hand_size_before': len(state.players[player_index].hand),
            'top_card_before': str(state.deck.top_stack_card),
            'effect_active': state.effect_active,
            # 'remaining_demand_turns_before': state.demand_turns_left
        })

    def log_turn_after_move(self, state: GameState, player_index: int, action_made: str):
        self.logs[-1].update({
            'cards_in_hand_after': len(state.players[player_index].hand),
            'top_card_after': str(state.deck.top_stack_card),
            'action_made': action_made,
            'deck_remaining': len(state.deck.drawing_cards),
            # 'remaining_demand_turns_after': state.demand_turns_left,
        })


    def log_winner(self, winner_name: str, moves: int, game_id: int):
        self.game_results.append({
            'game_id': game_id,
            'winner': winner_name,
            'total_moves': moves
        })

    def save_logs_to_json(self, filename: str):
        with open(filename, "a") as f:
            for log in self.logs:
                f.write(json.dumps(log) + "\n")
        self.logs.clear()

    def save_game_winner(self, filename):
        with open(f"{filename}", "a") as f:
            f.write(json.dumps(*self.game_results) + "\n")
        self.game_results.clear()