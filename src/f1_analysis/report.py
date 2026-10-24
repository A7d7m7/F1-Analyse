from html import escape
from f1_analysis.metrics import race_summary, stint_summary
from f1_analysis.plots import plot_lap_times, plot_strategy, plot_cumulative_gap


def build_report(laps, metadata, drivers, reference):
    selected = laps[laps.Driver.isin(drivers)]
    summary = race_summary(laps)
    summary = summary[summary.Driver.isin(drivers)]
    title = escape(f"{metadata['season']} · {metadata['event']} · {metadata['session']}")
    jolpica = metadata["source"] == "Jolpica"
    figures = [plot_lap_times(selected, drivers), plot_cumulative_gap(selected, drivers, reference)]
    if not jolpica:
        figures.append(plot_strategy(selected, drivers))
    pace_note = "Rythme hors tour d’arrêt et tour suivant, sans filtrage Safety Car/VSC ni validation des suppressions. Aucun tour certifié propre." if jolpica else "Rythme : tours précis, non supprimés, hors stands, sous drapeau vert uniquement. Les statuts inconnus sont exclus."
    strategy_html = ("<h2>Arrêts</h2>" + selected[selected.IsPitInLap][["Driver", "LapNumber", "PitDurationSeconds"]].to_html(index=False) + "<p>Durées enregistrées incluant éventuellement un drapeau rouge, pas des pertes nettes. Pneus, secteurs, télémétrie et simulation indisponibles.</p>") if jolpica else "<h2>Relais</h2>" + stint_summary(selected).to_html(index=False, escape=True)
    charts = ''.join(fig.to_html(full_html=False, include_plotlyjs=True if i == 0 else False) for i, fig in enumerate(figures))
    findings = ''.join(f"<li>{escape(str(r.Driver))} : {int(r.CleanLaps)} tours certifiés propres ; rythme médian {escape(r.MedianPace)} ; {int(r.PitStops)} arrêts.</li>" for r in summary.itertuples())
    return f'''<!doctype html><html lang="fr"><meta charset="utf-8"><title>Rapport F1</title>
<style>body{{background:#0c1018;color:#edf1fa;font:16px system-ui;max-width:1200px;margin:40px auto;padding:20px}}h1{{border-left:5px solid #ff3344;padding-left:20px}}table{{border-collapse:collapse;width:100%}}td,th{{padding:10px;border-bottom:1px solid #354052}} .plotly-graph-div{{margin:24px 0}}</style>
<h1>{title}</h1><p>Source : {escape(str(metadata['source']))} · Référence : {escape(reference)}</p>
<h2>Constats calculés</h2><ul>{findings}</ul>
<p>{pace_note} Les écarts cumulés comparent un même numéro de tour, pas un intervalle en direct. Classement officiel prioritaire ; sinon ordre indicatif par tours parcourus puis temps. Les abandons et tours de retard ne sont pas des écarts en secondes.</p>
{summary.to_html(index=False, escape=True)}{charts}{strategy_html}
<p>La pente des temps reflète aussi le carburant et le trafic : ce n’est pas une mesure isolée de l’usure des pneus. Mode démo : données synthétiques, indépendantes du circuit sélectionné. Ce rapport couvre les analyses observées ; la simulation pédagogique reste une exploration séparée.</p></html>'''
