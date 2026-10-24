from types import SimpleNamespace
import time
import pandas as pd
from f1_analysis import data_loader as loader


def setup_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(loader, 'CACHE_DIR', tmp_path)
    return loader.SessionRequest(2024, 'Monaco Grand Prix', 'Race')


def test_initial_load_excludes_telemetry_and_reuses_disk(monkeypatch, tmp_path):
    request = setup_cache(monkeypatch, tmp_path)
    calls = []
    laps = pd.DataFrame({'Driver': ['VER'], 'LapNumber': [1], 'Team': ['Red Bull Racing'], 'LapTime': pd.to_timedelta([75], unit='s')})
    def session(request, telemetry):
        calls.append(telemetry)
        return SimpleNamespace(laps=laps, results=pd.DataFrame(), event={})
    monkeypatch.setattr(loader, '_load_session', session)
    first, telemetry, metadata = loader.load_fastf1_dataset(request)
    second, _, _ = loader.load_fastf1_dataset(request)
    assert calls == [False]
    assert telemetry.empty
    pd.testing.assert_frame_equal(first, second)
    assert metadata['source'] == 'FastF1'


def test_telemetry_cache_reused_per_driver(monkeypatch, tmp_path):
    request = setup_cache(monkeypatch, tmp_path)
    loads, extractions = [], []
    def session(request, telemetry):
        loads.append(telemetry)
        return SimpleNamespace(laps=pd.DataFrame({'Driver': ['VER', 'HAM', 'NOR']}), results=pd.DataFrame())
    def extract(session, laps):
        extractions.append(list(laps.Driver))
        return pd.DataFrame({'Driver': laps.Driver.tolist(), 'Distance': [0] * len(laps)})
    monkeypatch.setattr(loader, '_load_session', session)
    monkeypatch.setattr(loader, '_load_fastest_lap_telemetry', extract)
    assert set(loader.load_telemetry('FastF1', request, ('VER', 'HAM')).Driver) == {'VER', 'HAM'}
    assert set(loader.load_telemetry('FastF1', request, ('VER', 'NOR')).Driver) == {'VER', 'NOR'}
    loader.load_telemetry('FastF1', request, ('HAM', 'VER'))
    assert loads == [True, True]
    assert extractions == [['VER', 'HAM'], ['NOR']]


def test_expired_corrupt_and_empty_cache(monkeypatch, tmp_path):
    request = setup_cache(monkeypatch, tmp_path)
    assert loader.load_telemetry('FastF1', request, ()).empty
    path = loader._cache_path(request, 'laps')
    path.parent.mkdir(parents=True)
    path.write_text('invalid json')
    assert loader._read_prepared(request, 'laps') is None
    loader._write_prepared(request, 'laps', pd.DataFrame({'Driver': ['VER']}), {})
    assert loader._read_prepared(request, 'laps') is not None
    monkeypatch.setattr(loader.time, 'time', lambda: path.stat().st_mtime + loader.PREPARED_CACHE_TTL + 1)
    assert loader._read_prepared(request, 'laps') is None


def test_session_flags_disable_weather_and_enable_messages(monkeypatch, tmp_path):
    import sys
    request = setup_cache(monkeypatch, tmp_path)
    flags = []
    fake = SimpleNamespace(Cache=SimpleNamespace(enable_cache=lambda path: None), get_session=lambda *args: SimpleNamespace(load=lambda **kwargs: flags.append(kwargs)))
    monkeypatch.setitem(sys.modules, 'fastf1', fake)
    loader._load_session(request, telemetry=False)
    assert flags == [dict(laps=True, telemetry=False, weather=False, messages=True)]
