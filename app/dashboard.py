from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
from html import escape
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from f1_analysis.f1_auth import F1Login
from f1_analysis.comparison import telemetry_delta, gain_zones, simulate_strategy
from f1_analysis.report import build_report
from f1_analysis.config import DEFAULT_EVENT, DEFAULT_SEASON, SESSION_LABELS
from f1_analysis.data_loader import SessionRequest, load_dataset, load_telemetry
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
        color: #aebbd0;
    }
    [data-testid="stMetric"] { background:#161f2e; border:1px solid #2b394e; border-top:3px solid #ff3344; padding:18px; border-radius:12px; }
    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        margin: 0.25rem 0 0.75rem;
    }
    .muted {
        color: #aebbd0;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False, max_entries=12, ttl=3600)
def cached_dataset(source: str, season: int, event: str, session_label: str):
    request = SessionRequest(season=season, event=event, session_label=session_label)
    return load_dataset(source, request)


@st.cache_data(show_spinner=False, max_entries=24, ttl=3600)
def cached_telemetry(source: str, season: int, event: str, session_label: str, drivers: tuple[str, ...]):
    frame = load_telemetry(source, SessionRequest(season, event, session_label), drivers)
    if frame.empty:
        raise ValueError("Aucune télémétrie disponible. Tu peux réessayer en rouvrant cette section.")
    return frame


@st.cache_data(show_spinner=False, max_entries=12)
def cached_event_options(season: int):
    return event_options_for_season(season)


@st.cache_resource
def f1_login():
    return F1Login()


def select_fastf1():
    st.session_state["data_source"] = "FastF1"


@st.fragment(run_every="2s")
def f1_account_panel():
    login = f1_login()
    st.subheader("Compte F1 TV")
    st.caption("Connexion locale à cette machine, partagée par les onglets du dashboard. Abonnement F1 TV adapté requis. Le parcours navigateur FastF1 utilise une extension indiquée sur sa page de connexion.")
    if login.connected():
        st.success("Compte F1 connecté")
        if st.button("Utiliser FastF1", key="use_f1", on_click=select_fastf1):
            cached_dataset.clear()
            cached_telemetry.clear()
            st.rerun()
        if st.button("Déconnecter le compte F1", key="disconnect_f1"):
            login.disconnect()
            cached_dataset.clear()
            cached_telemetry.clear()
            st.rerun()
    elif login.running():
        st.info("Connexion en attente, expiration après 5 minutes.")
        if login.url:
            st.link_button("Ouvrir la connexion F1", login.url)
        else:
            st.caption("Préparation du lien de connexion…")
        if st.button("Annuler la connexion", key="cancel_f1"):
            login.cancel()
            st.rerun()
    else:
        st.caption("Compte non connecté ou session expirée.")
        if login.process is not None:
            st.warning("Connexion terminée sans session valide. Tu peux réessayer.")
        if st.button("Se connecter à F1 TV", key="connect_f1"):
            login.start()
            st.rerun()


def metric_card(label: str, value: object, delta: object | None = None) -> None:
    st.metric(label=label, value=value, delta=delta)


with st.sidebar:
    st.title("F1 Analytics")
    source = st.radio("Source", ["Jolpica", "Demo locale", "FastF1"], horizontal=False, key="data_source")

    with st.expander("Connexion au compte F1", expanded=source == "FastF1"):
        f1_account_panel()

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
    session_label = st.selectbox("Session", ["Race"] if source == "Jolpica" else list(SESSION_LABELS.keys()), index=0)

    st.divider()
    st.caption(f"Circuit selectionne : {selected_event['location']} - {selected_event['country']}")
    st.caption("Jolpica : gratuit, courses uniquement. Données conservées six heures en cache. FastF1 : connexion F1 TV nécessaire pour les archives.")


if source == "FastF1" and not f1_login().connected():
    st.info("Connecte ton compte F1 dans la barre latérale, puis clique sur Utiliser FastF1. Jolpica reste accessible sans compte.")
    st.stop()

try:
    with st.spinner("Chargement des temps, pneus et résultats — sans télémétrie…"):
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

st.caption("RACE ENGINEERING / PERFORMANCE LAB")
st.title("F1 · Centre d’analyse")
st.markdown(
    f"<span class='muted'>{metadata['season']} - {escape(str(metadata['event']))} - {metadata['session']} | Source : {metadata['source']}</span>",
    unsafe_allow_html=True,
)

leader = filtered_summary.iloc[0]
best_lap_row = filtered_summary.sort_values("BestLapSeconds").iloc[0]
median_best = filtered_summary.sort_values("MedianPaceSeconds").iloc[0]
total_pit_stops = int(filtered_summary["PitStops"].sum())

kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
with kpi_1:
    metric_card("Premier de la sélection", leader["Driver"])
with kpi_2:
    metric_card(("Meilleur tour hors stands · min:s" if source == "Jolpica" else "Meilleur tour propre · min:s"), best_lap_row["Driver"], best_lap_row["BestLap"])
with kpi_3:
    metric_card(("Médiane hors stands · min:s" if source == "Jolpica" else "Rythme médian propre · min:s"), median_best["Driver"], median_best["MedianPace"])
with kpi_4:
    metric_card("Pit stops selection", total_pit_stops)

if source == "Demo locale":
    st.info("Démonstration synthétique : le circuit et la session choisis ne modifient pas les performances générées. Les tours 30 à 32 illustrent une Safety Car.")
if "OfficialPosition" not in laps:
    st.caption("Ordre indicatif : tours parcourus, puis temps cumulé. Les statuts d’arrivée ne sont pas disponibles.")
if source == "Jolpica":
    st.info("Jolpica : temps hors tour d’arrêt et tour suivant. Les drapeaux, suppressions de tours et pneus sont inconnus : le rythme peut inclure Safety Car, VSC ou trafic. Aucun tour n’est certifié propre.")
else:
    st.caption("Rythme propre : tours précis et non supprimés, hors entrée/sortie des stands, avec TrackStatus = 1. Un statut inconnu est exclu.")
section = st.radio("Analyse", ["Vue générale", "Rythme", "Stratégie", "Télémétrie", "Simulation", "Données et rapport"], horizontal=True, key="analysis_section")


if section == "Vue générale":
    left, right = st.columns([1.1, 0.9])
    with left:
        st.markdown("<div class='section-title'>Ecart cumule en course</div>", unsafe_allow_html=True)
        st.plotly_chart(plot_cumulative_gap(laps, selected_drivers, reference_driver), width="stretch")
        st.caption("Écart au même numéro de tour : ce graphique ne représente pas un intervalle en direct. Aucune extrapolation après un abandon ; une donnée manquante interrompt la série.")
    with right:
        st.markdown("<div class='section-title'>Synthese pilotes</div>", unsafe_allow_html=True)
        display_cols = [
            "Driver",
            "Team",
            "Laps",
            "BestLap",
            "MedianPace",
            "PitStops",
            "ResultStatus", "Gap",
            *([] if source == "Jolpica" else ["CleanLaps"]),
        ]
        st.dataframe(
            filtered_summary[display_cols],
            hide_index=True,
            width="stretch",
        )

if section == "Rythme":
    st.markdown("<div class='section-title'>Temps au tour</div>", unsafe_allow_html=True)
    st.plotly_chart(plot_lap_times(laps, selected_drivers), width="stretch")
    st.caption("Temps bruts : croix sur le tour d’arrêt et le tour suivant. Rythme Jolpica hors stands, sans filtrage SC/VSC ; les autres sources utilisent les tours propres.")
    left, right = st.columns(2)
    with left:
        st.markdown("<div class='section-title'>Rythme median mobile</div>", unsafe_allow_html=True)
        st.plotly_chart(plot_rolling_pace(laps, selected_drivers), width="stretch")
    with right:
        st.markdown("<div class='section-title'>Distribution par secteur</div>", unsafe_allow_html=True)
        if source == "Jolpica":
            st.info("Temps par secteur indisponibles avec Jolpica.")
        else:
            st.plotly_chart(plot_sector_box(laps, selected_drivers), width="stretch")

if section == "Stratégie" and source == "Jolpica":
    st.subheader("Arrêts aux stands")
    stops = laps[laps.Driver.isin(selected_drivers) & laps.IsPitInLap][["Driver", "LapNumber", "PitDurationSeconds"]]
    st.dataframe(stops.rename(columns={"Driver": "Pilote", "LapNumber": "Tour", "PitDurationSeconds": "Durée enregistrée (s)"}), hide_index=True)
    st.caption("La durée Jolpica peut inclure entrée, sortie et interruption sous drapeau rouge ; elle ne mesure pas uniquement l’immobilisation et n’est pas une perte de temps nette.")
    st.info("Gommes, âge des pneus et dégradation indisponibles. Aucun relais pneus n’est reconstitué.")

if section == "Stratégie" and source != "Jolpica":
    st.markdown("<div class='section-title'>Strategie pneus</div>", unsafe_allow_html=True)
    st.plotly_chart(plot_strategy(laps, selected_drivers), width="stretch")
    st.caption("Pente en secondes par tour : variation observée, influencée par le carburant et le trafic. Moins de quatre tours propres : estimation indisponible.")
    st.markdown("<div class='section-title'>Relais et degradation</div>", unsafe_allow_html=True)
    st.dataframe(
        stint_summary(laps).query("Driver in @selected_drivers"),
        hide_index=True,
        width="stretch",
    )

if section == "Télémétrie" and source == "Jolpica":
    st.info("Jolpica ne fournit pas de télémétrie : vitesse, freinage et écart par distance indisponibles. Le mode démo permet d’explorer ces graphiques synthétiques.")

if section == "Télémétrie" and source != "Jolpica":
    st.caption("La télémétrie se charge à la demande. FastF1 télécharge les flux de la session au premier accès ; seuls les meilleurs tours des pilotes sélectionnés sont extraits et conservés.")
    try:
        with st.spinner("Chargement de la télémétrie des pilotes sélectionnés…"):
            telemetry = cached_telemetry(source, int(season), event.strip(), session_label, tuple(sorted(selected_drivers)))
    except Exception as exc:
        st.warning(f"Télémétrie indisponible : {exc}")
        telemetry = pd.DataFrame()
    if telemetry.empty:
        st.warning("Aucune telemetrie disponible pour cette session.")
    else:
        metric = st.selectbox("Signal", ["Speed", "Throttle", "Brake", "RPM", "nGear", "DRS"])
        available_telemetry_drivers = sorted(set(selected_drivers) & set(telemetry["Driver"].unique()))
        if not available_telemetry_drivers:
            st.warning("Aucun des pilotes selectionnes n'a de telemetrie chargee.")
        else:
            st.plotly_chart(plot_telemetry(telemetry, available_telemetry_drivers, metric), width="stretch")
            st.caption("Meilleur tour rapide disponible de chaque pilote, potentiellement à des moments différents. Frein réel : signal binaire ; frein démo : intensité synthétique en %. DRS : code brut FastF1.")
            if len(available_telemetry_drivers) >= 2 and "ElapsedSeconds" in telemetry:
                compared = st.selectbox("Pilote à comparer", [d for d in available_telemetry_drivers if d != reference_driver]) if reference_driver in available_telemetry_drivers else available_telemetry_drivers[1]
                ref = reference_driver if reference_driver in available_telemetry_drivers else available_telemetry_drivers[0]
                try:
                    delta = telemetry_delta(telemetry, compared, ref)
                    fig = px.line(delta, x="Distance", y="DeltaSeconds", template="plotly_dark", labels={"Distance": "Distance (m)", "DeltaSeconds": f"Écart {compared} − {ref} (s)"})
                    st.plotly_chart(fig, width="stretch")
                    st.caption("Interpolation sur la distance commune. Écart positif : pilote comparé plus lent. Une variation négative indique une zone où il gagne du temps. Résolution indicative, sans attribution automatique aux virages.")
                    st.dataframe(gain_zones(delta), hide_index=True)
                    st.plotly_chart(plot_telemetry(telemetry, [compared, ref], "Brake"), width="stretch")
                except ValueError as exc:
                    st.warning(str(exc))

if section == "Données et rapport":
    st.subheader("Détail des tours")
    st.caption("Une lecture simplifiée des chronos. Les données techniques complètes restent disponibles dans la vue brute et l’export CSV.")
    filtered_laps = laps[laps["Driver"].isin(selected_drivers)].copy()
    controls = st.columns([2, 1])
    with controls[0]:
        table_driver = st.selectbox("Pilote affiché", ["Tous les pilotes", *selected_drivers], key="table_driver")
    with controls[1]:
        table_mode = st.selectbox("Affichage", ["Vue lisible", "Données brutes"], key="table_mode")
    shown = filtered_laps if table_driver == "Tous les pilotes" else filtered_laps[filtered_laps.Driver.eq(table_driver)]
    shown = shown.sort_values(["LapNumber", "Driver"]).reset_index(drop=True)
    st.caption(f"{len(shown):,} lignes · {shown.Driver.nunique()} pilote(s) · Temps en minutes:secondes")
    if table_mode == "Données brutes":
        st.dataframe(shown, hide_index=True, height=520, row_height=40, width="stretch", alt="Données techniques des tours sélectionnés")
    else:
        table = pd.DataFrame({
            "Tour": shown["LapNumber"],
            "Pilote": shown["Driver"],
            "Écurie": shown["Team"],
            "Chrono": shown["LapTimeFormatted"],
            "Type de tour": shown.apply(lambda r: "Arrêt aux stands" if r.IsPitInLap else ("Après arrêt" if r.IsPitOutLap else "En piste"), axis=1),
        })
        if "PitDurationSeconds" in shown:
            table["Durée aux stands (s)"] = shown["PitDurationSeconds"]
        styles = pd.DataFrame("", index=table.index, columns=table.columns)
        for i in table.index:
            styles.loc[i, :] = "background-color: #192330; color: #d6dfe9" if i % 2 == 0 else "background-color: #141d28; color: #d6dfe9"
        styles["Chrono"] += "; color: #edf3f8; font-weight: 600"
        styles["Pilote"] += "; color: #9bc1e5; font-weight: 600"
        styles.loc[table["Type de tour"].ne("En piste"), "Type de tour"] += "; color: #e6c58b"
        styled = table.style.apply(lambda _: styles, axis=None)
        st.dataframe(
            styled, hide_index=True, width="stretch", height=520, row_height=44,
            column_config={
                "Tour": st.column_config.NumberColumn("Tour", width="small", format="%d"),
                "Pilote": st.column_config.TextColumn("Pilote", width="small"),
                "Écurie": st.column_config.TextColumn("Écurie", width="medium"),
                "Chrono": st.column_config.TextColumn("Chrono · min:s", width="small"),
                "Type de tour": st.column_config.TextColumn("Type de tour", width="medium"),
                "Durée aux stands (s)": st.column_config.NumberColumn("Stands · s", format="%.3f", help="Durée enregistrée, pas une perte nette. Une interruption peut y être incluse."),
            },
            alt="Chronos par pilote et par tour avec identification des arrêts aux stands",
        )
        st.caption("Les durées absentes sont indiquées par un tiret. Le rythme Jolpica n’est pas filtré des Safety Cars.")
    csv = filtered_laps.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Telecharger les tours en CSV",
        data=csv,
        file_name="f1_laps_analysis.csv",
        mime="text/csv",
    )

    if st.button("Préparer le rapport HTML", key="report"):
        report = build_report(laps, metadata, selected_drivers, reference_driver)
        st.download_button("Télécharger le rapport HTML autonome", report, file_name="rapport_f1.html", mime="text/html")

