"""
Exercice 2 : placer k jetons sur une grille n x n de sorte que chaque ligne et
chaque colonne contienne un nombre PAIR de jetons (exemple : n = 5, k = 10).
Résolu par algorithme génétique (AG).

Codage     : un individu = ensemble de k cases distinctes (numérotées 0 à n*n-1).
Fitness    : nombre de lignes et de colonnes qui respectent la parité.
Opérateurs : sélection (tournoi ou loterie), croisement d'ensembles,
             mutation par déplacement d'un jeton, élitisme.
"""
import itertools
import random
from math import comb

N = 5                 # taille de la grille
K = 10                # nombre de jetons (k < n²)
NB_CASES = N * N



def taille_espace(n=N, k=K):
    return comb(n * n, k)


def compter_solutions_faisables(n=N, k=K):
    """Dénombre les grilles faisables ayant exactement k jetons.
    Une grille dont toutes les lignes et colonnes sont paires est entièrement
    déterminée par son bloc (n-1) x (n-1) : on énumère ces 2^((n-1)^2) blocs,
    puis on complète la dernière ligne et la dernière colonne."""
    total, par_poids = 0, {}
    for masque in range(2 ** ((n - 1) ** 2)):
        g = [[(masque >> (i * (n - 1) + j)) & 1 for j in range(n - 1)] + [0] for i in range(n)]
        for i in range(n - 1):
            g[i][n - 1] = sum(g[i][:n - 1]) % 2
        for j in range(n):
            g[n - 1][j] = sum(g[i][j] for i in range(n - 1)) % 2
        poids = sum(map(sum, g))
        par_poids[poids] = par_poids.get(poids, 0) + 1
    return par_poids.get(k, 0), 2 ** ((n - 1) ** 2)

def individu_aleatoire():
    return random.sample(range(NB_CASES), K)


def vers_grille(ind):
    g = [[0] * N for _ in range(N)]
    for case in ind:
        g[case // N][case % N] = 1
    return g

def violations(ind):
    """Nombre de lignes + colonnes contenant un nombre impair de jetons."""
    g = vers_grille(ind)
    lignes = sum(sum(g[i]) % 2 for i in range(N))
    colonnes = sum(sum(g[i][j] for i in range(N)) % 2 for j in range(N))
    return lignes + colonnes


def fitness(ind):
    """2n - (nombre de lignes/colonnes impaires) : vaut 2n = 10 si faisable."""
    return 2 * N - violations(ind)


def est_faisable(ind):
    return violations(ind) == 0

def selection_tournoi(pop, fits, k=3):
    candidats = random.sample(range(len(pop)), k)
    return pop[max(candidats, key=lambda i: fits[i])]


def selection_loterie(pop, fits):
    total = sum(fits)
    tirage, cumul = random.uniform(0, total), 0
    for ind, f in zip(pop, fits):
        cumul += f
        if cumul >= tirage:
            return ind
    return pop[-1]


def croisement(p1, p2):
    """Croisement d'ensembles : les cases communes aux deux parents sont
    conservées ; on complète avec des cases tirées parmi celles qui ne sont
    que chez un seul parent. Chaque enfant a toujours exactement k cases
    distinctes (pas de réparation nécessaire)."""
    communs = set(p1) & set(p2)
    autres = list(set(p1) ^ set(p2))
    enfants = []
    for _ in range(2):
        random.shuffle(autres)
        enfants.append(list(communs) + autres[:K - len(communs)])
    return enfants[0], enfants[1]


def mutation(ind, pm=0.3):
    """Avec la probabilité pm, un jeton est déplacé vers une case vide."""
    ind = ind[:]
    if random.random() < pm:
        i = random.randrange(K)
        libres = [c for c in range(NB_CASES) if c not in ind]
        ind[i] = random.choice(libres)
    return ind

def algo_genetique(taille_pop=50, generations=200, pc=0.8, pm=0.3,
                   selection=selection_tournoi, elitisme=2, graine=None):
    if graine is not None:
        random.seed(graine)
    pop = [individu_aleatoire() for _ in range(taille_pop)]
    historique = []
    for g in range(generations + 1):
        fits = [fitness(i) for i in pop]
        ordre = sorted(range(taille_pop), key=lambda i: fits[i], reverse=True)
        historique.append((g, fits[ordre[0]], sum(fits) / taille_pop))
        if fits[ordre[0]] == 2 * N or g == generations:     # solution faisable trouvée
            return pop[ordre[0]], historique
        nouvelle = [pop[i][:] for i in ordre[:elitisme]]
        while len(nouvelle) < taille_pop:
            p1, p2 = selection(pop, fits), selection(pop, fits)
            e1, e2 = croisement(p1, p2) if random.random() < pc else (p1[:], p2[:])
            nouvelle += [mutation(e1, pm), mutation(e2, pm)]
        pop = nouvelle[:taille_pop]

def afficher(ind):
    g = vers_grille(ind)
    for i in range(N):
        print("   " + " ".join("●" if x else "·" for x in g[i]) + f"   | {sum(g[i])}")
    print("   " + "-" * (2 * N - 1))
    print("   " + " ".join(str(sum(g[i][j] for i in range(N))) for j in range(N)))
    print("   jetons :", len(ind), "  faisable :", est_faisable(ind))

if __name__ == "__main__":
    def fmt(x):
        return f"{x:,}".replace(",", " ")

    print(f"n = {N}, k = {K}")
    print(f"Espace de recherche C({NB_CASES},{K}) = {fmt(taille_espace())}")
    print(f"Sans fixer k (codage binaire libre) : 2^{NB_CASES} = {fmt(2 ** NB_CASES)}")
    nb, nb_total = compter_solutions_faisables()
    print(f"Grilles faisables avec exactement k = {K} jetons : {fmt(nb)} "
          f"({100 * nb / taille_espace():.2f} % de l'espace)")
    print(f"Grilles faisables (tous nombres de jetons) : 2^{(N - 1) ** 2} = {fmt(nb_total)}")

    print("\nAlgorithme génétique, graine 1 :")
    best, hist = algo_genetique(graine=1)
    for g, b, moy in hist:
        print(f"  génération {g:3d} : meilleure fitness = {b:2d}   moyenne = {moy:5.2f}")
    afficher(best)

    NB = 100
    print(f"\nComparaison sur {NB} exécutions :")
    for nom, sel in (("tournoi", selection_tournoi), ("loterie", selection_loterie)):
        gens = []
        for s in range(NB):
            b, h = algo_genetique(graine=s, selection=sel)
            if est_faisable(b):
                gens.append(h[-1][0])
        print(f"  sélection {nom:8s} : {len(gens)}/{NB} solutions faisables, "
              f"génération moyenne = {sum(gens)/max(1,len(gens)):.1f}")
