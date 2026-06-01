from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from f1_analysis.config import CACHE_DIR, SESSION_LABELS
from f1_analysis.sample_data import load_demo_dataset


@dataclass(frozen=True)
class SessionRequest:
    season: int
    event: str
    session_label: str

    @property
    def fastf1_session_code(self) -> str:
        return SESSION_LABELS.get(self.session_label, self.session_label)


def load_dataset(
    source: str,
    request: SessionRequest | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    if source == "Demo locale":
        if request is None:
            return load_demo_dataset()
        return load_demo_dataset(
            season=request.season,
            event=request.event,
            session=request.session_label,
        )
    if request is None:
        raise ValueError("A SessionRequest is required for FastF1 data")
    return load_fastf1_dataset(request)


def load_fastf1_dataset(request: SessionRequest) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    try:
        import fastf1
    except ImportError as exc:
        raise RuntimeError(
            "FastF1 is not installed. Install project dependencies or use demo mode."
        ) from exc

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(CACHE_DIR))

    session = fastf1.get_session(
        request.season,
        request.event,
        request.fastf1_session_code,
    )
    session.load(laps=True, telemetry=True, weather=False, messages=False)

    laps = _normalise_laps(session.laps, request, session.event.get("EventName", request.event))
    telemetry = _load_fastest_lap_telemetry(session, laps)
    metadata = {
        "source": "FastF1",
        "season": request.season,
        "event": session.event.get("EventName", request.event),
        "session": request.session_label,
        "drivers": sorted(laps["Driver"].dropna().unique().tolist()),
    }
    return laps, telemetry, metadata


def _normalise_laps(laps: pd.DataFrame, request: SessionRequest, event_name: str) -> pd.DataFrame:
    frame = laps.copy()
    frame["Season"] = request.season
    frame["EventName"] = event_name
    frame["SessionName"] = request.session_label
    frame["LapTimeSeconds"] = _timedelta_seconds(frame.get("LapTime"))
    frame["Sector1Seconds"] = _timedelta_seconds(frame.get("Sector1Time"))
    frame["Sector2Seconds"] = _timedelta_seconds(frame.get("Sector2Time"))
    frame["Sector3Seconds"] = _timedelta_seconds(frame.get("Sector3Time"))

    if "PitInTime" in frame or "PitOutTime" in frame:
        pit_in = frame.get("PitInTime", pd.Series(index=frame.index, dtype="object"))
        pit_out = frame.get("PitOutTime", pd.Series(index=frame.index, dtype="object"))
        frame["IsPitLap"] = pit_in.notna() | pit_out.notna()
    else:
        frame["IsPitLap"] = False

    columns = [
        "Season",
        "EventName",
        "SessionName",
        "LapNumber",
        "Driver",
        "Team",
        "Compound",
        "Stint",
        "TyreLife",
        "LapTimeSeconds",
        "Sector1Seconds",
        "Sector2Seconds",
        "Sector3Seconds",
        "IsPitLap",
        "IsAccurate",
    ]
    existing = [column for column in columns if column in frame.columns]
    return frame[existing].dropna(subset=["LapTimeSeconds", "Driver"])


def _load_fastest_lap_telemetry(session: object, laps: pd.DataFrame) -> pd.DataFrame:
    telemetry_frames: list[pd.DataFrame] = []
    for driver in sorted(laps["Driver"].dropna().unique()):
        try:
            driver_laps = session.laps.pick_drivers(driver).pick_quicklaps()
            fastest_lap = driver_laps.pick_fastest()
            telemetry = fastest_lap.get_car_data().add_distance()
            telemetry["Driver"] = driver
            telemetry["LapNumber"] = int(fastest_lap["LapNumber"])
            telemetry_frames.append(
                telemetry[
                    [
                        "Driver",
                        "LapNumber",
                        "Distance",
                        "Speed",
                        "Throttle",
                        "Brake",
                        "RPM",
                        "nGear",
                        "DRS",
                    ]
                ]
            )
        except Exception:
            continue

    if not telemetry_frames:
        return pd.DataFrame(
            columns=["Driver", "LapNumber", "Distance", "Speed", "Throttle", "Brake", "RPM", "nGear", "DRS"]
        )
    return pd.concat(telemetry_frames, ignore_index=True)


def _timedelta_seconds(series: pd.Series | None) -> pd.Series:
    if series is None:
        return pd.Series(dtype="float64")
    if hasattr(series, "dt"):
        return series.dt.total_seconds()
    return pd.to_timedelta(series, errors="coerce").dt.total_seconds()
