# F1 Race Strategy Analytics

Dashboard d'analyse de donnees sportives applique a la Formule 1.

Le projet compare les performances de pilotes sur une session F1 avec :

- selection de la saison et du Grand Prix depuis le calendrier de la saison, sans saisie libre ;
- rythme au tour ;
- strategie pneus et relais ;
- impact des pit stops ;
- ecarts cumules en course ;
- comparaison de telemetrie sur un tour rapide.

Il fonctionne avec deux modes :

- **Demo locale** : donnees generees pour ouvrir le dashboard sans API.
- **FastF1** : donnees reelles de timing et telemetrie quand `fastf1` est installe.

## Stack

- Python
- pandas / numpy
- Plotly
- Streamlit
- FastF1

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Lancer le dashboard

```powershell
python -m streamlit run app/dashboard.py
```

Puis ouvrir l'URL affichee par Streamlit, en general :

```text
http://localhost:8501
```

## Structure

```text
F1-Analyse/
  app/
    dashboard.py
  data/
    README.md
  reports/
    README.md
  src/
    f1_analysis/
      config.py
      data_loader.py
      metrics.py
      plots.py
      sample_data.py
  tests/
    test_metrics.py
```

## Prochaines ameliorations

- Ajouter un modele de prediction de degradation pneus.
- Exporter automatiquement un rapport HTML apres chaque analyse.
- Ajouter une page "portfolio" avec captures et interpretation business.
- Comparer les strategies reelles avec une strategie alternative simulee.
- Etendre le calendrier embarque aux saisons futures quand elles sont publiees.
