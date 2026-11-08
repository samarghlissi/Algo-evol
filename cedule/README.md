# Ordonnancement de la maintenance par algorithme génétique

Heuristiques & Méta-heuristiques – LSI3 – Faculté des Sciences de Sfax
Réalisé par : **Ghlissi Samar** – Groupe : **LSI3 3TP2**

## Problème

Planifier la maintenance de 7 centrales électriques sur 4 intervalles de l'année, de façon à **maximiser la puissance en réserve**.

| Unité | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| Capacité (MW) | 20 | 15 | 35 | 40 | 15 | 15 | 10 |
| Intervalles de maintenance | 2 | 2 | 1 | 1 | 1 | 1 | 1 |

Demande par intervalle : 80, 90, 65 et 70 MW. Capacité totale : 150 MW.

## Formulation

- **Variable de décision** : `x_ut = 1` si l'unité `u` est en maintenance pendant l'intervalle `t`, 0 sinon.
- **Contraintes** : chaque unité reçoit exactement le nombre d'intervalles de maintenance requis, **consécutifs** ; la réserve de chaque intervalle doit être positive ou nulle.
- **Réserve** : `R_t = 150 − (puissance en maintenance à t) − demande_t`
- **Fonction objectif** : maximiser `min(R_1, R_2, R_3, R_4)`. La performance d'un chromosome vaut 0 si une réserve est négative.

## Codage

Un gène de 4 bits par unité : le bit `k` vaut 1 si l'unité est en maintenance à l'intervalle `k`. Exemple : `1100` = maintenance aux intervalles 1 et 2.

| Unités | Gènes possibles |
|---|---|
| 1 et 2 (durée 2) | `1100`, `0110`, `0011` |
| 3 à 7 (durée 1) | `1000`, `0100`, `0010`, `0001` |

Un chromosome est la suite des 7 gènes. Croisement et mutation ne touchent que des **blocs de 4 bits**, pour que les cédules restent valides.

## Opérateurs génétiques

| Opérateur | Choix |
|---|---|
| Sélection | **Loterie** (roulette : probabilité proportionnelle à la performance) |
| Croisement | 1 point, placé entre deux blocs de 4 bits (pc = 0,8) |
| Mutation principale | **Inversion** : inversion de l'ordre de gènes de même type (pm = 0,2) |
| Autres mutations testées | inversion miroir des bits, remplacement de gène, échange de gènes |
| Élitisme | les 2 meilleurs individus sont conservés |
| Population / générations | 50 individus, 100 générations |

## Fichiers

- `exercice_cedule.py` : le programme complet, commenté (données, codage, performance, sélection, croisement, mutations, AG, comparaison)
- `captures/ex4.png` : capture de l'exécution

## Exécution

```bash
python exercice_cedule.py
```

Aucune bibliothèque obligatoire. Pour obtenir la courbe de convergence (`convergence.png`), installer `matplotlib` (`pip install matplotlib`) ; sinon le programme l'ignore.

## Résultats

- **Vérification** sur l'exemple du cours : réserves 20, 25, 35, 30, donc performance 20.
- **Optimum exact** (énumération des 9 216 plannings) : **25 MW**, par exemple `1100 1100 0010 0001 0010 0001 1000` (réserves 25, 25, 35, 25). Seuls 43 plannings sur 9 216 l'atteignent.
- **AG (loterie + inversion)**, population 50 : optimum trouvé dans 30 exécutions sur 30.
- **Comparaison des mutations**, population 10, 40 générations, 100 exécutions :

| Mutation | Performance moyenne | Optimum atteint |
|---|---|---|
| Remplacement de gène | 21,25 | 48 / 100 |
| Inversion (segment de gènes) | 20,35 | 37 / 100 |
| Échange de gènes | 20,35 | 34 / 100 |
| Inversion miroir (bits) | 18,70 | 25 / 100 |

L'inversion et l'échange ne font que réarranger des gènes déjà présents ; le remplacement peut en introduire de nouveaux, ce qui explique son avantage avec une petite population.

### Capture d'exécution

![Exécution exercice 4](captures/ex4.png)
