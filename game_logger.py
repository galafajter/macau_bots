from game_state import GameState
from card import Card
import json
from database import MacauDatabase
from db_models import Game, Player, Strategy, Move, GameCard


class GameLogger:

    def __init__(self, db_instance: MacauDatabase):
        self.db: MacauDatabase = db_instance

        self.game = None
        self.players = []
        self.strategies = []

        self.moves_logs: list[Move] = []
        self.cards_positions_logs: list[GameCard] = []

        self.card_id_cache = self._load_card_ids()


    def _load_card_ids(self) -> dict:
        with self.db._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, suit, rank FROM cards")

            return {(row[1], row[2]): row[0] for row in cursor.fetchall()}

    def _get_card_id(self, card: Card) -> int:
        return self.card_id_cache.get((card.suit.value, card.value.value))

    def init_log(self, state: GameState):
        players = state.players
        game = Game(
            num_players=len(players),
            initial_cards_num=len(players[0].hand),
        )
        self.game = self.db.insert_game(game)

        for pos, player in enumerate(players):

            strategy = Strategy(
                name=player.get_strategy_name(),
                params=player.get_params()
            )

            strategy = self.db.insert_strategy(strategy)

            player_db = Player(
                strategy_id=strategy.id,
                game_id=self.game.id,
                position=pos
            )

            player_db = self.db.insert_player(player_db)
            self.players.append(player_db)

        for pos, player in enumerate(players):
            player_id = self.players[pos].id
            for card in player.hand:
                self.cards_positions_logs.append(
                    GameCard(
                        game_id=self.game.id,
                        card_id=self._get_card_id(card),
                        location='hand',
                        player_id=player_id,
                        move_num=0
                    )
                )
        
        for card in state.deck.drawing_cards:
            self.cards_positions_logs.append(
                GameCard(
                    game_id=self.game.id,
                    card_id=self._get_card_id(card),
                    location='deck',
                    player_id=None,
                    move_num=0
                )
            )
        
        top_card = state.deck.top_stack_card
        self.cards_positions_logs.append(
            GameCard(
                game_id=self.game.id,
                card_id=self._get_card_id(top_card),
                location='stack',
                player_id=None,
                move_num=0
            )
        )

    def in_game_log_before(self, state: GameState, move_num: int) -> Move:
        """Logging data while game runs before player move"""
        
        hand_before_str = json.dumps([f"{c.value.name}_{c.suit.name}" for c in state.current_player.hand])
        top_card_id = self._get_card_id(state.deck.top_stack_card)

        move_before = Move(
            game_id=self.game.id,
            player_id=self.players[state.current_player_index].id,
            move_num=move_num,
            hand_before=hand_before_str,
            top_card_before=top_card_id,
        )
        self.moves_logs.append(move_before)
    
    def in_game_log_after(self, state: GameState):
        """Logging data while game runs after player move"""
        move_before = self.moves_logs[-1]

        hand_after_str = json.dumps([f"{c.value.name}_{c.suit.name}" for c in state.current_player.hand])
        top_card_id = self._get_card_id(state.deck.top_stack_card)

        move_after = Move(
            game_id=move_before.game_id,
            player_id=move_before.player_id,
            move_num=move_before.move_num,
            action=state.action,
            hand_before=move_before.hand_before,
            hand_after=hand_after_str,
            top_card_before=move_before.top_card_before,
            top_card_after=top_card_id
        )

        self.moves_logs[-1] = move_after

        if state.action == "play_card":
            for card in state.last_affected_cards:
                self.cards_positions_logs.append(
                    GameCard(
                        game_id=self.game.id,
                        card_id=self._get_card_id(card),
                        location='stack',
                        player_id=None,
                        move_num=move_after.move_num
                    )
                )

        elif state.action in ("draw_card", "draw_more_cards"):
            for card in state.last_affected_cards:
                self.cards_positions_logs.append(
                    GameCard(
                        game_id=self.game.id,
                        card_id=self._get_card_id(card),
                        location='hand',
                        player_id=move_after.player_id,
                        move_num=move_after.move_num
                    )
                )
        
    def endgame_log(self, winner_pos: int, total_moves: int):
        winner_db_id = self.players[winner_pos].id

        self.db.insert_moves(self.moves_logs)
        self.db.insert_game_cards(self.cards_positions_logs)

        self.db.update_game_winner_and_total_moves(self.game.id, winner_db_id, total_moves)

        self.players.clear()
        self.strategies.clear()
        self.moves_logs.clear()
        self.cards_positions_logs.clear()
        self.game = None
