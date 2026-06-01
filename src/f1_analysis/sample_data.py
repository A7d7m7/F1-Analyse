from __future__ import annotations

import math

import numpy as np
import pandas as pd


DEMO_DRIVERS = ["VER", "LEC", "NOR", "HAM"]


def build_demo_laps(
    seed: int = 7,
    season: int = 2024,
    event: str = "Demo Grand Prix",
    session: str = "Race",
) -> pd.DataFrame:
    """Create deterministic race-like lap data for the dashboard demo mode."""
    rng = np.random.default_rng(seed)
    rows: list[dict[str, object]] = []
    race_laps = 58

    driver_profiles = {
        "VER": {"team": "Red Bull Racing", "base": 73.15, "offset": 0.00, "stops": [21, 42]},
        "LEC": {"team": "Ferrari", "base": 73.35, "offset": 0.10, "stops": [19, 40]},
        "NOR": {"team": "McLaren", "base": 73.45, "offset": 0.18, "stops": [24, 43]},
        "HAM": {"team": "Mercedes", "base": 73.70, "offset": 0.30, "stops": [18, 39]},
    }

    compounds = ["MEDIUM", "HARD", "SOFT"]

    for driver, profile in driver_profiles.items():
        stops = profile["stops"]
        stint = 1
        tyre_life = 0
        for lap in range(1, race_laps + 1):
            if lap in stops:
                stint += 1
                tyre_life = 0

            compound = compounds[min(stint - 1, len(compounds) - 1)]
            tyre_life += 1
            degradation = tyre_life * (0.035 + 0.006 * (stint - 1))
            fuel_effect = (race_laps - lap) * 0.018
            traffic = 0.35 if driver == "HAM" and 12 <= lap <= 18 else 0.0
            pit_loss = 21.5 if lap in stops else 0.0
            noise = rng.normal(0, 0.12)
            lap_time = profile["base"] + profile["offset"] + degradation + fuel_effect + traffic + pit_loss + noise

            sector1 = lap_time * 0.315 + rng.normal(0, 0.04)
            sector2 = lap_time * 0.355 + rng.normal(0, 0.04)
            sector3 = lap_time - sector1 - sector2

            rows.append(
                {
                    "Season": season,
                    "EventName": event,
                    "SessionName": session,
                    "LapNumber": lap,
                    "Driver": driver,
                    "Team": profile["team"],
                    "Compound": compound,
                    "Stint": stint,
                    "TyreLife": tyre_life,
                    "LapTimeSeconds": round(float(lap_time), 3),
                    "Sector1Seconds": round(float(sector1), 3),
                    "Sector2Seconds": round(float(sector2), 3),
                    "Sector3Seconds": round(float(sector3), 3),
                    "IsPitLap": lap in stops,
                    "IsAccurate": True,
                }
            )

    return pd.DataFrame(rows)


def build_demo_telemetry(seed: int = 11) -> pd.DataFrame:
    """Create deterministic telemetry curves for the demo fastest laps."""
    rng = np.random.default_rng(seed)
    rows: list[dict[str, object]] = []
    track_length = 5_260
    samples = 420
    distance = np.linspace(0, track_length, samples)

    driver_offsets = {
        "VER": 2.5,
        "LEC": 1.5,
        "NOR": 0.7,
        "HAM": 0.0,
    }

    for driver, offset in driver_offsets.items():
        for idx, dist in enumerate(distance):
            phase = dist / track_length * 2 * math.pi
            braking_zone = max(0.0, math.sin(phase * 4.0 + 0.35)) ** 10
            cornering = max(0.0, math.sin(phase * 7.0 - 0.9)) ** 6
            speed = 258 + offset + 46 * math.sin(phase * 2.1 - 0.4) - 88 * braking_zone - 36 * cornering
            speed += rng.normal(0, 1.2)
            brake = min(100, braking_zone * 115)
            throttle = max(0, min(100, 96 - brake * 0.85 - cornering * 22 + rng.normal(0, 2.0)))
            rpm = 9_800 + speed * 28 + rng.normal(0, 90)
            gear = int(np.clip(np.floor((speed - 70) / 35), 1, 8))
            drs = 1 if 1_150 < dist < 1_820 or 3_750 < dist < 4_420 else 0

            rows.append(
                {
                    "Driver": driver,
                    "LapNumber": 36,
                    "Distance": round(float(dist), 2),
                    "Speed": round(float(speed), 2),
                    "Throttle": round(float(throttle), 2),
                    "Brake": round(float(brake), 2),
                    "RPM": round(float(rpm), 0),
                    "nGear": gear,
                    "DRS": drs,
                    "Sample": idx,
                }
            )

    return pd.DataFrame(rows)


def load_demo_dataset(
    season: int = 2024,
    event: str = "Demo Grand Prix",
    session: str = "Race",
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    laps = build_demo_laps(season=season, event=event, session=session)
    telemetry = build_demo_telemetry()
    metadata = {
        "source": "Demo locale",
        "season": season,
        "event": event,
        "session": session,
        "drivers": DEMO_DRIVERS,
    }
    return laps, telemetry, metadata
