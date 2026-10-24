# Méthodes et limites

## Classement et abandons

Le résultat officiel FastF1 est prioritaire. Sans résultat, l’ordre est indicatif : nombre de tours décroissant puis somme des temps croissante. Un statut absent reste inconnu : un nombre réduit de tours ne prouve pas un abandon.

Un pilote avec moins de tours reçoit un retard en tours et aucun écart final en secondes. Une donnée manquante invalide l’écart cumulé à partir du premier trou. Le graphique compare le même numéro de tour : ce n’est pas un intervalle en direct, notamment lors des tours pris. La somme des temps n’inclut pas automatiquement tous les effets de départ, pénalités ou interruption.

## Rythme

Un tour propre doit avoir un temps positif, IsAccurate vrai, ne pas être supprimé, ne pas être un tour de stands et avoir TrackStatus exactement égal à `1`. Cela exclut SC, VSC, drapeaux jaunes et rouges, y compris les statuts mixtes. Un statut de piste absent est exclu. Le filtre est volontairement prudent. IsAccurate est un contrôle de synchronisation FastF1, pas une garantie absolue.

Les arrêts sont comptés à partir des entrées aux stands, pas de l’union entrée/sortie. Sans cette information détaillée, IsPitLap constitue un repli approximatif. Les tours de sortie restent exclus du rythme. Le rythme médian, les secteurs et les pentes utilisent les tours propres. Les temps bruts restent visibles.

La pente par relais est une régression linéaire du temps sur le numéro de tour, en s/tour. Au moins quatre tours propres sont nécessaires. Carburant et trafic influencent la pente : il ne faut pas l’appeler mesure pure d’usure des pneus.

## Télémétrie

Interpolation des temps écoulés sur 500 points de distance commune, puis différence pilote − référence, ramenée à zéro au début de la zone commune. Une valeur positive signifie plus lent ; une variation négative indique un gain local. Dix zones de distance sont affichées, sans identification automatique des virages. Les meilleurs tours peuvent provenir de conditions différentes.

Le frein FastF1 est binaire ; le frein démo est une intensité synthétique en pourcentage. Le DRS FastF1 est un code brut. Les absences de télémétrie sont signalées.

## Simulation

Temps au tour = rythme médian propre + pente saisie × âge théorique du pneu + perte fixe au tour d’arrêt. On déplace un arrêt observé sans changer leur nombre ou leur ordre. L’âge est réinitialisé au tour suivant. L’écart est calculé entre deux scénarios du même modèle, pas entre un modèle et la course réelle.

Même gomme et pente dans tous les relais ; pas de carburant, trafic, météo, SC ou réaction adverse. Les pertes identiques aux stands s’annulent dans l’écart final. Ce modèle pédagogique ne recommande pas une stratégie optimale et ne vérifie pas les obligations sportives de composés. La simulation n’est accessible que pour Race et Sprint.

## Sources

- [Schéma de données officiel FastF1](https://github.com/theOehrly/Fast-F1/blob/main/docs/api_reference/timing_data.rst)
- [Premiers pas FastF1](https://github.com/theOehrly/Fast-F1/blob/main/docs/getting_started/basics.rst)
