from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"

DEFAULT_SEASON = 2024
DEFAULT_EVENT = "Monaco Grand Prix"
DEFAULT_SESSION = "R"

SESSION_LABELS = {
    "Race": "R",
    "Qualifying": "Q",
    "Sprint": "S",
    "Practice 1": "FP1",
    "Practice 2": "FP2",
    "Practice 3": "FP3",
}

DRIVER_COLORS = {
    "VER": "#3671C6",
    "PER": "#3671C6",
    "LEC": "#E8002D",
    "SAI": "#E8002D",
    "HAM": "#27F4D2",
    "RUS": "#27F4D2",
    "NOR": "#FF8000",
    "PIA": "#FF8000",
    "ALO": "#229971",
    "STR": "#229971",
    "OCO": "#0090FF",
    "GAS": "#0090FF",
}

COMPOUND_COLORS = {
    "SOFT": "#da291c",
    "MEDIUM": "#ffd12e",
    "HARD": "#f4f4f4",
    "INTERMEDIATE": "#43b02a",
    "WET": "#0067ad",
    "UNKNOWN": "#9ca3af",
}
