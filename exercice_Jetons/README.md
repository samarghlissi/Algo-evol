# Exercice 2 : jetons sur une grille (algorithme génétique)

Heuristiques & Méta-heuristiques – LSI3 – Faculté des Sciences de Sfax
Réalisé par : **Nom Prénom** – Groupe : **…**

## Problème

Sur une grille de **n lignes et n colonnes**, on veut placer **k jetons** (k < n²) de sorte que **chaque ligne et chaque colonne contienne un nombre pair de jetons**. Exemple : n = 5, k = 10.

Exemple de solution faisable (n = 5, k = 10), trouvée par le programme :

```
 · · · ● ●   | 2
 ● ● · · ·   | 2
 ● · ● · ·   | 2
 · ● · ● ·   | 2
 · · ● · ●   | 2
 ---------
 2 2 2 2 2
```

## Question 1 : taille de l'espace de recherche

On choisit k cases parmi les n² cases de la grille :

> **C(n², k) = C(25, 10) = 3 268 760 grilles possibles**

Remarques :

- Si on ne fixe pas k (codage binaire libre de 25 cases, chacune pleine ou vide), l'espace est 2²⁵ = 33 554 432.
- Parmi les 3 268 760 grilles, seules **12 840** sont faisables (0,39 %). Ce nombre a été obtenu par deux méthodes qui donnent le même résultat : énumération complète des 3 268 760 grilles, et énumération des 2¹⁶ grilles à lignes et colonnes paires (une grille paire est déterminée par son bloc 4 × 4).
- **k doit être pair** : le nombre total de jetons est la somme des jetons de chaque ligne, qui sont tous pairs. Pour k impair il n'existe aucune solution.

## Question 2a : codage des solutions

Un individu est un **ensemble de k = 10 cases distinctes**, numérotées de 0 à 24 (la case de la ligne i, colonne j porte le numéro 5i + j). Exemple : `[3, 4, 5, 6, 10, 12, 16, 18, 22, 24]`.

Ce codage garantit **par construction** que la grille contient exactement k jetons. L'AG n'a donc à gérer que la contrainte de parité.

## Question 2b : fonction fitness (à maximiser)

On compte les lignes et colonnes qui contiennent un nombre **impair** de jetons (les violations) :

> **fitness = 2n − (lignes impaires + colonnes impaires)**

La fitness vaut 2n = 10 si et seulement si la solution est faisable. Plus il y a de lignes ou de colonnes impaires, plus la fitness diminue.

## Question 2c : code complet

Fichier `exercice_jetons.py`. Les opérateurs implémentés :

| Opérateur | Choix |
|---|---|
| Sélection | tournoi (taille 3) et loterie (roulette) |
| Croisement | croisement d'ensembles : les cases communes aux deux parents sont conservées, on complète avec des cases choisies parmi celles qui ne sont que chez un parent (probabilité 0,8) |
| Mutation | déplacement d'un jeton vers une case vide (probabilité 0,3) |
| Élitisme | les 2 meilleurs individus sont conservés |
| Paramètres | 50 individus, 200 générations maximum, arrêt dès qu'une solution faisable est trouvée |

Le croisement et la mutation produisent toujours des individus valides : exactement k cases distinctes, sans réparation.

## Exécution

```bash
python exercice_jetons.py
```

Aucune bibliothèque externe n'est nécessaire.

## Résultats

Exécution avec graine 1 : la solution faisable est trouvée à la **génération 2**.

| Génération | 0 | 1 | 2 |
|---|---|---|---|
| Meilleure fitness | 8 | 8 | **10** |

Comparaison sur 100 exécutions :

| Sélection | Solutions faisables | Génération moyenne |
|---|---|---|
| Tournoi | 100 / 100 | 3,2 |
| Loterie | 100 / 100 | 4,9 |

Le problème est facile pour l'AG : une solution faisable est trouvée en quelques générations, alors qu'elle représente seulement 0,39 % de l'espace de recherche. Le tournoi est un peu plus rapide que la loterie.

### Capture d'exécution

![Exécution exercice jetons](![execution_ex2.png](capture/execution_ex2.png)captures/execution.png)
