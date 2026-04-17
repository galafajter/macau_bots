import time

from itertools import cycle
from typing import Optional
import random
from game_state import GameState
from game_master import GameMaster
from game_logger import GameLogger
from card import Card, Deck, Value, Suit
from player import Player, AggressivePlayer, CautiousPlayer, RandomPlayer
from typing import List

from tqdm import tqdm

# random.seed(20)

class MacauGame:

    NUMBER_OF_CARDS_PER_PLAYER = 5
    def __init__(self, players: List[Player]):
        if len(players) < 2:
            raise ValueError("Not enough players")
        self.game_master: GameMaster = GameMaster()
        self.game_state: GameState = self.__create_initial_game_state(players)

    def __create_initial_game_state(self, players: List[Player]) -> GameState:

        # create deck
        deck = Deck()
        cards_to_deal, first_card = self.__deal_cards(deck, len(players))

        # deal cards for players
        for i, player_cards in enumerate(cards_to_deal):
            players[i].hand = player_cards

        # put the start card on the stack
        deck.put_on_stack(first_card)

        state = GameState(deck=deck, players=players, current_player_index=0)

        return state

    def __deal_cards(self, deck: Deck, players_num: int) -> tuple[List[List[Card]], Card]:
        cards_to_deal = self.NUMBER_OF_CARDS_PER_PLAYER * players_num

        # TODO adjusting number of decks based on `players_number`
        if cards_to_deal > len(deck.drawing_cards):
            raise ValueError("Too much players for one deck")

        cards_for_players: List[List[Card]] = [[] for _ in range(players_num)]

        for i in range(cards_to_deal):
            cards_for_players[i % players_num].append(deck.draw_from_deck())

        first_card: Card = deck.draw_from_deck()

        # deal drawing_cards to the moment when passive card is on the table
        while first_card.value in (Value.TWO, Value.THREE, Value.FOUR,
                                   Value.JACK, Value.QUEEN, Value.KING,
                                   Value.ACE):
            first_card = deck.draw_from_deck()


        return cards_for_players, first_card

    def play(self, game_id, game_logger, log_filename):
        move_num = 1
        while True:
            # current = self.game_state.current_player
            # top = self.game_state.deck.top_stack_card

            player_idx = self.game_state.current_player_index
            game_logger.log_turn_before_move(self.game_state, player_idx, move_num, game_id)

            action = self.game_master.process_turn(self.game_state)

            game_logger.log_turn_after_move(self.game_state, player_idx, action)

            move_num += 1
    
            for player in self.game_state.players:
                if len(player.hand) == 0:
                    game_logger.log_winner(self.game_state.current_player.name, move_num, game_id)
                    game_logger.save_logs_to_json(log_filename)
                    game_logger.logs.clear()
                    # print(f"Player {player.name} won after {move_num} total moves!")
                    return player.name
    
            if move_num > 1000:  # zabezpieczenie przed nieskończoną pętlą
                # print("Game too long - possible infinite loop")
                return "error"

def simulate_single_game(args):
    game_id, players, filename = args
    game = MacauGame(players)
    logger = GameLogger()
    result = game.play(game_id, logger, filename)
    return result


if __name__ == "__main__":
    import uuid
    rand_uuid = uuid.uuid4().hex[:8]
    filename = f"./results/{rand_uuid}_macau_simulation.json"
    logger = GameLogger()
    for idx in tqdm(range(1000)):
        game = MacauGame(players=[CautiousPlayer("Cautious"), AggressivePlayer("Aggressive"), RandomPlayer("Random")])
        game.play(idx, logger, filename)
