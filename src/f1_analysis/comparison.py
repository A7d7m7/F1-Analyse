"""Distance-aligned telemetry and explicit, educational strategy scenarios."""
import numpy as np
import pandas as pd


def telemetry_delta(telemetry, driver, reference):
    frames = []
    for name in [driver, reference]:
        frame = telemetry[telemetry.Driver.eq(name)].dropna(subset=["Distance", "ElapsedSeconds"]).sort_values("Distance").drop_duplicates("Distance")
        if len(frame) < 2:
            raise ValueError("Télémétrie temporelle insuffisante pour comparer ces pilotes.")
        frames.append(frame)
    a, b = frames
    start, end = max(a.Distance.min(), b.Distance.min()), min(a.Distance.max(), b.Distance.max())
    if end <= start:
        raise ValueError("Aucune distance commune.")
    distance = np.linspace(start, end, 500)
    delta = np.interp(distance, a.Distance, a.ElapsedSeconds) - np.interp(distance, b.Distance, b.ElapsedSeconds)
    return pd.DataFrame({"Distance": distance, "DeltaSeconds": delta - delta[0]})


def gain_zones(delta, count=10):
    groups = np.array_split(np.arange(len(delta)), count)
    return pd.DataFrame([{
        "Début (m)": round(delta.iloc[g[0]].Distance),
        "Fin (m)": round(delta.iloc[g[-1]].Distance),
        "Variation écart (s)": round(delta.iloc[g[-1]].DeltaSeconds - delta.iloc[g[0]].DeltaSeconds, 3),
    } for g in groups if len(g) > 1])


def simulate_strategy(laps, driver, stop, shift, pit_loss, degradation):
    from f1_analysis.metrics import prepare_laps
    frame = prepare_laps(laps)
    frame = frame[frame.Driver.eq(driver)].sort_values("LapNumber")
    clean = frame[frame.IsCleanLap]
    stops = frame.loc[frame.IsPitInLap, "LapNumber"].astype(int).tolist()
    if stop not in stops or clean.empty:
        raise ValueError("Un arrêt observé et des tours propres sont nécessaires.")
    new_stop = stop + shift
    alternative = [new_stop if value == stop else value for value in stops]
    if new_stop <= 1 or new_stop >= frame.LapNumber.max() or sorted(set(alternative)) != alternative:
        raise ValueError("L’arrêt déplacé doit rester entre les arrêts voisins et dans la course.")
    numbers = np.arange(1, int(frame.LapNumber.max()) + 1)
    baseline = float(clean.LapTimeSeconds.median())
    def model(schedule):
        age = np.array([lap - max([0] + [s for s in schedule if s < lap]) for lap in numbers])
        return baseline + degradation * age + np.isin(numbers, schedule) * pit_loss
    original, changed = model(stops), model(alternative)
    return pd.DataFrame({"Tour": numbers, "Scénario initial (s)": np.cumsum(original), "Scénario alternatif (s)": np.cumsum(changed), "Écart alternatif (s)": np.cumsum(changed - original)})
