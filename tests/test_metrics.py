from f1_analysis.metrics import cumulative_gap, race_summary, stint_summary
from f1_analysis.sample_data import build_demo_laps, load_demo_dataset


def test_race_summary_contains_all_demo_drivers():
    laps = build_demo_laps()
    summary = race_summary(laps)

    assert set(summary["Driver"]) == {"VER", "LEC", "NOR", "HAM"}
    assert summary["BestLapSeconds"].notna().all()
    assert summary["PitStops"].sum() == 8


def test_stint_summary_estimates_degradation():
    laps = build_demo_laps()
    stints = stint_summary(laps)

    assert {"Driver", "Stint", "Compound", "DegradationPerLap"}.issubset(stints.columns)
    assert stints["DegradationPerLap"].notna().all()


def test_cumulative_gap_uses_reference_driver():
    laps = build_demo_laps()
    gaps = cumulative_gap(laps, "VER")

    ver_gaps = gaps[gaps["Driver"] == "VER"]
    assert ver_gaps["GapSeconds"].abs().max() == 0
    assert {"LapNumber", "Driver", "GapSeconds"}.issubset(gaps.columns)


def test_demo_dataset_reflects_selected_event():
    laps, _, metadata = load_demo_dataset(
        season=2026,
        event="Monaco Grand Prix",
        session="Qualifying",
    )

    assert metadata["season"] == 2026
    assert metadata["event"] == "Monaco Grand Prix"
    assert laps["Season"].unique().tolist() == [2026]
    assert laps["EventName"].unique().tolist() == ["Monaco Grand Prix"]
