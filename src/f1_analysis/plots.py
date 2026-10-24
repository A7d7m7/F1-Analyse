from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from f1_analysis.config import COMPOUND_COLORS, DRIVER_COLORS
from f1_analysis.metrics import cumulative_gap, prepare_laps


PLOT_TEMPLATE = "plotly_dark"


def _driver_color(driver: str) -> str:
    return DRIVER_COLORS.get(driver, "#aabbcc")


def driver_colors(frame, drivers):
    import re
    colors = {}
    team_palette = {"Red Bull Racing": "#3671C6", "Ferrari": "#E8002D", "McLaren": "#FF8000", "Mercedes": "#27F4D2"}
    for driver in drivers:
        rows = frame[frame.Driver.eq(driver)]
        color = str(rows.TeamColor.dropna().iloc[0]).lstrip("#") if "TeamColor" in rows and rows.TeamColor.notna().any() else ""
        team = rows.Team.iloc[0] if "Team" in rows and len(rows) else ""
        colors[driver] = "#" + color if re.fullmatch(r"[0-9a-fA-F]{6}", color) else team_palette.get(team, _driver_color(driver))
    return colors


def plot_lap_times(laps: pd.DataFrame, drivers: list[str]) -> go.Figure:
    frame = prepare_laps(laps)
    frame = frame[frame["Driver"].isin(drivers)]
    fig = px.line(
        frame,
        x="LapNumber",
        y="LapTimeSeconds",
        color="Driver",
        color_discrete_map=driver_colors(laps, drivers),
        markers=True,
        template=PLOT_TEMPLATE,
        labels={"LapNumber": "Lap", "LapTimeSeconds": "Temps au tour (s)"},
    )
    pit_laps = frame[frame["IsPitLap"]]
    if not pit_laps.empty:
        fig.add_trace(
            go.Scatter(
                x=pit_laps["LapNumber"],
                y=pit_laps["LapTimeSeconds"],
                mode="markers",
                marker=dict(size=11, symbol="x", color="#111827"),
                name="Pit stop",
                hovertemplate="Pit stop lap %{x}<extra></extra>",
            )
        )
    fig.update_layout(height=440, legend_title_text="", margin=dict(l=10, r=10, t=30, b=10))
    return fig


def plot_rolling_pace(laps: pd.DataFrame, drivers: list[str]) -> go.Figure:
    frame = prepare_laps(laps)
    frame = frame[frame["Driver"].isin(drivers) & frame["IsPaceLap"]]
    fig = px.line(
        frame,
        x="LapNumber",
        y="RollingPace3",
        color="Driver",
        color_discrete_map=driver_colors(laps, drivers),
        template=PLOT_TEMPLATE,
        labels={"LapNumber": "Lap", "RollingPace3": "Rythme median 3 tours (s)"},
    )
    fig.update_layout(height=390, legend_title_text="", margin=dict(l=10, r=10, t=30, b=10))
    return fig


def plot_cumulative_gap(laps: pd.DataFrame, drivers: list[str], reference_driver: str) -> go.Figure:
    gaps = cumulative_gap(laps, reference_driver)
    gaps = gaps[gaps["Driver"].isin(drivers)]
    fig = px.line(
        gaps,
        x="LapNumber",
        y="GapSeconds",
        color="Driver",
        color_discrete_map=driver_colors(laps, drivers),
        template=PLOT_TEMPLATE,
        labels={"LapNumber": "Lap", "GapSeconds": f"Ecart vs {reference_driver} (s)"},
    )
    fig.add_hline(y=0, line_width=1, line_dash="dot", line_color="#6b7280")
    fig.update_layout(height=390, legend_title_text="", margin=dict(l=10, r=10, t=30, b=10))
    return fig


def plot_strategy(laps: pd.DataFrame, drivers: list[str]) -> go.Figure:
    frame = prepare_laps(laps)
    frame = frame[frame["Driver"].isin(drivers)].copy()
    if "Stint" not in frame:
        frame["Stint"] = 1
    if "Compound" not in frame:
        frame["Compound"] = "UNKNOWN"

    stints = (
        frame.groupby(["Driver", "Stint", "Compound"])
        .agg(StartLap=("LapNumber", "min"), EndLap=("LapNumber", "max"))
        .reset_index()
    )

    fig = go.Figure()
    for _, row in stints.iterrows():
        compound = str(row["Compound"] or "UNKNOWN")
        fig.add_trace(
            go.Bar(
                y=[row["Driver"]],
                x=[row["EndLap"] - row["StartLap"] + 1],
                base=[row["StartLap"]],
                orientation="h",
                marker_color=COMPOUND_COLORS.get(compound, COMPOUND_COLORS["UNKNOWN"]),
                marker_line=dict(color="#111827", width=1 if compound == "HARD" else 0),
                name=compound,
                customdata=[[row["EndLap"]]],
                hovertemplate=(
                    f"{row['Driver']}<br>{compound}<br>"
                    "Laps %{base}-%{customdata[0]}<extra></extra>"
                ),
                showlegend=compound not in {trace.name for trace in fig.data},
            )
        )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        height=300,
        barmode="stack",
        xaxis_title="Lap",
        yaxis_title="",
        legend_title_text="Pneu",
        margin=dict(l=10, r=10, t=30, b=10),
    )
    return fig


def plot_sector_box(laps: pd.DataFrame, drivers: list[str]) -> go.Figure:
    frame = prepare_laps(laps)
    frame = frame[frame["Driver"].isin(drivers)]
    frame = frame[frame["IsCleanLap"]]
    sectors = frame.melt(
        id_vars=["Driver", "LapNumber"],
        value_vars=[column for column in ["Sector1Seconds", "Sector2Seconds", "Sector3Seconds"] if column in frame],
        var_name="Sector",
        value_name="Seconds",
    ).dropna()
    sectors["Sector"] = sectors["Sector"].str.replace("Seconds", "", regex=False)
    fig = px.box(
        sectors,
        x="Sector",
        y="Seconds",
        color="Driver",
        color_discrete_map=driver_colors(laps, drivers),
        template=PLOT_TEMPLATE,
        labels={"Seconds": "Temps (s)"},
    )
    fig.update_layout(height=360, legend_title_text="", margin=dict(l=10, r=10, t=30, b=10))
    return fig


def plot_telemetry(telemetry: pd.DataFrame, drivers: list[str], metric: str) -> go.Figure:
    frame = telemetry[telemetry["Driver"].isin(drivers)]
    fig = px.line(
        frame,
        x="Distance",
        y=metric,
        color="Driver",
        color_discrete_map=driver_colors(telemetry, drivers),
        template=PLOT_TEMPLATE,
        labels={"Distance": "Distance (m)", metric: {"Speed": "Vitesse (km/h)", "Throttle": "Accélérateur (%)", "Brake": "Frein actif (0/1)", "RPM": "Régime (tr/min)", "nGear": "Rapport", "DRS": "Code DRS"}.get(metric, metric)},
    )
    if metric == "Brake" and not frame.empty and pd.to_numeric(frame["Brake"]).max() > 1:
        fig.update_yaxes(title="Frein synthétique (%)")
    fig.update_layout(height=430, legend_title_text="", margin=dict(l=10, r=10, t=30, b=10))
    return fig
