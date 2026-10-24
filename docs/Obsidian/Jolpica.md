# Jolpica : état actuel du mode gratuit

Jolpica est désormais la source par défaut. FastF1 est optionnel et la démo reste disponible. Voir [[Architecture]] et [[Méthodes et limites]] pour les méthodes historiques FastF1, et [[Journal des changements]] pour la migration.

## Parcours conseillé

Lancer Streamlit, garder Jolpica, saison 2024, Monaco, Race. Comparer LEC et NOR. Montrer les résultats et les temps bruts ; préciser que la médiane hors stands inclut potentiellement SC/VSC. La page Stratégie montre les arrêts et leurs durées, sans gommes. Données et rapport permet d’exporter le CSV et le rapport HTML autonome.

## Garanties et limites

- Aucun compte requis pour cette intégration. L’API publique peut ralentir ou limiter les requêtes.
- Les tours sont paginés sans tronquer la course aux cent premiers chronos.
- Les courses futures ou non publiées affichent une erreur. Pas de substitution silencieuse par des données démo.
- Les trous de chronométrage restent manquants ; les écarts cumulés s’interrompent.
- Les pilotes sans tour sont conservés avec leur nombre de tours officiel égal à zéro. Une ligne technique sans temps permet de conserver leur résultat dans le tableau.
- Le rythme est non vérifié, hors tour d’arrêt et tour suivant. Aucun indicateur de tour propre n’est attribué. Drapeaux, suppression des tours et secteurs sont absents.
- Les durées des arrêts peuvent inclure entrée, sortie et drapeau rouge. Ce n’est pas une mesure du travail des mécaniciens ni une perte nette.
- Pneus, dégradation, télémétrie et simulation sont indisponibles dans ce mode.
- Résultats officiels prioritaires. Écart final calculé avec les temps officiels quand disponibles. Un écart cumulé sur le même tour n’est pas un intervalle en direct.
- Cache JSON séparé, six heures sur disque ; mémoire une heure. Adapté à l’analyse après course.

Documentation primaire : [API Jolpica](https://github.com/jolpica/jolpica-f1/tree/main/docs), [tours](https://github.com/jolpica/jolpica-f1/blob/main/docs/endpoints/laps.md), [arrêts](https://github.com/jolpica/jolpica-f1/blob/main/docs/endpoints/pitstops.md).
