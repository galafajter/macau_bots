import time

from itertools import cycle
from typing import Optional
import random
from core.game_state import GameState
from core.game_master import GameMaster
from logger.game_logger import GameLogger
from database.database import MacauDatabase
from core.card import Card, Deck, Value, Suit
from core.player import Player, AggressivePlayer, CautiousPlayer, RandomPlayer
from typing import List
from pathlib import Path
from tqdm import tqdm

class MacauGame:

    def __init__(self, players: List[Player], number_of_cards_per_player: int):
        if len(players) < 2:
            raise ValueError("Not enough players")
        self.game_master: GameMaster = GameMaster()
        self.number_of_cards_per_player: int = number_of_cards_per_player
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
        cards_to_deal = self.number_of_cards_per_player * players_num

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

    def play(self,game_logger: GameLogger):
        move_num = 1

        game_logger.init_log(self.game_state)

        while True:
        
            game_logger.in_game_log_before(self.game_state, move_num)
            hand_before = list(self.game_state.current_player.hand)

            self.game_master.process_turn(self.game_state)
            self.game_state.eval_action(hand_before)

            game_logger.in_game_log_after(self.game_state)

            move_num += 1
            # TODO add more places than one
            for pos, player in enumerate(self.game_state.players):
                if len(player.hand) == 0:
                    game_logger.endgame_log(winner_pos=pos, total_moves=move_num)

                    return player.name

            if move_num > 1000:
                # print("Game too long - possible infinite loop")
                return "error"


if __name__ == "__main__":
    db = MacauDatabase("macau.db")
    logger = GameLogger(db_instance=db)

    players = [CautiousPlayer("Cautious"), AggressivePlayer("Aggressive"), RandomPlayer("Random")]
    for idx in tqdm(range(1000)):
        game = MacauGame(players=players, number_of_cards_per_player=5)
        
        game.play(logger)
        
        players = players[-1:] + players[:-1]