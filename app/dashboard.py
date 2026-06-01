from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from f1_analysis.config import DEFAULT_EVENT, DEFAULT_SEASON, SESSION_LABELS
from f1_analysis.data_loader import SessionRequest, load_dataset
from f1_analysis.metrics import driver_options, prepare_laps, race_summary, stint_summary
from f1_analysis.plots import (
    plot_cumulative_gap,
    plot_lap_times,
    plot_rolling_pace,
    plot_sector_box,
    plot_strategy,
    plot_telemetry,
)
from f1_analysis.schedule import available_seasons, event_options_for_season, format_event_option


st.set_page_config(
    page_title="F1 Race Strategy Analytics",
    page_icon=":racing_car:",
    layout="wide",
)


st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1320px;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
    [data-testid="stMetricLabel"] {
        color: #4b5563;
    }
    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        margin: 0.25rem 0 0.75rem;
    }
    .muted {
        color: #6b7280;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def cached_dataset(source: str, season: int, event: str, session_label: str):
    request = SessionRequest(season=season, event=event, session_label=session_label)
    return load_dataset(source, request)


@st.cache_data(show_spinner=False)
def cached_event_options(season: int):
    return event_options_for_season(season)


def metric_card(label: str, value: object, delta: object | None = None) -> None:
    st.metric(label=label, value=value, delta=delta)


with st.sidebar:
    st.title("F1 Analytics")
    source = st.radio("Source", ["Demo locale", "FastF1"], horizontal=False)

    season_options = available_seasons()
    season_index = season_options.index(DEFAULT_SEASON) if DEFAULT_SEASON in season_options else 0
    season = st.selectbox("Saison", season_options, index=season_index)

    event_options = cached_event_options(int(season))
    if not event_options:
        st.error("Aucun Grand Prix disponible pour cette saison.")
        st.stop()

    default_event_index = next(
        (index for index, option in enumerate(event_options) if option["name"] == DEFAULT_EVENT),
        0,
    )
    event_labels = [format_event_option(option) for option in event_options]
    selected_event_label = st.selectbox(
        "Grand Prix / circuit",
        event_labels,
        index=default_event_index,
        key=f"event_{season}",
    )
    selected_event = event_options[event_labels.index(selected_event_label)]
    event = selected_event["name"]
    session_label = st.selectbox("Session", list(SESSION_LABELS.keys()), index=0)

    st.divider()
    st.caption(f"Circuit selectionne : {selected_event['location']} - {selected_event['country']}")
    st.caption("FastF1 telecharge les donnees au premier chargement puis les garde en cache local.")


try:
    laps, telemetry, metadata = cached_dataset(source, int(season), event.strip(), session_label)
except Exception as exc:
    st.error(str(exc))
    st.info("Bascule sur 'Demo locale' pour explorer le dashboard sans dependances FastF1.")
    st.stop()

laps = prepare_laps(laps)
drivers = driver_options(laps)

if not drivers:
    st.warning("Aucun pilote disponible dans les donnees chargees.")
    st.stop()

default_selection = drivers[:2] if len(drivers) >= 2 else drivers
selected_drivers = st.sidebar.multiselect("Pilotes", drivers, default=default_selection)
if not selected_drivers:
    st.warning("Selectionne au moins un pilote.")
    st.stop()

reference_driver = st.sidebar.selectbox(
    "Reference ecart",
    selected_drivers,
    index=0,
)

summary = race_summary(laps)
filtered_summary = summary[summary["Driver"].isin(selected_drivers)]

st.title("F1 Race Strategy Analytics")
st.markdown(
    f"<span class='muted'>{metadata['season']} - {metadata['event']} - {metadata['session']} | Source : {metadata['source']}</span>",
    unsafe_allow_html=True,
)

leader = filtered_summary.iloc[0]
best_lap_row = filtered_summary.sort_values("BestLapSeconds").iloc[0]
median_best = filtered_summary.sort_values("MedianPaceSeconds").iloc[0]
total_pit_stops = int(filtered_summary["PitStops"].sum())

kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
with kpi_1:
    metric_card("Leader selection", leader["Driver"], leader["RaceTime"])
with kpi_2:
    metric_card("Meilleur tour", best_lap_row["Driver"], best_lap_row["BestLap"])
with kpi_3:
    metric_card("Meilleur rythme median", median_best["Driver"], median_best["MedianPace"])
with kpi_4:
    metric_card("Pit stops selection", total_pit_stops)

overview_tab, pace_tab, strategy_tab, telemetry_tab, data_tab = st.tabs(
    ["Vue generale", "Rythme", "Strategie", "Telemetrie", "Donnees"]
)

with overview_tab:
    left, right = st.columns([1.1, 0.9])
    with left:
        st.markdown("<div class='section-title'>Ecart cumule en course</div>", unsafe_allow_html=True)
        st.plotly_chart(plot_cumulative_gap(laps, selected_drivers, reference_driver), width="stretch")
    with right:
        st.markdown("<div class='section-title'>Synthese pilotes</div>", unsafe_allow_html=True)
        display_cols = [
            "Driver",
            "Team",
            "Laps",
            "BestLap",
            "MedianPace",
            "PitStops",
            "GapToLeaderSeconds",
        ]
        st.dataframe(
            filtered_summary[display_cols],
            hide_index=True,
            width="stretch",
        )

with pace_tab:
    st.markdown("<div class='section-title'>Temps au tour</div>", unsafe_allow_html=True)
    st.plotly_chart(plot_lap_times(laps, selected_drivers), width="stretch")
    left, right = st.columns(2)
    with left:
        st.markdown("<div class='section-title'>Rythme median mobile</div>", unsafe_allow_html=True)
        st.plotly_chart(plot_rolling_pace(laps, selected_drivers), width="stretch")
    with right:
        st.markdown("<div class='section-title'>Distribution par secteur</div>", unsafe_allow_html=True)
        st.plotly_chart(plot_sector_box(laps, selected_drivers), width="stretch")

with strategy_tab:
    st.markdown("<div class='section-title'>Strategie pneus</div>", unsafe_allow_html=True)
    st.plotly_chart(plot_strategy(laps, selected_drivers), width="stretch")
    st.markdown("<div class='section-title'>Relais et degradation</div>", unsafe_allow_html=True)
    st.dataframe(
        stint_summary(laps).query("Driver in @selected_drivers"),
        hide_index=True,
        width="stretch",
    )

with telemetry_tab:
    if telemetry.empty:
        st.warning("Aucune telemetrie disponible pour cette session.")
    else:
        metric = st.selectbox("Signal", ["Speed", "Throttle", "Brake", "RPM", "nGear", "DRS"])
        available_telemetry_drivers = sorted(set(selected_drivers) & set(telemetry["Driver"].unique()))
        if not available_telemetry_drivers:
            st.warning("Aucun des pilotes selectionnes n'a de telemetrie chargee.")
        else:
            st.plotly_chart(plot_telemetry(telemetry, available_telemetry_drivers, metric), width="stretch")
            st.caption("Comparaison sur le meilleur tour rapide disponible pour chaque pilote.")

with data_tab:
    st.markdown("<div class='section-title'>Tours nettoyes</div>", unsafe_allow_html=True)
    filtered_laps = laps[laps["Driver"].isin(selected_drivers)]
    st.dataframe(filtered_laps, hide_index=True, width="stretch")
    csv = filtered_laps.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Telecharger les tours en CSV",
        data=csv,
        file_name="f1_laps_analysis.csv",
        mime="text/csv",
    )
