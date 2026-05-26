import sqlite3
import json
from datetime import datetime
from card import Suit, Value
from db_models import Game, Card, Player, Strategy, Move, GameCard

class MacauDatabase:
    
    def __init__(self, db_path: str = "macau.db"):
        self.db_path = db_path
        self._create_tables()
        self.seed_cards()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")  # Wymuszenie relacji kluczy obcych
        return conn

    def _create_tables(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS strategies (
                    id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    name    TEXT NOT NULL,
                    params  TEXT,
                    UNIQUE(name, params)
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    id                INTEGER PRIMARY KEY AUTOINCREMENT,
                    num_players       INTEGER NOT NULL,
                    initial_cards_num INTEGER NOT NULL,
                    winner            INTEGER,
                    total_moves       INTEGER NOT NULL,
                    created_at        TEXT NOT NULL,
                    FOREIGN KEY (winner) REFERENCES players(id)
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_id INTEGER NOT NULL,
                    game_id     INTEGER NOT NULL,
                    position    INTEGER NOT NULL,
                    FOREIGN KEY (strategy_id) REFERENCES strategies(id),
                    FOREIGN KEY (game_id) REFERENCES games(id)
               );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cards (
                    id   INTEGER PRIMARY KEY AUTOINCREMENT,
                    suit TEXT NOT NULL,
                    rank TEXT NOT NULL,
                    UNIQUE(suit, rank)
                );
            """)    

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_cards (
                    game_id   INTEGER NOT NULL,
                    card_id   INTEGER NOT NULL,
                    location  TEXT NOT NULL, -- 'deck', 'discard', 'hand'
                    player_id INTEGER,
                    move_num  INTEGER,
                    PRIMARY KEY (game_id, card_id, move_num),
                    FOREIGN KEY (game_id) REFERENCES games(id),
                    FOREIGN KEY (card_id) REFERENCES cards(id),
                    FOREIGN KEY (player_id) REFERENCES players(id)
                );
            """)   

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS moves (
                    id                INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id           INTEGER NOT NULL,
                    player_id         INTEGER NOT NULL,
                    move_num          INTEGER NOT NULL,
                    action            TEXT NOT NULL,
                    hand_before       TEXT,
                    hand_after        TEXT,
                    top_card_before   INTEGER,
                    top_card_after    INTEGER,
                    FOREIGN KEY (game_id) REFERENCES games(id),
                    FOREIGN KEY (player_id) REFERENCES players(id),
                    FOREIGN KEY (top_card_before) REFERENCES cards(id),
                    FOREIGN KEY (top_card_after) REFERENCES cards(id)
                );
            """) 
            conn.commit()
                
    # generate cards
    
    def seed_cards(self):
        suits = list(Suit)
        values = list(Value)
        with self._connect() as conn:
            for suit in suits:
                for val in values:
                    conn.execute("INSERT OR IGNORE INTO cards (suit, rank) VALUES (?, ?)", (suit.value, val.value))

    # insert strategies

    def insert_strategy(self, strategy: Strategy) -> Strategy:
    # ON CONFLICT DO UPDATE nic nie zmienia (name=name), ale zmusza baze do zwrotu ID
        query = """
        INSERT INTO strategies (name, params) 
        VALUES (?, ?)
        ON CONFLICT(name, params) DO UPDATE SET name=name
        RETURNING id
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (strategy.name, strategy.get_params_json()))
            strategy.id = cursor.fetchone()[0]
            conn.commit()
        return strategy
    
    def insert_game(self, game: Game) -> Game:
        query = "INSERT INTO games (num_players, initial_cards_num, winner, total_moves, created_at) VALUES (?, ?, ?, ?, ?)"
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (game.num_players, game.initial_cards_num, game.winner, game.total_moves, game.created_at.isoformat()))
            game.id = cursor.lastrowid
            conn.commit()
        return game

    def update_game_winner_and_total_moves(self, game_id: int, winner_player_id: int, total_moves: int):
        """Aktualizacja zwycięzcy i liczby ruchów po zakończeniu rozgrywki."""
        query = "UPDATE games SET winner = ?, total_moves = ? WHERE id = ?"
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (winner_player_id, total_moves, game_id))
            conn.commit()

    def insert_player(self, player: Player) -> Player:
        query = "INSERT INTO players (strategy_id, game_id, position) VALUES (?, ?, ?)"
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (player.strategy_id, player.game_id, player.position))
            player.id = cursor.lastrowid
            conn.commit()
        return player

    def insert_game_cards(self, game_cards: list[GameCard]):
        """Wstawia stan początkowy lub historię zmian lokalizacji kart."""
        if not game_cards:
            return
        
        query = "INSERT INTO game_cards (game_id, card_id, location, player_id, move_num) VALUES (?, ?, ?, ?, ?)"
        with self._connect() as conn:
            cursor = conn.cursor()
            data = [(gc.game_id, gc.card_id, gc.location, gc.player_id, gc.move_num) for gc in game_cards]
            cursor.executemany(query, data)
            conn.commit()

    def insert_moves(self, moves: Move) -> Move:
        if not moves:
            return
        query = """
            INSERT INTO moves (game_id, player_id, move_num, action, hand_before, hand_after, top_card_before, top_card_after)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            data = [(
                m.game_id, m.player_id, m.move_num,
                m.action, m.hand_before, m.hand_after,
                m.top_card_before, m.top_card_after
            ) for m in moves]
            
            cursor.executemany(query, data)
            conn.commit()
        return moves

            
   