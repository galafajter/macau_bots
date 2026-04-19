from itertools import combinations
from multiprocessing import Pool, cpu_count
from pathlib import Path
from tqdm import tqdm
import uuid


from makao_game import MacauGame
from game_logger import GameLogger
from player import (
    CautiousPlayer, AggressivePlayer, RandomPlayer,
    ThresholdPlayer, DualThresholdPlayer, BalancingPlayer,
    ChangeSuitPlayer
)

# simulation config

STRATEGY_REGISTRY: dict[str, type] = {
    "Cautious": CautiousPlayer,
    "Aggressive": AggressivePlayer,
    "Random": RandomPlayer,
    "Threshold": ThresholdPlayer,
    "DualThreshold": DualThresholdPlayer,
    "Balancing": BalancingPlayer,
    "ChangeSuit": ChangeSuitPlayer,
}

PLAYER_COUNTS   = [3, 4, 5]
SIMULATIONS_PER_CONFIG = 1000
OUTPUT_DIR = Path("./eda/simulation_results")


def generate_configs(
    registry:     dict[str, type],
    player_counts: list[int],
) -> list[list[tuple[str, type]]]:
    """
    Returns list of configurations
    Each configuration is a list of tuples (name, strategy)
    """
    strategy_items = list(registry.items())   # [(name, cls), ...]
    configs = []

    for n in player_counts:
        if n > len(strategy_items):
            # not enough strategies to make combination without replacement
            continue
        for combo in combinations(strategy_items, n):
            configs.append(list(combo))

    return configs


def run_config(args: tuple) -> dict:
    """
    Runs simulation for one configuration.
    Saves results into a json file.
    """
    config, n_sims, output_dir = args

    names = [name for name, _ in config]
    config_label = "_vs_".join(names)

    filename    = output_dir / f"{config_label}.json"
    output_dir.mkdir(parents=True, exist_ok=True)

    players = [cls(name) for name, cls in config]

    for game_id in range(n_sims):

        logger = GameLogger()
        game   = MacauGame(players=players)
        game.play(game_id, logger, filename)

        # rotate players list to assure that every player starts game approx same number of times
        players = players[-1:] + players[:-1]


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    configs = generate_configs(STRATEGY_REGISTRY, PLAYER_COUNTS)
    print(f"Total number of configurations: {len(configs)}")
    print(f"Total number of games: {len(configs) * SIMULATIONS_PER_CONFIG:,}")

    worker_args = [
        (cfg, SIMULATIONS_PER_CONFIG, OUTPUT_DIR)
        for cfg in configs
    ]

    results = []
    with Pool(processes=cpu_count()) as pool:
        for result in tqdm(
            pool.imap_unordered(run_config, worker_args),
            total=len(worker_args),
            desc="Configurations",
        ):
            results.append(result)

