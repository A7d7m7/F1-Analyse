from __future__ import annotations

from typing import TypedDict

from f1_analysis.config import CACHE_DIR


class EventOption(TypedDict):
    round: int
    name: str
    location: str
    country: str


FALLBACK_EVENTS_BY_SEASON: dict[int, tuple[tuple[int, str, str, str], ...]] = {
    2018: (
        (1, "Australian Grand Prix", "Melbourne", "Australia"),
        (2, "Bahrain Grand Prix", "Sakhir", "Bahrain"),
        (3, "Chinese Grand Prix", "Shanghai", "China"),
        (4, "Azerbaijan Grand Prix", "Baku", "Azerbaijan"),
        (5, "Spanish Grand Prix", "Barcelona", "Spain"),
        (6, "Monaco Grand Prix", "Monaco", "Monaco"),
        (7, "Canadian Grand Prix", "Montreal", "Canada"),
        (8, "French Grand Prix", "Le Castellet", "France"),
        (9, "Austrian Grand Prix", "Spielberg", "Austria"),
        (10, "British Grand Prix", "Silverstone", "Great Britain"),
        (11, "German Grand Prix", "Hockenheim", "Germany"),
        (12, "Hungarian Grand Prix", "Budapest", "Hungary"),
        (13, "Belgian Grand Prix", "Spa-Francorchamps", "Belgium"),
        (14, "Italian Grand Prix", "Monza", "Italy"),
        (15, "Singapore Grand Prix", "Singapore", "Singapore"),
        (16, "Russian Grand Prix", "Sochi", "Russia"),
        (17, "Japanese Grand Prix", "Suzuka", "Japan"),
        (18, "United States Grand Prix", "Austin", "United States"),
        (19, "Mexican Grand Prix", "Mexico City", "Mexico"),
        (20, "Brazilian Grand Prix", "Sao Paulo", "Brazil"),
        (21, "Abu Dhabi Grand Prix", "Yas Island", "United Arab Emirates"),
    ),
    2019: (
        (1, "Australian Grand Prix", "Melbourne", "Australia"),
        (2, "Bahrain Grand Prix", "Sakhir", "Bahrain"),
        (3, "Chinese Grand Prix", "Shanghai", "China"),
        (4, "Azerbaijan Grand Prix", "Baku", "Azerbaijan"),
        (5, "Spanish Grand Prix", "Barcelona", "Spain"),
        (6, "Monaco Grand Prix", "Monaco", "Monaco"),
        (7, "Canadian Grand Prix", "Montreal", "Canada"),
        (8, "French Grand Prix", "Le Castellet", "France"),
        (9, "Austrian Grand Prix", "Spielberg", "Austria"),
        (10, "British Grand Prix", "Silverstone", "Great Britain"),
        (11, "German Grand Prix", "Hockenheim", "Germany"),
        (12, "Hungarian Grand Prix", "Budapest", "Hungary"),
        (13, "Belgian Grand Prix", "Spa-Francorchamps", "Belgium"),
        (14, "Italian Grand Prix", "Monza", "Italy"),
        (15, "Singapore Grand Prix", "Singapore", "Singapore"),
        (16, "Russian Grand Prix", "Sochi", "Russia"),
        (17, "Japanese Grand Prix", "Suzuka", "Japan"),
        (18, "Mexican Grand Prix", "Mexico City", "Mexico"),
        (19, "United States Grand Prix", "Austin", "United States"),
        (20, "Brazilian Grand Prix", "Sao Paulo", "Brazil"),
        (21, "Abu Dhabi Grand Prix", "Yas Island", "United Arab Emirates"),
    ),
    2020: (
        (1, "Austrian Grand Prix", "Spielberg", "Austria"),
        (2, "Styrian Grand Prix", "Spielberg", "Austria"),
        (3, "Hungarian Grand Prix", "Budapest", "Hungary"),
        (4, "British Grand Prix", "Silverstone", "Great Britain"),
        (5, "70th Anniversary Grand Prix", "Silverstone", "Great Britain"),
        (6, "Spanish Grand Prix", "Barcelona", "Spain"),
        (7, "Belgian Grand Prix", "Spa-Francorchamps", "Belgium"),
        (8, "Italian Grand Prix", "Monza", "Italy"),
        (9, "Tuscan Grand Prix", "Mugello", "Italy"),
        (10, "Russian Grand Prix", "Sochi", "Russia"),
        (11, "Eifel Grand Prix", "Nurburgring", "Germany"),
        (12, "Portuguese Grand Prix", "Portimao", "Portugal"),
        (13, "Emilia Romagna Grand Prix", "Imola", "Italy"),
        (14, "Turkish Grand Prix", "Istanbul", "Turkey"),
        (15, "Bahrain Grand Prix", "Sakhir", "Bahrain"),
        (16, "Sakhir Grand Prix", "Sakhir", "Bahrain"),
        (17, "Abu Dhabi Grand Prix", "Yas Island", "United Arab Emirates"),
    ),
    2021: (
        (1, "Bahrain Grand Prix", "Sakhir", "Bahrain"),
        (2, "Emilia Romagna Grand Prix", "Imola", "Italy"),
        (3, "Portuguese Grand Prix", "Portimao", "Portugal"),
        (4, "Spanish Grand Prix", "Barcelona", "Spain"),
        (5, "Monaco Grand Prix", "Monaco", "Monaco"),
        (6, "Azerbaijan Grand Prix", "Baku", "Azerbaijan"),
        (7, "French Grand Prix", "Le Castellet", "France"),
        (8, "Styrian Grand Prix", "Spielberg", "Austria"),
        (9, "Austrian Grand Prix", "Spielberg", "Austria"),
        (10, "British Grand Prix", "Silverstone", "Great Britain"),
        (11, "Hungarian Grand Prix", "Budapest", "Hungary"),
        (12, "Belgian Grand Prix", "Spa-Francorchamps", "Belgium"),
        (13, "Dutch Grand Prix", "Zandvoort", "Netherlands"),
        (14, "Italian Grand Prix", "Monza", "Italy"),
        (15, "Russian Grand Prix", "Sochi", "Russia"),
        (16, "Turkish Grand Prix", "Istanbul", "Turkey"),
        (17, "United States Grand Prix", "Austin", "United States"),
        (18, "Mexico City Grand Prix", "Mexico City", "Mexico"),
        (19, "Sao Paulo Grand Prix", "Sao Paulo", "Brazil"),
        (20, "Qatar Grand Prix", "Lusail", "Qatar"),
        (21, "Saudi Arabian Grand Prix", "Jeddah", "Saudi Arabia"),
        (22, "Abu Dhabi Grand Prix", "Yas Island", "United Arab Emirates"),
    ),
    2022: (
        (1, "Bahrain Grand Prix", "Sakhir", "Bahrain"),
        (2, "Saudi Arabian Grand Prix", "Jeddah", "Saudi Arabia"),
        (3, "Australian Grand Prix", "Melbourne", "Australia"),
        (4, "Emilia Romagna Grand Prix", "Imola", "Italy"),
        (5, "Miami Grand Prix", "Miami", "United States"),
        (6, "Spanish Grand Prix", "Barcelona", "Spain"),
        (7, "Monaco Grand Prix", "Monaco", "Monaco"),
        (8, "Azerbaijan Grand Prix", "Baku", "Azerbaijan"),
        (9, "Canadian Grand Prix", "Montreal", "Canada"),
        (10, "British Grand Prix", "Silverstone", "Great Britain"),
        (11, "Austrian Grand Prix", "Spielberg", "Austria"),
        (12, "French Grand Prix", "Le Castellet", "France"),
        (13, "Hungarian Grand Prix", "Budapest", "Hungary"),
        (14, "Belgian Grand Prix", "Spa-Francorchamps", "Belgium"),
        (15, "Dutch Grand Prix", "Zandvoort", "Netherlands"),
        (16, "Italian Grand Prix", "Monza", "Italy"),
        (17, "Singapore Grand Prix", "Singapore", "Singapore"),
        (18, "Japanese Grand Prix", "Suzuka", "Japan"),
        (19, "United States Grand Prix", "Austin", "United States"),
        (20, "Mexico City Grand Prix", "Mexico City", "Mexico"),
        (21, "Sao Paulo Grand Prix", "Sao Paulo", "Brazil"),
        (22, "Abu Dhabi Grand Prix", "Yas Island", "United Arab Emirates"),
    ),
    2023: (
        (1, "Bahrain Grand Prix", "Sakhir", "Bahrain"),
        (2, "Saudi Arabian Grand Prix", "Jeddah", "Saudi Arabia"),
        (3, "Australian Grand Prix", "Melbourne", "Australia"),
        (4, "Azerbaijan Grand Prix", "Baku", "Azerbaijan"),
        (5, "Miami Grand Prix", "Miami", "United States"),
        (6, "Monaco Grand Prix", "Monaco", "Monaco"),
        (7, "Spanish Grand Prix", "Barcelona", "Spain"),
        (8, "Canadian Grand Prix", "Montreal", "Canada"),
        (9, "Austrian Grand Prix", "Spielberg", "Austria"),
        (10, "British Grand Prix", "Silverstone", "Great Britain"),
        (11, "Hungarian Grand Prix", "Budapest", "Hungary"),
        (12, "Belgian Grand Prix", "Spa-Francorchamps", "Belgium"),
        (13, "Dutch Grand Prix", "Zandvoort", "Netherlands"),
        (14, "Italian Grand Prix", "Monza", "Italy"),
        (15, "Singapore Grand Prix", "Singapore", "Singapore"),
        (16, "Japanese Grand Prix", "Suzuka", "Japan"),
        (17, "Qatar Grand Prix", "Lusail", "Qatar"),
        (18, "United States Grand Prix", "Austin", "United States"),
        (19, "Mexico City Grand Prix", "Mexico City", "Mexico"),
        (20, "Sao Paulo Grand Prix", "Sao Paulo", "Brazil"),
        (21, "Las Vegas Grand Prix", "Las Vegas", "United States"),
        (22, "Abu Dhabi Grand Prix", "Yas Island", "United Arab Emirates"),
    ),
    2024: (
        (1, "Bahrain Grand Prix", "Sakhir", "Bahrain"),
        (2, "Saudi Arabian Grand Prix", "Jeddah", "Saudi Arabia"),
        (3, "Australian Grand Prix", "Melbourne", "Australia"),
        (4, "Japanese Grand Prix", "Suzuka", "Japan"),
        (5, "Chinese Grand Prix", "Shanghai", "China"),
        (6, "Miami Grand Prix", "Miami", "United States"),
        (7, "Emilia Romagna Grand Prix", "Imola", "Italy"),
        (8, "Monaco Grand Prix", "Monaco", "Monaco"),
        (9, "Canadian Grand Prix", "Montreal", "Canada"),
        (10, "Spanish Grand Prix", "Barcelona", "Spain"),
        (11, "Austrian Grand Prix", "Spielberg", "Austria"),
        (12, "British Grand Prix", "Silverstone", "Great Britain"),
        (13, "Hungarian Grand Prix", "Budapest", "Hungary"),
        (14, "Belgian Grand Prix", "Spa-Francorchamps", "Belgium"),
        (15, "Dutch Grand Prix", "Zandvoort", "Netherlands"),
        (16, "Italian Grand Prix", "Monza", "Italy"),
        (17, "Azerbaijan Grand Prix", "Baku", "Azerbaijan"),
        (18, "Singapore Grand Prix", "Singapore", "Singapore"),
        (19, "United States Grand Prix", "Austin", "United States"),
        (20, "Mexico City Grand Prix", "Mexico City", "Mexico"),
        (21, "Sao Paulo Grand Prix", "Sao Paulo", "Brazil"),
        (22, "Las Vegas Grand Prix", "Las Vegas", "United States"),
        (23, "Qatar Grand Prix", "Lusail", "Qatar"),
        (24, "Abu Dhabi Grand Prix", "Yas Island", "United Arab Emirates"),
    ),
    2025: (
        (1, "Australian Grand Prix", "Melbourne", "Australia"),
        (2, "Chinese Grand Prix", "Shanghai", "China"),
        (3, "Japanese Grand Prix", "Suzuka", "Japan"),
        (4, "Bahrain Grand Prix", "Sakhir", "Bahrain"),
        (5, "Saudi Arabian Grand Prix", "Jeddah", "Saudi Arabia"),
        (6, "Miami Grand Prix", "Miami", "United States"),
        (7, "Emilia Romagna Grand Prix", "Imola", "Italy"),
        (8, "Monaco Grand Prix", "Monaco", "Monaco"),
        (9, "Spanish Grand Prix", "Barcelona", "Spain"),
        (10, "Canadian Grand Prix", "Montreal", "Canada"),
        (11, "Austrian Grand Prix", "Spielberg", "Austria"),
        (12, "British Grand Prix", "Silverstone", "Great Britain"),
        (13, "Belgian Grand Prix", "Spa-Francorchamps", "Belgium"),
        (14, "Hungarian Grand Prix", "Budapest", "Hungary"),
        (15, "Dutch Grand Prix", "Zandvoort", "Netherlands"),
        (16, "Italian Grand Prix", "Monza", "Italy"),
        (17, "Azerbaijan Grand Prix", "Baku", "Azerbaijan"),
        (18, "Singapore Grand Prix", "Singapore", "Singapore"),
        (19, "United States Grand Prix", "Austin", "United States"),
        (20, "Mexico City Grand Prix", "Mexico City", "Mexico"),
        (21, "Sao Paulo Grand Prix", "Sao Paulo", "Brazil"),
        (22, "Las Vegas Grand Prix", "Las Vegas", "United States"),
        (23, "Qatar Grand Prix", "Lusail", "Qatar"),
        (24, "Abu Dhabi Grand Prix", "Yas Island", "United Arab Emirates"),
    ),
    2026: (
        (1, "Australian Grand Prix", "Melbourne", "Australia"),
        (2, "Chinese Grand Prix", "Shanghai", "China"),
        (3, "Japanese Grand Prix", "Suzuka", "Japan"),
        (4, "Bahrain Grand Prix", "Sakhir", "Bahrain"),
        (5, "Saudi Arabian Grand Prix", "Jeddah", "Saudi Arabia"),
        (6, "Miami Grand Prix", "Miami", "United States"),
        (7, "Canadian Grand Prix", "Montreal", "Canada"),
        (8, "Monaco Grand Prix", "Monaco", "Monaco"),
        (9, "Spanish Grand Prix", "Barcelona-Catalunya", "Spain"),
        (10, "Austrian Grand Prix", "Spielberg", "Austria"),
        (11, "British Grand Prix", "Silverstone", "Great Britain"),
        (12, "Belgian Grand Prix", "Spa-Francorchamps", "Belgium"),
        (13, "Hungarian Grand Prix", "Budapest", "Hungary"),
        (14, "Dutch Grand Prix", "Zandvoort", "Netherlands"),
        (15, "Italian Grand Prix", "Monza", "Italy"),
        (16, "Madrid Grand Prix", "Madrid", "Spain"),
        (17, "Azerbaijan Grand Prix", "Baku", "Azerbaijan"),
        (18, "Singapore Grand Prix", "Singapore", "Singapore"),
        (19, "United States Grand Prix", "Austin", "United States"),
        (20, "Mexico City Grand Prix", "Mexico City", "Mexico"),
        (21, "Sao Paulo Grand Prix", "Sao Paulo", "Brazil"),
        (22, "Las Vegas Grand Prix", "Las Vegas", "United States"),
        (23, "Qatar Grand Prix", "Lusail", "Qatar"),
        (24, "Abu Dhabi Grand Prix", "Yas Marina", "United Arab Emirates"),
    ),
}