if section == "Simulation" and source == "Jolpica":
    st.info("Simulation désactivée avec Jolpica : gommes, âge des pneus et rythme sous drapeau vert inconnus. Utilise la démo pour explorer le modèle pédagogique.")

if section == "Simulation" and source != "Jolpica":
    st.subheader("Déplacer un arrêt aux stands")
    st.info("Modèle pédagogique : rythme médian constant + pente linéaire selon l’âge du pneu + perte fixe aux stands. Même gomme et même nombre d’arrêts. Trafic, carburant, météo, Safety Car et interactions entre pilotes ne sont pas simulés. Aucune prédiction du résultat réel.")
    simulation_driver = st.selectbox("Pilote simulé", selected_drivers)
    observed_stops = laps.loc[laps.Driver.eq(simulation_driver) & laps.IsPitInLap, "LapNumber"].astype(int).tolist()
    if session_label not in ["Race", "Sprint"]:
        st.warning("La simulation est réservée aux courses et aux sprints.")
    elif not observed_stops:
        st.warning("Aucun arrêt observé pour ce pilote.")
    else:
        stop = st.selectbox("Arrêt observé (tour)", observed_stops)
        shift = st.slider("Décalage (tours)", -10, 10, -5)
        loss = st.number_input("Perte aux stands (s)", min_value=0.0, value=21.5, step=0.5)
        slope = st.number_input("Dégradation supposée (s/tour d’âge)", min_value=0.0, value=0.04, step=0.01)
        try:
            simulation = simulate_strategy(laps, simulation_driver, stop, shift, loss, slope)
            st.metric("Écart final alternatif − initial (s)", f"{simulation.iloc[-1]['Écart alternatif (s)']:+.3f}")
            st.caption("Négatif = gain théorique. La perte aux stands est identique dans les deux scénarios : elle s’annule dans l’écart final.")
            st.plotly_chart(px.line(simulation, x="Tour", y="Écart alternatif (s)", template="plotly_dark"), width="stretch")
            st.download_button("Exporter le scénario CSV", simulation.to_csv(index=False), "scenario.csv", "text/csv")
        except ValueError as exc:
            st.warning(str(exc))
