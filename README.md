# macau_bots

Silnik gry karcianej **Makao** (Macau) w Pythonie z botami, symulacjami Monte-Carlo
i pełną historią partii w SQLite (pod analizy EDA / przyszłe UCzenie ze wzmocnieniem).

## Zaimplementowane zasady

Jedno źródło prawdy o kartach: [`core/rules.py`](core/rules.py).

| Karta | Efekt |
|---|---|
| 2, 3 | **Wojna** — kara dobierania (kumuluje się), obrona kartą wojenną lub Damą |
| 4 | **Blokada** — następny gracz pauzuje 1 turę na każdą 4 w łańcuchu (obrona: 4, Dama); *bez dobierania* |
| Walet | **Żądanie wartości** (karty pasywnej) — obowiązuje okrążenie |
| Dama | Karta „na wszystko"; niweluje aktywny efekt |
| Król ♥ / ♠ | **Wojna +5**; Król ♦/♣ jest pasywny; ♠ odwraca kierunek gry |
| As | **Żądanie koloru** — obowiązuje okrążenie |

**Szczęśliwa karta**: gdy aktywny jest efekt (wojna / żądanie) i gracz nie ma
odpowiedzi w ręce, dobiera **jedną kartę próbną** — jeśli jest legalną odpowiedzią,
*może* ją położyć (kara + wartość karty przechodzi na następnego gracza).
Szczegóły: `GameMaster._offer_lucky_card`.

**Pat**: gdy talia jest wyczerpana i nikt nie może nic zrobić, partia kończy się
`"stalemate"` (z pełnym zapisem w bazie). Partia nigdy nie wisi w nieskończoność.

## Struktura

```
core/
├── rules.py          # klasyfikacja kart funkcyjnych/pasywnych (jedno źródło prawdy)
├── card.py           # Card, Deck
├── game_state.py     # stan partii (GameState)
├── game_master.py    # silnik: tury, efekty, szczęśliwa karta, blokady
├── macau_game.py     # MacauGame: rozdanie, pętla partii, pat-guard
└── player.py         # interfejs Player + strategie (Random, Aggressive, Cautious, ...)
simulations/         # masowe symulacje (multiprocessing -> SQLite)
database/            # schemat i zapis partii (sqlite3)
logger/              # GameLogger: ruch po ruchu do bazy
tests/               # pytest: reguły, efekty, talia, determinizm, paty (1112 testów)
eda/                 # notebooky analizy danych
```

## Instalacja

Python 3.12+. Zależności:

```
pip install -r requirements.txt          # runtime (tqdm)
pip install -r dev-requirements.txt     # dev: pytest, ruff, mypy
```

## Uruchomienie

```bash
# symulacje (wszystkie konfiguracje par botów, wiele procesów, zapis do SQLite)
python -m simulations.simulation_without_replacement

# pojedyncze partie z przykładowymi botami (własny runner: main w core/macau_game.py)
python -m core.macau_game

# testy (~2 s)
pytest -q

# linter / typy
ruff check .
mypy core logger database simulations   # obecnie informational (docelowo blocking)
```

Bazy SQLite (np. `data/test.db`) trzymają: `games` (zwycięzca, liczba ruchów —
`winner = NULL` oznacza pat), `moves` (ruch po ruchu, ręce, karty stosu),
`game_cards` (pozycje każdej karty w każdym ruchu).

## CI

GitHub Actions (`.github/workflows/ci.yml`): **ruff** i **pytest** blokują PR;
**mypy** na razie informacyjnie (kod typowany stopniowo, patrz `pyproject.toml`).

## Konwencje

- Zasady gry zmienia się **wyłącznie** w `core/rules.py` / `GameMaster` — najpierw regulamin, potem kod.
- Nowa strategia bota = podklasa `Player` z `make_move()`; boty nie dotykają silnika.
- Commitowanie zgodnie z konwencją repo; zmiany przez PR.
