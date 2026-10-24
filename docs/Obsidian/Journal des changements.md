# Journal des changements

## 24 octobre 2026

### Fiabilité avant présentation

Remplacement du classement basé uniquement sur la somme des temps par la priorité aux résultats officiels, avec repli tours/temps. Conservation des statuts d’arrivée. Retards en tours séparés des secondes. Préservation des tours dont le temps manque pour empêcher des écarts trompeurs.

Ajout des drapeaux et de la distinction entrée/sortie des stands, filtrage des tours propres, et comptage des arrêts sur les entrées. Chargement des messages FastF1 pour les suppressions de tours.

### Fonctions d’analyse

Comparaison temporelle par distance, zones de gain et freinages. Simulation paramétrable d’un arrêt déplacé, validation des bornes et des arrêts voisins. Export HTML autonome avec constats calculés, statistiques, graphiques et limites ; export CSV du scénario séparé.

### Présentation

Thème sombre anthracite/rouge, cartes de statistiques, couleurs des équipes depuis les résultats et palette de secours. Unités des signaux et explications sous les graphiques. Navigation par section pour éviter de calculer les vues cachées.

### Vérification

Tests de régression dans `tests/test_reliability.py` : abandon, tour de retard, classement officiel, données manquantes, filtres, arrêts, alignement télémétrique, scénario identique et export HTML. Vérification des sections par Streamlit AppTest. Les appels réels FastF1 ne sont pas validés par ces tests hors ligne. La validation esthétique dans un navigateur est distincte des tests fonctionnels.

### Optimisation du chargement FastF1

Le chargement initial utilise désormais `telemetry=False`. Il conserve les tours, les résultats et les messages nécessaires au filtrage. La section Télémétrie déclenche séparément le chargement lourd et extrait uniquement les pilotes sélectionnés.

Un cache JSON des données préparées est enregistré dans `data/cache/prepared`, avec clé de session versionnée, expiration après six heures et écriture atomique. Les télémétries sont enregistrées par pilote : ajouter un pilote ne recalcule pas ceux déjà préparés. Une absence de données n’est pas conservée sur disque. Un fichier absent, expiré ou illisible déclenche un nouveau chargement. Le cache mémoire Streamlit expire après une heure et limite le nombre d’entrées. Les fichiers préparés expirés sont remplacés au prochain accès ; il n’existe pas de purge automatique globale.

Les indicateurs de chargement distinguent les temps/résultats de la télémétrie. Limite : FastF1 télécharge encore les flux de la session entière au premier accès télémétrique ; le filtrage par pilote réduit l’extraction et le cache préparé, pas le téléchargement initial de ces flux. Le cache FastF1 existant est conservé. Les caches peuvent rester en retard sur des données en cours de correction : ce dashboard vise l’analyse après session.

Tests hors ligne ajoutés : télémétrie désactivée au démarrage, cache disque réutilisé, extraction des seuls pilotes manquants, expiration, fichier corrompu, sélection vide et paramètres de session. Aucun facteur d’accélération chiffré n’est annoncé sans mesure réseau réelle.

### Migration vers Jolpica comme source par défaut

Ajout de `src/f1_analysis/jolpica.py`, un adaptateur HTTP sans compte : calendrier réel pour résoudre le numéro de manche, résultats officiels, tours et arrêts paginés. La pagination des tours compte les chronos individuels, pas les objets tour. Requêtes espacées de 0,3 seconde, timeout connexion 5 s / lecture 20 s, identification de l’application et erreur explicite pour HTTP 429. Cache préparé séparé de celui de FastF1.

Le dashboard propose Jolpica en premier et limite sa session à Race. La médiane utilise les tours hors arrêt et hors tour suivant, dans un mode non vérifié distinct d’IsCleanLap. Aucun drapeau vert ni tour précis n’est inventé. Le classement conserve les pilotes DNS et les abandons, le nombre de tours et les arrêts officiels. Les temps finaux officiels servent à calculer l’écart quand ils sont disponibles ; sinon il reste indisponible.

La stratégie Jolpica affiche seulement les arrêts et leurs durées enregistrées. Les secteurs, la télémétrie, les pneus et la simulation affichent leur indisponibilité. Le rapport HTML suit les mêmes limites et n’invente pas de relais pneus. Les anciennes notes décrivent les étapes précédentes ; pour l’état actuel, consulter [[Jolpica]].

Validation : 23 tests hors ligne réussis. Test réseau réel Monaco 2024 : 20 pilotes, 1237 lignes dont entrées sans temps, environ 9,83 s au premier accès et 0,074 s au cache disque. Ces durées sont une mesure ponctuelle, pas une garantie. Rapport d’exemple produit dans `reports/monaco_2024_jolpica.html` (fichier généré ignoré par Git).

### Chargement persistant après migration

Le serveur Streamlit lancé avant l’intégration Jolpica a été redémarré pour recharger les modules Python. Validation dans un processus neuf : lecture de Monaco depuis le cache en 0,086 s, quatre indicateurs affichés et aucune exception AppTest. Après modification du routage d’une source, un redémarrage complet évite de conserver des fonctions importées d’une ancienne version.

### Connexion au compte F1 depuis le dashboard

Ajout du panneau « Connexion au compte F1 » dans la barre latérale : état du jeton local FastF1, connexion navigateur via le CLI FastF1 3.9, lien de connexion, annulation, expiration du processus après cinq minutes et déconnexion. Le mode FastF1 est bloqué avant tout téléchargement si aucun jeton valide n’est enregistré. Le bouton « Utiliser FastF1 » sélectionne la source après connexion.

Le mot de passe et le jeton ne sont jamais affichés ni conservés dans les widgets Streamlit. FastF1 gère son stockage local. Le compte est partagé par les onglets et utilisateurs de cette instance locale : ce mécanisme n’est pas une authentification multi-utilisateur pour un site public. La connexion navigateur officielle FastF1 utilise une extension ; le terminal est proposé comme alternative. L’adaptateur de statut utilise l’API interne de FastF1 3.9, isolée dans `f1_auth.py` et à revérifier lors des mises à jour.

Les tests couvrent le lien autorisé, l’annulation et l’absence de téléchargement lorsque déconnecté. La connexion réelle avec abonnement doit être effectuée par le propriétaire du compte ; elle n’a pas été validée avec des identifiants réels.

### Lisibilité du tableau de tours

La vue Données et rapport affiche désormais une table de lecture limitée aux colonnes Tour, Pilote, Écurie, Chrono, Type de tour et durée aux stands si disponible. Les temps utilisent min:s avec millisecondes, les lignes sont espacées de 44 px et alternent deux fonds doux. Les en-têtes sont contrastés sans couleurs vives, et l’accent des contrôles devient bleu discret. Un filtre pilote et un sélecteur Vue lisible / Données brutes gardent l’accès aux informations détaillées. L’export CSV conserve toutes les colonnes des pilotes sélectionnés, indépendamment du filtre visuel.
