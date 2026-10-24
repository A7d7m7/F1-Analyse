# Utilisation

Depuis la racine du dépôt :

```bash
source .venv/bin/activate
python -m streamlit run app/dashboard.py
python -m pytest
```

Commencer en Demo locale. Sélectionner deux pilotes. Montrer les temps bruts puis les tours propres dans Rythme. Dans Télémétrie, expliquer le signe de l’écart et comparer les freinages. Dans Simulation, déplacer un arrêt de cinq tours, puis mettre zéro pour constater un écart nul. Dans Données et rapport, préparer puis télécharger le HTML.

Le fichier HTML embarque ses graphiques et se consulte sans serveur. Il couvre les analyses observées ; le scénario est exportable séparément en CSV. La démo reste synthétique, y compris si une qualification est sélectionnée. Les analyses de somme des temps ont surtout du sens pour une course ; pour les autres sessions, privilégier rythme et télémétrie.
