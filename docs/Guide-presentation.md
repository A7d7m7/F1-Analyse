# Présenter le projet et répondre aux questions

## Présentation en 30 secondes

« J’ai développé un dashboard Python pour comparer les performances et les stratégies en Formule 1. Il utilise Streamlit pour l’interface, pandas et NumPy pour les calculs, Plotly pour les graphiques et FastF1 pour les données réelles. Je peux comparer le rythme sur des tours propres, examiner les pneus et la télémétrie, explorer un scénario d’arrêt et exporter un rapport HTML. »

## Pourquoi ce projet ?

« Je voulais transformer des données sportives en analyses visuelles compréhensibles, en faisant attention aux pièges comme les abandons, les tours de retard et la Safety Car. »

## Comment évites-tu un classement trompeur ?

« Je privilégie le résultat officiel. À défaut, je compare d’abord les tours parcourus puis le temps. Un pilote qui abandonne ne devient donc pas premier parce que son temps total est plus court. Les retards d’un tour ne sont pas affichés comme des secondes. »

## Comment compares-tu le rythme ?

« Je garde les tours précis, non supprimés, hors entrée et sortie des stands et entièrement sous drapeau vert. Je compare ensuite la médiane et les secteurs. Les statuts inconnus sont exclus. Cela limite les biais sans rendre toutes les conditions identiques. »

## La dégradation est-elle exacte ?

« C’est une pente observée des temps, pas une mesure physique de l’usure. Le carburant et le trafic interviennent aussi. Avec moins de quatre tours propres, je ne donne pas d’estimation. »

## Que représente l’écart télémétrique ?

« J’aligne les temps écoulés sur une distance commune par interpolation. Un écart positif indique que le pilote comparé est plus lent. Une baisse indique une zone où il gagne du temps. Les zones sont des portions de distance, pas des virages détectés automatiquement. »

## Peux-tu prédire la meilleure stratégie ?

« Pas avec ce modèle. C’est une simulation pédagogique à rythme et dégradation simplifiés. Elle permet d’explorer un arrêt avancé ou retardé, mais elle ignore le trafic, la météo et les réactions des autres pilotes. Je présente toujours ces hypothèses. »

## Y a-t-il de l’intelligence artificielle ?

« Non, l’analyse actuelle repose sur des statistiques et un modèle explicite. Les constats du rapport sont calculés à partir des données. Je n’ai pas entraîné de modèle prédictif. »

## Comment as-tu vérifié le projet ?

« Avec des tests de cas comme un abandon, un pilote à un tour, un temps manquant et un arrêt déplacé de zéro tour. J’ai aussi vérifié les différentes sections avec AppTest. Les tests hors ligne ne prouvent pas la disponibilité des données réelles. »

## Pourquoi Streamlit et pas une application entièrement HTML ?

« Streamlit permet de garder les calculs et les interactions en Python. Le thème et les cartes donnent une présentation de dashboard ; Plotly apporte les graphiques interactifs. Le rapport exporté est un fichier HTML autonome. »

## Quelle est la prochaine amélioration ?

« Valider sur plusieurs vraies courses, mieux prendre en compte les pénalités et les interruptions, puis ajouter un modèle par gomme avec carburant et trafic. »

## Comment parler de l’aide reçue ?

« J’ai utilisé un assistant de développement pour m’aider à implémenter et tester les évolutions. Je dois pouvoir expliquer les calculs, leurs limites et les choix techniques ; la documentation du projet sert de support. »

## Comment as-tu accéléré le chargement ?

« J’ai séparé les données légères de la télémétrie. Les temps et résultats se chargent d’abord ; la télémétrie arrive seulement dans sa section. Je garde aussi les données préparées sur disque pendant six heures, avec un cache par pilote pour éviter les extractions répétées. Le premier téléchargement télémétrique peut rester lent, car FastF1 récupère les flux de toute la session. Je n’annonce pas de gain chiffré sans mesure réelle. »

## Mise à jour : quelle source utilise le projet aujourd’hui ?

« Le mode principal est Jolpica, une API gratuite sans compte pour les résultats, les temps au tour et les arrêts. FastF1 reste optionnel pour les données détaillées et nécessite désormais un accès F1 TV adapté. »

## Peux-tu filtrer les Safety Cars avec Jolpica ?

« Non. Le mode gratuit retire les tours d’arrêt et le tour suivant, mais les drapeaux ne sont pas fournis. J’affiche donc une médiane hors stands non vérifiée, jamais un rythme certifié sous drapeau vert. Les fonctionnalités liées aux pneus ou à la télémétrie indiquent clairement qu’elles sont indisponibles. Les réponses précédentes sur les tours propres concernent FastF1 et la démo. »

## Pourquoi les durées de stands semblent parfois très longues ?

« Jolpica peut inclure dans ces durées le passage dans la voie des stands ou une interruption sous drapeau rouge. Je les présente comme des durées enregistrées, pas comme une durée de changement de pneus ou une perte nette. »

## Comment sais-tu que tous les tours ont été récupérés ?

« L’API limite la taille des pages. Je parcours ces pages en comptant les chronos de chaque pilote. C’est testé hors ligne, et le mode a aussi été vérifié sur Monaco 2024 avec vingt pilotes. »

## Comment se connecter à F1 TV ?

« J’ouvre Connexion au compte F1 dans la barre latérale, puis Se connecter à F1 TV. Le lien mène au parcours navigateur de FastF1 avec son extension. Après connexion, Utiliser FastF1 sélectionne la source. Une commande terminal est aussi disponible. Les identifiants ne passent pas par les formulaires du dashboard ; FastF1 conserve son jeton local. Cette connexion concerne la machine locale, pas des comptes séparés par utilisateur d’un site public. »
