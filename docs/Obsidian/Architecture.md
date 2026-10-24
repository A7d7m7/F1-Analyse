# Architecture

`app/dashboard.py` orchestre les filtres et les vues Streamlit. Les transformations restent dans des modules Python testables.

1. `data_loader.py` charge FastF1 et conserve les drapeaux, entrées/sorties des stands, résultats et couleurs des équipes. Les messages de direction de course sont chargés pour connaître les tours supprimés.
2. `sample_data.py` produit une démonstration reproductible : mêmes performances quel que soit le circuit choisi. Elle contient des tours de stands et une période de Safety Car illustrative.
3. `metrics.py` prépare les tours, filtre le rythme, produit les synthèses et écarts.
4. `comparison.py` aligne la télémétrie par distance et calcule un scénario d’arrêt alternatif.
5. `plots.py` produit les graphiques Plotly et utilise les couleurs des résultats lorsque disponibles, avec une palette de secours.
6. `report.py` construit un HTML autonome avec Plotly embarqué et les métadonnées échappées.
7. `.streamlit/config.toml` définit la palette sombre ; le dashboard ajoute des cartes et une hiérarchie visuelle.

Les chargements sont mis en cache avec une limite de 12 entrées. Seule la section sélectionnée est calculée.
