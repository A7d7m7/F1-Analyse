import numpy as np
import pandas as pd
import pytest
from f1_analysis.metrics import prepare_laps, race_summary, cumulative_gap
from f1_analysis.sample_data import build_demo_laps, build_demo_telemetry
from f1_analysis.comparison import telemetry_delta, simulate_strategy
from f1_analysis.report import build_report


def test_retirement_and_lapped_driver_never_lead_on_shorter_time():
    laps = build_demo_laps()
    laps = laps[~((laps.Driver.eq('HAM') & laps.LapNumber.gt(10)) | (laps.Driver.eq('NOR') & laps.LapNumber.gt(57)))]
    result = race_summary(laps).set_index('Driver')
    assert result.index[0] in ['VER', 'LEC']
    assert np.isnan(result.loc['HAM', 'GapToLeaderSeconds'])
    assert result.loc['NOR', 'LapsBehind'] == 1


def test_filters_and_pit_count():
    laps = build_demo_laps()
    frame = prepare_laps(laps)
    assert not frame.loc[frame.TrackStatus.eq('4'), 'IsCleanLap'].any()
    assert not frame.loc[frame.IsPitOutLap, 'IsCleanLap'].any()
    assert race_summary(laps).PitStops.sum() == 8
    laps['TrackStatus'] = None
    assert not prepare_laps(laps).IsCleanLap.any()


def test_official_position_and_missing_timing():
    laps = build_demo_laps()
    laps['OfficialPosition'] = laps.Driver.map({'HAM': 1, 'VER': 2, 'LEC': 3, 'NOR': 4})
    assert race_summary(laps).iloc[0].Driver == 'HAM'
    laps.loc[laps.Driver.eq('VER') & laps.LapNumber.eq(5), 'LapTimeSeconds'] = np.nan
    gaps = cumulative_gap(laps, 'LEC')
    assert gaps.loc[gaps.Driver.eq('VER'), 'LapNumber'].max() == 4
    assert race_summary(laps).set_index('Driver').loc['VER', 'Laps'] == 58


def test_telemetry_identity_and_known_delta():
    telemetry = build_demo_telemetry()
    assert telemetry_delta(telemetry, 'VER', 'VER').DeltaSeconds.abs().max() == 0
    telemetry.loc[telemetry.Driver.eq('HAM'), 'ElapsedSeconds'] *= 2
    delta = telemetry_delta(telemetry, 'HAM', 'VER')
    assert delta.iloc[-1].DeltaSeconds > 0


def test_simulation_identity_and_invalid_stop():
    laps = build_demo_laps()
    assert simulate_strategy(laps, 'VER', 21, 0, 21.5, .04)['Écart alternatif (s)'].abs().max() == 0
    with pytest.raises(ValueError):
        simulate_strategy(laps, 'VER', 21, 30, 21.5, .04)


def test_report_is_self_contained_and_escapes_metadata():
    report = build_report(build_demo_laps(), {'season': 2024, 'event': '<script>oops</script>', 'session': 'Race', 'source': 'Demo'}, ['VER', 'HAM'], 'VER')
    assert '<script>oops</script>' not in report
    assert '&lt;script&gt;' in report
    import re
    assert not re.search(r'<script[^>]+src=[\"\']https?://', report)
    assert 'plotly.js' in report
