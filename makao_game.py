import time

from itertools import cycle
from typing import Optional
import random
from game_state import GameState
from game_master import GameMaster
from game_logger import GameLogger
from card import Card, Deck, Value, Suit
from player import Player
from typing import List

random.seed(20)

class MacauGame:

    NUMBER_OF_CARDS_PER_PLAYER = 5
    def __init__(self, players_num: int):
        if players_num < 2:
            raise ValueError("Not enough players")
        self.game_logger = GameLogger()
        self.game_master: GameMaster = GameMaster()
        self.game_state: GameState = self.__create_initial_game_state(players_num)


    def __create_initial_game_state(self, players_num: int) -> GameState:

        # create players
        players: List[Player] = [Player(str(i)) for i in range(players_num)]

        # create deck
        deck = Deck()
        cards_to_deal, first_card = self.__deal_cards(deck, players_num)

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


    # def play(self):
    #     turn = 0
    #     while True:

    #         print(turn)
    #         print(f"Player {self.game_state.current_player_index} on move")
    #         print(f"Player 0 hand: {self.game_state.players[0].hand}")
    #         print(f"Player 1 hand: {self.game_state.players[1].hand}")
    #         print(f"Player 2 hand: {self.game_state.players[2].hand}")
    #         print(f"Top card: {self.game_state.deck.top_stack_card}")
    #         # print(f"Possible card to play: {self.game_state.}")
    #         print(f"Is some effect active: {self.game_state.effect_active}")
    #         print(f"Suit demand: {self.game_state.demanded_suit}")
    #         print(f"Value demand: {self.game_state.demanded_value}")
    #         print("------------------------------------------------")
    #         print()
    #         self.game_master.process_turn(self.game_state)
    #         turn += 1
    #         if len(self.game_state.current_player.hand) == 0:
    #             return f"Player {self.game_state.current_player.name} won!"
    # #
    #         # time.sleep(0.5)

    def play(self):
        turn = 0
        while True:
            current = self.game_state.current_player
            top = self.game_state.deck.top_stack_card
            # TODO logger
            self.game_master.process_turn(self.game_state)
            # TODO logger ater
            print(f"Tura {turn} | Gracz {current.name} | Top: {top} | Ręka: {current.hand}")
            turn += 1 # TODO make turn change after whole all players make a move
    
            for player in self.game_state.players:
                if len(player.hand) == 0:
                    print(f"Player {player.name} won after {turn} turns!")
                    return player.name
    
            if turn > 1000:  # zabezpieczenie przed nieskończoną pętlą
                print("Game too long - possible infinite loop")
                return "error"

if __name__ == "__main__":
    game = MacauGame(players_num=3)
    game.play()