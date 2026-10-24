from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from io import StringIO
import json
import os
from pathlib import Path
import tempfile
import time

import pandas as pd

from f1_analysis.config import CACHE_DIR, SESSION_LABELS
from f1_analysis.sample_data import load_demo_dataset, build_demo_telemetry


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
    if source == "Jolpica":
        if request is None:
            raise ValueError("Une session est nécessaire pour Jolpica.")
        from f1_analysis.jolpica import load_jolpica_dataset
        return load_jolpica_dataset(request)
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
    cached = _read_prepared(request, "laps")
    if cached is not None:
        return cached[0], _empty_telemetry(), cached[1]
    session = _load_session(request, telemetry=False)

    laps = _normalise_laps(session.laps, request, session.event.get("EventName", request.event))
    if not session.results.empty:
        results = session.results[["Abbreviation", "Position", "Status"]].rename(columns={"Abbreviation": "Driver", "Position": "OfficialPosition", "Status": "ResultStatus"})
        laps = laps.merge(results, on="Driver", how="left")
    if "TeamColor" in session.results:
        colors = session.results.set_index("Abbreviation")["TeamColor"]
        laps["TeamColor"] = laps["Driver"].map(colors)
    metadata = {
        "source": "FastF1",
        "season": request.season,
        "event": session.event.get("EventName", request.event),
        "session": request.session_label,
        "drivers": sorted(laps["Driver"].dropna().unique().tolist()),
    }
    _write_prepared(request, "laps", laps, metadata)
    return laps, _empty_telemetry(), metadata


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
        frame["IsPitInLap"] = pit_in.notna()
        frame["IsPitOutLap"] = pit_out.notna()
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
        "IsAccurate", "TrackStatus", "Deleted", "IsPitInLap", "IsPitOutLap",
    ]
    existing = [column for column in columns if column in frame.columns]
    return frame[existing].dropna(subset=["Driver", "LapNumber"])


def _load_fastest_lap_telemetry(session: object, laps: pd.DataFrame) -> pd.DataFrame:
    telemetry_frames: list[pd.DataFrame] = []
    for driver in sorted(laps["Driver"].dropna().unique()):
        try:
            driver_laps = session.laps.pick_drivers(driver).pick_quicklaps()
            fastest_lap = driver_laps.pick_fastest()
            telemetry = fastest_lap.get_car_data().add_distance()
            telemetry["ElapsedSeconds"] = telemetry["Time"].dt.total_seconds()
            telemetry["ElapsedSeconds"] -= telemetry["ElapsedSeconds"].iloc[0]
            telemetry["Driver"] = driver
            telemetry["LapNumber"] = int(fastest_lap["LapNumber"])
            telemetry_frames.append(
                telemetry[
                    [
                        "Driver",
                        "LapNumber",
                        "Distance", "ElapsedSeconds",
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


TELEMETRY_COLUMNS = ["Driver", "LapNumber", "Distance", "ElapsedSeconds", "Speed", "Throttle", "Brake", "RPM", "nGear", "DRS"]
PREPARED_CACHE_VERSION = "v2"
PREPARED_CACHE_TTL = 6 * 3600


def _empty_telemetry():
    return pd.DataFrame(columns=TELEMETRY_COLUMNS)


def _cache_path(request, kind):
    key = sha256(json.dumps([PREPARED_CACHE_VERSION, request.season, request.event, request.fastf1_session_code, kind]).encode()).hexdigest()
    return CACHE_DIR / "prepared" / f"{key}.json"


def _read_prepared(request, kind):
    path = _cache_path(request, kind)
    try:
        if time.time() - path.stat().st_mtime > PREPARED_CACHE_TTL:
            return None
        payload = json.loads(path.read_text())
        return pd.read_json(StringIO(payload["frame"]), orient="table"), payload["metadata"]
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _write_prepared(request, kind, frame, metadata):
    path = _cache_path(request, kind)
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump({"frame": frame.to_json(orient="table", index=False), "metadata": metadata}, handle)
        os.replace(temporary, path)
    except OSError:
        # Cache persistence must never prevent displaying successfully loaded data.
        pass
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _load_session(request, telemetry):
    try:
        import fastf1
    except ImportError as exc:
        raise RuntimeError("FastF1 non installé : installe les dépendances ou utilise la démo.") from exc
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(CACHE_DIR))
    session = fastf1.get_session(request.season, request.event, request.fastf1_session_code)
    session.load(laps=True, telemetry=telemetry, weather=False, messages=True)
    return session


def load_telemetry(source: str, request: SessionRequest, drivers: tuple[str, ...]) -> pd.DataFrame:
    """Load telemetry on demand; persist successful results separately per driver."""
    drivers = tuple(sorted(set(drivers)))
    if not drivers or source == "Jolpica":
        return _empty_telemetry()
    if source == "Demo locale":
        frame = build_demo_telemetry()
        return frame[frame.Driver.isin(drivers)]
    frames, missing = [], []
    for driver in drivers:
        cached = _read_prepared(request, f"telemetry:{driver}")
        if cached is None:
            missing.append(driver)
        else:
            frames.append(cached[0])
    if missing:
        session = _load_session(request, telemetry=True)
        available = session.laps[session.laps.Driver.isin(missing)]
        loaded = _load_fastest_lap_telemetry(session, available)
        if not loaded.empty and "TeamColor" in session.results:
            loaded["TeamColor"] = loaded.Driver.map(session.results.set_index("Abbreviation").TeamColor)
        for driver in missing:
            frame = loaded[loaded.Driver.eq(driver)].copy()
            if not frame.empty:
                _write_prepared(request, f"telemetry:{driver}", frame, {})
                frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else _empty_telemetry()
