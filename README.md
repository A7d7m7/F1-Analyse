# F1 Race Strategy Analytics

**Comprendre la performance en Formule 1 à travers les données.**

Un dashboard interactif pour comparer les pilotes, explorer leur rythme en course et replacer leurs performances dans leur contexte : arrêts aux stands, relais et télémétrie selon la source disponible.

Développé en **Python** avec **Streamlit**, **pandas**, **NumPy** et **Plotly**, le projet associe visualisation, intégration d’API et calculs statistiques. **Jolpica est la source gratuite par défaut** ; une démonstration locale permet de découvrir l’application sans accès réseau, et FastF1 donne accès à des analyses plus détaillées avec un compte adapté.

[Prise en main](#prise-en-main) · [Fonctionnalités](#fonctionnalités) · [Sources de données](#sources-de-données) · [Méthodologie](#méthodologie-et-limites) · [Architecture](#architecture) · [Tests](#tests)

## Pourquoi ce projet ?

Un classement final indique qui termine devant. Il explique moins facilement comment une course s’est construite.

Ce projet permet d’explorer plusieurs questions :

- Quel pilote maintient le rythme le plus régulier ?
- À quels moments les écarts se creusent-ils ?
- Comment les arrêts influencent-ils les temps observés ?
- Où un pilote gagne-t-il du temps sur un tour rapide, lorsque la télémétrie est disponible ?

L’objectif est de rendre ces analyses accessibles tout en distinguant **les observations, les estimations et les données indisponibles**.

## Fonctionnalités

### Comparer les performances

Sélection de la saison, du Grand Prix et des pilotes, puis consultation des résultats, du nombre de tours, du meilleur chrono et du rythme médian. Le classement privilégie les résultats officiels ; les retards en tours sont distingués des écarts en secondes.

### Explorer le rythme et les écarts

Graphiques interactifs des temps au tour, médiane mobile et écarts cumulés par rapport à un pilote de référence. Les tours de stands sont identifiés et les trous de chronométrage ne sont pas extrapolés.

### Examiner les arrêts et les stratégies

Avec Jolpica, affichage des tours d’arrêt et des durées enregistrées. Avec FastF1 ou la démo, accès supplémentaire aux gommes, aux relais et à une estimation de la variation des temps par relais.

### Approfondir avec la télémétrie

Avec FastF1 ou la démo : comparaison de la vitesse, de l’accélérateur, du freinage, du régime moteur, des rapports et du DRS. Un alignement par distance permet de visualiser l’écart temporel et les portions où un pilote gagne du temps.

### Explorer un scénario alternatif

Un modèle pédagogique permet d’avancer ou de retarder un arrêt et d’observer l’effet théorique d’une dégradation linéaire des pneus. Ses hypothèses et ses limites sont affichées dans l’interface. Cette fonction est désactivée avec Jolpica.

### Partager les résultats

Tableau de lecture en français, chronos formatés, filtre par pilote, vue technique complète, export CSV et génération d’un **rapport HTML autonome** contenant graphiques, statistiques et constats calculés.

## Sources de données

| Capacité | Jolpica · mode gratuit | FastF1 · mode détaillé | Démo locale |
|---|---|---|---|
| Compte requis | Non | F1 TV pour les archives détaillées | Non |
| Données | Réelles | Réelles, selon disponibilité | Synthétiques |
| Sessions dans l’application | Course | Course, qualifications, sprint, essais | Exploration de l’interface |
| Résultats et temps au tour | Oui | Oui | Générés |
| Rythme | Hors stands, sans validation SC/VSC | Filtré sur les tours propres | Filtré sur les indicateurs simulés |
| Arrêts | Tours et durées enregistrées | Identification des tours de stands | Simulés |
| Pneus et relais | Indisponibles | Oui | Simulés |
| Secteurs et télémétrie | Indisponibles | Oui | Simulés |
| Simulation pédagogique | Désactivée | Course et sprint | Course et sprint |
| Exports CSV et HTML | Oui | Oui | Oui |

**Jolpica suffit pour démarrer gratuitement.** Les fonctions qui nécessitent des données absentes affichent une explication ; elles ne sont pas alimentées avec des données inventées.

La démo produit les mêmes performances synthétiques quel que soit le circuit sélectionné. Elle sert à explorer l’application, pas à analyser le Grand Prix affiché.

## Prise en main

### Prérequis

- Python **3.10 ou supérieur** et `pip` ;
- une connexion Internet pour les sources réelles ;
- un navigateur web.

Les commandes ci-dessous utilisent un environnement virtuel pour isoler les dépendances.

### 1. Récupérer le projet

```bash
git clone https://github.com/A7d7m7/F1-Analyse.git
cd F1-Analyse
```

### 2. Créer et activer l’environnement

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows · PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Installer et lancer

```bash
python -m pip install -r requirements.txt
python -m streamlit run app/dashboard.py
```

Ouvrir [localhost:8501](http://localhost:8501). Pour arrêter le serveur, utiliser `Ctrl+C` dans le terminal.

### Premier parcours conseillé

1. Garder la source **Jolpica** et sélectionner **2024 → Monaco Grand Prix → Race**.
2. Choisir deux pilotes et un pilote de référence.
3. Explorer **Vue générale**, **Rythme**, puis **Stratégie**.
4. Dans **Données et rapport**, préparer puis télécharger le rapport HTML.
5. Passer à **Demo locale** pour découvrir la télémétrie et la simulation sans abonnement.

Une course future ou dont les résultats ne sont pas encore publiés affiche un message explicite.

## Connexion optionnelle à FastF1

L’accès aux archives détaillées F1 nécessite une authentification avec un abonnement F1 TV approprié. Le [mainteneur de FastF1 décrit ce changement d’accès](https://github.com/theOehrly/Fast-F1/issues/978).

Dans la barre latérale :

1. Ouvrir **Connexion au compte F1**.
2. Cliquer sur **Se connecter à F1 TV**, puis ouvrir le lien proposé.
3. Suivre le parcours navigateur FastF1, qui utilise une extension.
4. Après connexion, cliquer sur **Utiliser FastF1**.

Une alternative est disponible dans le terminal, avec l’environnement virtuel activé :

```bash
python -m fastf1 auth f1tv --authenticate
```

Le panneau permet aussi d’annuler la connexion ou de se déconnecter. Le dashboard ne demande pas le mot de passe dans ses widgets ; FastF1 gère le jeton sur la machine locale.

> La connexion F1 est partagée par cette instance locale. Ce mécanisme n’est pas une gestion de comptes séparés pour un déploiement public multi-utilisateur.

## Méthodologie et limites

### Classement et écarts

Les résultats officiels sont prioritaires. À défaut, l’ordre indicatif repose sur le nombre de tours parcourus puis le temps cumulé. Un pilote ayant parcouru moins de tours ne passe donc pas devant simplement parce que son temps total est plus court.

Les écarts cumulés comparent **un même numéro de tour** : ils ne représentent pas un intervalle en direct. Les données manquantes interrompent les comparaisons. Dans le mode Jolpica, l’écart final utilise les temps officiels lorsqu’ils sont disponibles.

### Rythme

- **Jolpica** : exclusion du tour d’arrêt et du tour suivant. Sans drapeaux ni statut de suppression, le rythme peut encore inclure Safety Car, VSC et trafic. Aucun tour n’est certifié propre.
- **FastF1 et démo** : utilisation des tours avec temps positif, indicateur de précision valide, non supprimés, hors stands et avec statut de piste entièrement vert. Un statut inconnu est exclu.

Ces filtres réduisent certains biais sans rendre identiques les conditions de chaque pilote.

### Arrêts, pneus et simulation

La durée de stands Jolpica peut inclure entrée, sortie ou interruption sous drapeau rouge. Elle n’est ni une perte nette de temps en course ni seulement la durée du changement de pneus.

La pente des temps par relais est une estimation statistique, influencée aussi par le carburant et le trafic. Au moins quatre tours propres sont nécessaires ; ce n’est pas une mesure isolée de l’usure des pneus.

La simulation utilise un rythme médian constant, une dégradation linéaire saisie par l’utilisateur et une perte fixe aux stands. Elle ignore notamment le trafic, le carburant, la météo et les réactions adverses. **Elle ne prédit pas le résultat réel et ne recommande pas une stratégie optimale.**

Les constats du rapport sont calculés à partir des données. Aucun modèle d’intelligence artificielle n’est entraîné dans la version actuelle.

## Performance et cache

- Cache mémoire Streamlit pour les données chargées, avec expiration après une heure.
- Cache JSON des données préparées dans `data/cache/prepared`, valable six heures et réutilisable après redémarrage.
- Pagination Jolpica des chronos, requêtes espacées et délais réseau bornés.
- Télémétrie FastF1 chargée uniquement dans sa section, avec extraction et cache par pilote.
- Calcul des vues uniquement lorsqu’elles sont sélectionnées.

Le premier téléchargement télémétrique FastF1 peut rester long : les flux sont récupérés pour la session entière avant extraction des tours utiles. Les fichiers préparés expirés sont remplacés au prochain accès ; aucune purge globale automatique n’est implémentée.

Le projet est destiné à **l’analyse après session**, pas au suivi en temps réel. Les délais dépendent du réseau, des limites API et de la disponibilité des sources.

## Architecture

```text
F1-Analyse/
├── app/
│   └── dashboard.py          # Interface, navigation et filtres
├── src/f1_analysis/
│   ├── jolpica.py            # API gratuite, pagination et normalisation
│   ├── data_loader.py        # Routage des sources et cache sur disque
│   ├── metrics.py            # Préparation, classements et statistiques
│   ├── comparison.py         # Écarts télémétriques et simulation
│   ├── plots.py              # Graphiques interactifs Plotly
│   ├── report.py             # Rapport HTML autonome
│   ├── f1_auth.py            # Connexion locale au compte F1
│   ├── sample_data.py        # Démonstration reproductible
│   ├── schedule.py           # Calendriers et sélection des événements
│   └── config.py             # Paramètres et palettes
├── tests/                    # Tests de calculs, intégration simulée et interface
├── docs/
│   ├── Obsidian/             # Méthodes, architecture et journal des évolutions
│   └── Guide-presentation.md # Présentation du projet et questions fréquentes
├── .streamlit/config.toml    # Thème de l’application
└── requirements.txt          # Dépendances Python
```

La logique de calcul est séparée de l’interface pour pouvoir tester les méthodes sans lancer de serveur web.

## Tests

Avec l’environnement virtuel activé :

```bash
python -m pytest
```

La suite couvre notamment :

- les abandons, les tours de retard et les données de chronométrage manquantes ;
- le filtrage du rythme et le comptage des arrêts ;
- la pagination Jolpica et la gestion des limites de requêtes ;
- la réutilisation, l’expiration et la corruption du cache ;
- l’alignement télémétrique et les scénarios de simulation ;
- les exports HTML et les vues Streamlit avec `AppTest` ;
- le parcours local de connexion F1, sans identifiants réels.

Les tests automatisés fonctionnent hors ligne avec des données générées ou des réponses simulées. Ils ne garantissent pas la disponibilité des API ni la validité d’un abonnement F1 TV. La connexion réelle reste à effectuer par le propriétaire du compte.

## Compétences mises en pratique

| Domaine | Mise en œuvre |
|---|---|
| Intégration de données | API HTTP, pagination, normalisation et sources complémentaires |
| Analyse | Agrégations, médianes mobiles, régression linéaire et interpolation |
| Visualisation | Graphiques interactifs, unités explicites et tableaux de lecture |
| Développement Python | Modules séparés, cache et gestion des erreurs |
| Qualité | Tests de cas limites, tests d’interface et documentation des hypothèses |
| Restitution | Exports CSV, rapport HTML et documentation technique |

## Pistes d’évolution

Ces éléments sont des améliorations envisagées, pas des fonctionnalités disponibles :

- enrichir la validation sur plusieurs courses et types d’interruptions ;
- améliorer la comparaison des rythmes selon le carburant et le trafic ;
- construire un modèle de stratégie par gomme avec hypothèses calibrées ;
- ajouter une intégration continue pour les tests ;
- publier une démonstration accessible en ligne avec des données adaptées au partage public.

## Documentation et contributions

Le dossier [docs/Obsidian](docs/Obsidian/Accueil.md) peut être ouvert comme coffre Obsidian. Il reste également consultable comme ensemble de fichiers Markdown. Le [guide de présentation](docs/Guide-presentation.md) rassemble une présentation courte et les réponses aux questions techniques.

Pour proposer une amélioration ou signaler un problème, ouvrir une [issue](https://github.com/A7d7m7/F1-Analyse/issues) avec la source sélectionnée, la saison, le Grand Prix et les étapes de reproduction. Ne pas joindre de mot de passe, de jeton ou de cookie de connexion.

## Sources et crédits

- [Jolpica F1](https://github.com/jolpica/jolpica-f1) — résultats, temps au tour et arrêts.
- [FastF1](https://github.com/theOehrly/Fast-F1) — accès aux données détaillées F1.
- [Streamlit](https://streamlit.io/) — interface web Python.
- [Plotly](https://plotly.com/python/) — visualisations interactives.
- [pandas](https://pandas.pydata.org/) et [NumPy](https://numpy.org/) — traitement et calcul numérique.

Projet indépendant, non affilié à Formula 1, à la FIA ou aux écuries. Les données restent soumises aux conditions de leurs fournisseurs.
