from __future__ import annotations

import numpy as np
import pandas as pd


def format_lap_time(seconds: float | int | None) -> str:
    if seconds is None or pd.isna(seconds):
        return "-"
    minutes = int(seconds // 60)
    remaining = float(seconds) - minutes * 60
    return f"{minutes}:{remaining:06.3f}"


def prepare_laps(laps: pd.DataFrame) -> pd.DataFrame:
    required = {"LapNumber", "Driver", "LapTimeSeconds"}
    missing = required - set(laps.columns)
    if missing:
        raise ValueError(f"Missing required lap columns: {sorted(missing)}")

    prepared = laps.copy()
    prepared = prepared[pd.notna(prepared["LapTimeSeconds"])]
    prepared["LapNumber"] = prepared["LapNumber"].astype(int)
    prepared["LapTimeSeconds"] = prepared["LapTimeSeconds"].astype(float)
    prepared["LapTimeFormatted"] = prepared["LapTimeSeconds"].map(format_lap_time)

    if "IsPitLap" not in prepared:
        prepared["IsPitLap"] = False
    prepared["IsPitLap"] = prepared["IsPitLap"].fillna(False).astype(bool)

    prepared["BestLapSeconds"] = prepared.groupby("Driver")["LapTimeSeconds"].transform("min")
    prepared["DeltaToDriverBest"] = prepared["LapTimeSeconds"] - prepared["BestLapSeconds"]
    prepared["RollingPace3"] = (
        prepared.sort_values(["Driver", "LapNumber"])
        .groupby("Driver")["LapTimeSeconds"]
        .transform(lambda values: values.rolling(3, min_periods=1).median())
    )
    prepared["CumulativeRaceTime"] = (
        prepared.sort_values(["Driver", "LapNumber"])
        .groupby("Driver")["LapTimeSeconds"]
        .cumsum()
    )
    return prepared


def race_summary(laps: pd.DataFrame) -> pd.DataFrame:
    prepared = prepare_laps(laps)

    summary = (
        prepared.groupby("Driver")
        .agg(
            Team=("Team", "first"),
            Laps=("LapNumber", "count"),
            BestLapSeconds=("LapTimeSeconds", "min"),
            MedianPaceSeconds=("LapTimeSeconds", "median"),
            AveragePaceSeconds=("LapTimeSeconds", "mean"),
            PitStops=("IsPitLap", "sum"),
            RaceTimeSeconds=("CumulativeRaceTime", "max"),
        )
        .reset_index()
    )
    leader_time = summary["RaceTimeSeconds"].min()
    summary["GapToLeaderSeconds"] = summary["RaceTimeSeconds"] - leader_time
    summary["BestLap"] = summary["BestLapSeconds"].map(format_lap_time)
    summary["MedianPace"] = summary["MedianPaceSeconds"].map(format_lap_time)
    summary["RaceTime"] = summary["RaceTimeSeconds"].map(format_lap_time)
    return summary.sort_values("RaceTimeSeconds")


def stint_summary(laps: pd.DataFrame) -> pd.DataFrame:
    prepared = prepare_laps(laps)
    if "Stint" not in prepared:
        prepared["Stint"] = 1
    if "Compound" not in prepared:
        prepared["Compound"] = "UNKNOWN"
    if "TyreLife" not in prepared:
        prepared["TyreLife"] = prepared.groupby(["Driver", "Stint"]).cumcount() + 1

    rows: list[dict[str, object]] = []
    for (driver, stint), group in prepared.groupby(["Driver", "Stint"]):
        ordered = group.sort_values("LapNumber")
        clean = ordered[~ordered["IsPitLap"]]
        degradation = calculate_degradation(clean)
        rows.append(
            {
                "Driver": driver,
                "Stint": int(stint),
                "Compound": ordered["Compound"].dropna().iloc[0] if ordered["Compound"].notna().any() else "UNKNOWN",
                "StartLap": int(ordered["LapNumber"].min()),
                "EndLap": int(ordered["LapNumber"].max()),
                "Laps": int(ordered["LapNumber"].count()),
                "AveragePaceSeconds": float(clean["LapTimeSeconds"].mean()) if not clean.empty else np.nan,
                "DegradationPerLap": degradation,
            }
        )

    result = pd.DataFrame(rows)
    if result.empty:
        return result
    result["AveragePace"] = result["AveragePaceSeconds"].map(format_lap_time)
    return result.sort_values(["Driver", "Stint"])


def calculate_degradation(stint_laps: pd.DataFrame) -> float:
    if len(stint_laps) < 4:
        return 0.0
    x = stint_laps["LapNumber"].astype(float).to_numpy()
    y = stint_laps["LapTimeSeconds"].astype(float).to_numpy()
    if np.isclose(x.max(), x.min()):
        return 0.0
    slope = np.polyfit(x, y, 1)[0]
    return round(float(slope), 4)


def cumulative_gap(laps: pd.DataFrame, reference_driver: str) -> pd.DataFrame:
    prepared = prepare_laps(laps)
    pivot = prepared.pivot_table(
        index="LapNumber",
        columns="Driver",
        values="CumulativeRaceTime",
        aggfunc="min",
    ).sort_index()
    if reference_driver not in pivot:
        raise ValueError(f"Reference driver {reference_driver!r} is not available")

    gaps = pivot.subtract(pivot[reference_driver], axis=0)
    gaps = gaps.reset_index().melt(id_vars="LapNumber", var_name="Driver", value_name="GapSeconds")
    return gaps.dropna()


def driver_options(laps: pd.DataFrame) -> list[str]:
    if "Driver" not in laps:
        return []
    return sorted(str(driver) for driver in laps["Driver"].dropna().unique())
