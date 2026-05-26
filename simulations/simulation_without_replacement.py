from itertools import combinations
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

from makao_game import MacauGame
from game_logger import GameLogger
from database.database import MacauDatabase
from player import (
    CautiousPlayer, AggressivePlayer, RandomPlayer,
    ThresholdPlayer, DualThresholdPlayer, BalancingPlayer,
    ChangeSuitPlayer,
)

# Configuration
STRATEGY_REGISTRY: dict[str, type] = {
    "Cautious":      CautiousPlayer,
    "Aggressive":    AggressivePlayer,
    "Random":        RandomPlayer,
    "Threshold":     ThresholdPlayer,
    "DualThreshold": DualThresholdPlayer,
    "Balancing":     BalancingPlayer,
    "ChangeSuit":    ChangeSuitPlayer,
}

PLAYER_COUNTS          = [3, 4, 5]
SIMULATIONS_PER_CONFIG = 1000
DB_PATH                = "../macau-without-replacement.db"
N_CARDS                = 5



def run_config(args: tuple) -> None:
    config, n_sims, db_path, n_cards = args

    # Każdy proces tworzy WŁASNE połączenie – zero konfliktów
    db = MacauDatabase(db_path)

    players = [cls(name) for name, cls in config]

    for _ in range(n_sims):
        game   = MacauGame(players=players, number_of_cards_per_player=n_cards)
        logger = GameLogger(db_instance=db)
        game.play(logger)
        # rotacja: każdy gracz zaczyna tyle samo razy
        players = players[-1:] + players[:-1]

    db.close()


def generate_configs(registry, player_counts):
    items = list(registry.items())
    configs = []
    for n in player_counts:
        if n > len(items):
            continue
        for combo in combinations(items, n):
            configs.append(list(combo))
    return configs


if __name__ == "__main__":
    db = MacauDatabase(DB_PATH)
    db.seed_cards()
    db.close()

    configs = generate_configs(STRATEGY_REGISTRY, PLAYER_COUNTS)
    total_games = len(configs) * SIMULATIONS_PER_CONFIG
    print(f"Konfiguracji:       {len(configs)}")
    print(f"Łączna liczba gier: {total_games:,}")

    worker_args = [
        (cfg, SIMULATIONS_PER_CONFIG, DB_PATH, N_CARDS)
        for cfg in configs
    ]

    with Pool(processes=cpu_count()) as pool:
        for _ in tqdm(
            pool.imap_unordered(run_config, worker_args),
            total=len(worker_args),
            desc="Configurations",
        ):
            pass
