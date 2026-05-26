import sqlite3
import json
from datetime import datetime
from card import Suit, Value
from db_models import Game, Card, Player, Strategy, Move, GameCard
import threading

class MacauDatabase:
    
    def __init__(self, db_path: str = "macau.db"):
        self.db_path = db_path
        self._local = threading.local()
        self._create_tables()

    def _get_conn(self) -> sqlite3.Connection:
        """Zwraca połączenie dla bieżącego wątku. Tworzy je jeśli nie istnieje."""
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA journal_mode = WAL;")  # równoległy zapis z wielu procesów
            conn.execute("PRAGMA synchronous = NORMAL;")  # bezpieczniejsze niż OFF, szybsze niż FULL
            conn.execute("PRAGMA cache_size = -20000;")
            conn.execute("PRAGMA temp_store = MEMORY;")
            self._local.conn = conn
        return self._local.conn

    from contextlib import contextmanager

    @contextmanager
    def _connect(self):
        """For compatibility reasons"""
        yield self._get_conn()

    def close(self):
        """Close connection of current thread"""
        if hasattr(self._local, "conn") and self._local.conn:
            self._local.conn.close()
            self._local.conn = None

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

    def seed_cards(self):
        suits = list(Suit)
        values = list(Value)
        with self._connect() as conn:
            for suit in suits:
                for val in values:
                    conn.execute("INSERT OR IGNORE INTO cards (suit, rank) VALUES (?, ?)", (suit.value, val.value))

    def insert_strategy(self, strategy: Strategy) -> Strategy:
        conn = self._get_conn()
        cursor = conn.execute(
            """INSERT INTO strategies (name, params)
               VALUES (?, ?)
               ON CONFLICT(name, params) DO UPDATE SET name=name
               RETURNING id""",
            (strategy.name, strategy.get_params_json()),
        )
        strategy.id = cursor.fetchone()[0]
        conn.commit()
        return strategy

    def insert_game(self, game: Game) -> Game:
        conn = self._get_conn()
        cursor = conn.execute(
            "INSERT INTO games (num_players, initial_cards_num, winner, total_moves, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (game.num_players, game.initial_cards_num,
             game.winner, game.total_moves, game.created_at.isoformat()),
        )
        game.id = cursor.lastrowid
        conn.commit()
        return game


    def update_game_winner_and_total_moves(self, game_id: int, winner_player_id: int, total_moves: int):
        conn = self._get_conn()
        conn.execute(
            "UPDATE games SET winner = ?, total_moves = ? WHERE id = ?",
            (winner_player_id, total_moves, game_id),
        )
        conn.commit()

    def insert_player(self, player: Player) -> Player:
        conn = self._get_conn()
        cursor = conn.execute(
            "INSERT INTO players (strategy_id, game_id, position) VALUES (?, ?, ?)",
            (player.strategy_id, player.game_id, player.position),
        )
        player.id = cursor.lastrowid
        conn.commit()
        return player


    def insert_moves(self, moves: list[Move]):
        if not moves:
            return
        conn = self._get_conn()
        conn.executemany(
            """INSERT INTO moves
               (game_id, player_id, move_num, action,
                hand_before, hand_after, top_card_before, top_card_after)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [(m.game_id, m.player_id, m.move_num, m.action,
              m.hand_before, m.hand_after, m.top_card_before, m.top_card_after)
             for m in moves],
        )
        conn.commit()


    def insert_game_cards(self, game_cards: list[GameCard]):
        if not game_cards:
            return
        conn = self._get_conn()
        conn.executemany(
            "INSERT OR IGNORE INTO game_cards "
            "(game_id, card_id, location, player_id, move_num) VALUES (?, ?, ?, ?, ?)",
            [(gc.game_id, gc.card_id, gc.location, gc.player_id, gc.move_num)
             for gc in game_cards],
        )
        conn.commit()


    def get_strategy_win_stats(self) -> list[dict]:
        conn = self._get_conn()
        rows = conn.execute("""
            SELECT s.name             AS strategy,
                   COUNT(*)           AS wins,
                   AVG(g.total_moves) AS avg_moves
            FROM games g
            JOIN players p ON p.id = g.winner
            JOIN strategies s ON s.id = p.strategy_id
            GROUP BY s.name
            ORDER BY wins DESC
        """).fetchall()
        return [{"strategy": r[0], "wins": r[1], "avg_moves": r[2]} for r in rows]


            
   