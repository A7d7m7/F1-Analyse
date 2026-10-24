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
    prepared = prepared.sort_values(["Driver", "LapNumber"]).reset_index(drop=True)
    prepared["LapNumber"] = prepared["LapNumber"].astype(int)
    prepared["LapTimeSeconds"] = prepared["LapTimeSeconds"].astype(float)
    prepared["LapTimeFormatted"] = prepared["LapTimeSeconds"].map(format_lap_time)

    if "IsPitLap" not in prepared:
        prepared["IsPitLap"] = False
    prepared["IsPitLap"] = prepared["IsPitLap"].fillna(False).astype(bool)

    for flag in ["IsPitInLap", "IsPitOutLap"]:
        if flag not in prepared:
            prepared[flag] = prepared["IsPitLap"] if flag == "IsPitInLap" else False
        prepared[flag] = prepared[flag].fillna(False).astype(bool)
    status = prepared.get("TrackStatus", pd.Series("", index=prepared.index)).fillna("").astype(str)
    accurate = prepared.get("IsAccurate", pd.Series(False, index=prepared.index)).fillna(False)
    deleted = prepared.get("Deleted", pd.Series(False, index=prepared.index)).fillna(False)
    prepared["IsCleanLap"] = (
        ~prepared["IsPitLap"] & accurate & ~deleted
        & status.eq("1") & prepared["LapTimeSeconds"].gt(0)
    )
    unverified = prepared.get("PaceMode", pd.Series("clean", index=prepared.index)).eq("unverified")
    prepared["IsPaceLap"] = prepared["IsCleanLap"] | (unverified & ~prepared["IsPitLap"] & prepared["LapTimeSeconds"].gt(0))
    clean_times = prepared["LapTimeSeconds"].where(prepared["IsPaceLap"])
    prepared["CleanLapTime"] = clean_times
    prepared["BestLapSeconds"] = prepared.groupby("Driver")["LapTimeSeconds"].transform("min")
    prepared["DeltaToDriverBest"] = prepared["LapTimeSeconds"] - prepared["BestLapSeconds"]
    prepared["RollingPace3"] = (
        prepared.sort_values(["Driver", "LapNumber"])
        .groupby("Driver")["CleanLapTime"]
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

    summary = prepared.groupby("Driver").agg(
        Team=("Team", "first"), Laps=("LapNumber", "max"),
        BestLapSeconds=("CleanLapTime", "min"), MedianPaceSeconds=("CleanLapTime", "median"),
        AveragePaceSeconds=("CleanLapTime", "mean"), CleanLaps=("IsCleanLap", "sum"),
        PitStops=("IsPitInLap", "sum"), RaceTimeSeconds=("CumulativeRaceTime", "last"),
    ).reset_index()
    for column in ["OfficialPosition", "ResultStatus", "OfficialLaps", "OfficialPitStops", "OfficialRaceTimeSeconds"]:
        if column in prepared:
            summary = summary.merge(prepared.groupby("Driver")[column].first(), on="Driver", how="left")
    if "OfficialLaps" in summary:
        summary["Laps"] = summary["OfficialLaps"]
        summary["PitStops"] = summary["OfficialPitStops"]
    if "OfficialPosition" not in summary:
        summary["OfficialPosition"] = np.nan
    if "ResultStatus" not in summary:
        summary["ResultStatus"] = "Inconnu"
    summary = summary.sort_values(["OfficialPosition", "Laps", "RaceTimeSeconds"], ascending=[True, False, True], na_position="last")
    leader = summary.iloc[0] if len(summary) else None
    summary["LapsBehind"] = (leader["Laps"] - summary["Laps"]) if leader is not None else 0
    # A partial sum is never a race gap: missing timing invalidates the comparison.
    complete = prepared.groupby("Driver").apply(
        lambda g: g["LapTimeSeconds"].notna().all() and set(g["LapNumber"]) == set(range(1, int(g["LapNumber"].max()) + 1)),
        include_groups=False,
    )
    valid = summary["Driver"].map(complete).fillna(False)
    leader_valid = bool(complete.get(leader["Driver"], False)) if leader is not None else False
    summary["GapToLeaderSeconds"] = (summary["RaceTimeSeconds"] - leader["RaceTimeSeconds"]).where(
        summary["LapsBehind"].eq(0) & valid & leader_valid
    ) if leader is not None else np.nan
    if "OfficialRaceTimeSeconds" in summary:
        official = summary["OfficialRaceTimeSeconds"] - summary.iloc[0]["OfficialRaceTimeSeconds"]
        summary["GapToLeaderSeconds"] = official.where(summary["LapsBehind"].eq(0))
    summary["Gap"] = summary.apply(lambda r: f"+{int(r.LapsBehind)} tour(s)" if r.LapsBehind > 0 else (f"{r.GapToLeaderSeconds:+.3f} s" if pd.notna(r.GapToLeaderSeconds) else "Indisponible"), axis=1)
    for target, source in [("BestLap", "BestLapSeconds"), ("MedianPace", "MedianPaceSeconds"), ("RaceTime", "RaceTimeSeconds")]:
        summary[target] = summary[source].map(format_lap_time)
    return summary


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
        clean = ordered[ordered["IsCleanLap"]]
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
        return np.nan
    x = stint_laps["LapNumber"].astype(float).to_numpy()
    y = stint_laps["LapTimeSeconds"].astype(float).to_numpy()
    if np.isclose(x.max(), x.min()):
        return np.nan
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

    for driver in pivot:
        group = prepared[prepared["Driver"].eq(driver)]
        invalid = group["LapTimeSeconds"].isna() | group["LapNumber"].diff().fillna(group["LapNumber"]).ne(1)
        if invalid.any():
            pivot.loc[pivot.index >= group.loc[invalid, "LapNumber"].min(), driver] = np.nan
    gaps = pivot.subtract(pivot[reference_driver], axis=0)
    gaps = gaps.reset_index().melt(id_vars="LapNumber", var_name="Driver", value_name="GapSeconds")
    return gaps.dropna()


def driver_options(laps: pd.DataFrame) -> list[str]:
    if "Driver" not in laps:
        return []
    return sorted(str(driver) for driver in laps["Driver"].dropna().unique())