def available_seasons() -> list[int]:
    return sorted(FALLBACK_EVENTS_BY_SEASON.keys(), reverse=True)


def event_options_for_season(season: int) -> list[EventOption]:
    """Return events for a season, preferring bundled calendars for stable UI behavior."""
    fallback_events = _fallback_event_options(season)
    if fallback_events:
        return fallback_events

    try:
        events = _fastf1_event_options(season)
    except Exception:
        events = []

    return events


def format_event_option(event: EventOption) -> str:
    return f"R{event['round']:02d} - {event['name']} ({event['location']})"


def _fastf1_event_options(season: int) -> list[EventOption]:
    import fastf1

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(CACHE_DIR))
    schedule = fastf1.get_event_schedule(season, include_testing=False)
    if schedule.empty:
        return []

    options: list[EventOption] = []
    for _, row in schedule.sort_values("RoundNumber").iterrows():
        round_number = int(row["RoundNumber"])
        if round_number <= 0:
            continue
        options.append(
            {
                "round": round_number,
                "name": str(row["EventName"]),
                "location": str(row.get("Location", "")),
                "country": str(row.get("Country", "")),
            }
        )
    return options


def _fallback_event_options(season: int) -> list[EventOption]:
    return [
        {"round": round_number, "name": name, "location": location, "country": country}
        for round_number, name, location, country in FALLBACK_EVENTS_BY_SEASON.get(season, ())
    ]
