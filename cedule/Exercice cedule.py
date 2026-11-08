

import itertools
import random

CAPACITE = [20, 15, 35, 40, 15, 15, 10]   # capacité de chaque unité (MW)
DUREE    = [2, 2, 1, 1, 1, 1, 1]          # nombre d'intervalles de maintenance requis
DEMANDE  = [80, 90, 65, 70]               # demande en puissance par intervalle (MW)

N_UNITES = len(CAPACITE)                  # 7 unités
N_INTERVALLES = len(DEMANDE)              # 4 intervalles
CAPACITE_TOTALE = sum(CAPACITE)           # 150 MW


# =====================================================================
# 2. CODAGE : un chromosome = 7 gènes de 4 bits (un gène par unité)
# =====================================================================
def genes_possibles(duree):
    res = []
    for debut in range(N_INTERVALLES - duree + 1):
        res.append("".join("1" if debut <= t < debut + duree else "0"
                           for t in range(N_INTERVALLES)))
    return res


GENES = [genes_possibles(d) for d in DUREE]
GROUPES = []
for i in range(N_UNITES):
    if GROUPES and GENES[GROUPES[-1][0]] == GENES[i]:
        GROUPES[-1].append(i)
    else:
        GROUPES.append([i])


def chromosome_aleatoire():
    return [random.choice(GENES[u]) for u in range(N_UNITES)]


# =====================================================================
#  FONCTION OBJECTIF (performance du chromosome)
# =====================================================================
def puissance_en_maintenance(chrom):
    """Puissance perdue (MW) dans chaque intervalle."""
    return [sum(CAPACITE[u] for u in range(N_UNITES) if chrom[u][t] == "1")
            for t in range(N_INTERVALLES)]


def reserves(chrom):
    """Réserve = capacité totale - puissance en maintenance - demande."""
    pm = puissance_en_maintenance(chrom)
    return [CAPACITE_TOTALE - pm[t] - DEMANDE[t] for t in range(N_INTERVALLES)]


def performance(chrom):
    """Performance = plus petite réserve ; 0 si une réserve est négative."""
    return max(0, min(reserves(chrom)))

def selection_loterie(population, perfs):
    total = sum(perfs)
    if total == 0:                       # tous à 0 : tirage uniforme
        return random.choice(population)
    tirage = random.uniform(0, total)
    cumul = 0
    for individu, p in zip(population, perfs):
        cumul += p
        if cumul >= tirage:
            return individu
    return population[-1]

def croisement(p1, p2):
    point = random.randint(1, N_UNITES - 1)
    return p1[:point] + p2[point:], p2[:point] + p1[point:]

def mutation_inversion(chrom):
    c = chrom[:]
    groupes = [g for g in GROUPES if len(g) >= 2]
    g = random.choice(groupes)
    i, j = sorted(random.sample(range(len(g)), 2))
    idx = g[i:j + 1]
    valeurs = [c[k] for k in idx][::-1]
    for k, v in zip(idx, valeurs):
        c[k] = v
    return c


def mutation_inversion_bits(chrom):
    c = chrom[:]
    u = random.randrange(N_UNITES)
    c[u] = c[u][::-1]
    return c


def mutation_remplacement(chrom):
    c = chrom[:]
    u = random.randrange(N_UNITES)
    autres = [g for g in GENES[u] if g != c[u]]
    c[u] = random.choice(autres)
    return c


def mutation_echange(chrom):
    c = chrom[:]
    g = random.choice([g for g in GROUPES if len(g) >= 2])
    a, b = random.sample(g, 2)
    c[a], c[b] = c[b], c[a]
    return c


MUTATIONS = {
    "inversion (segment de gènes)": mutation_inversion,
    "inversion miroir (bits)": mutation_inversion_bits,
    "remplacement de gène": mutation_remplacement,
    "échange de gènes": mutation_echange,
}


# =====================================================================
#  ALGORITHME GÉNÉTIQUE
# =====================================================================
def algo_genetique(taille_pop=50, generations=100, pc=0.8, pm=0.2,
                   mutation=mutation_inversion, elitisme=2, graine=None):
    if graine is not None:
        random.seed(graine)
    population = [chromosome_aleatoire() for _ in range(taille_pop)]
    historique = []                                   # meilleure perf par génération
    meilleur = None
    for g in range(generations + 1):
        perfs = [performance(c) for c in population]
        ordre = sorted(range(taille_pop), key=lambda i: perfs[i], reverse=True)
        if meilleur is None or perfs[ordre[0]] > performance(meilleur):
            meilleur = population[ordre[0]][:]
        historique.append((g, perfs[ordre[0]], sum(perfs) / taille_pop))
        if g == generations:
            break
        # nouvelle génération : élitisme + sélection/croisement/mutation
        nouvelle = [population[i][:] for i in ordre[:elitisme]]
        while len(nouvelle) < taille_pop:
            p1 = selection_loterie(population, perfs)
            p2 = selection_loterie(population, perfs)
            if random.random() < pc:
                e1, e2 = croisement(p1, p2)
            else:
                e1, e2 = p1[:], p2[:]
            for e in (e1, e2):
                if random.random() < pm:
                    e = mutation(e)
                if len(nouvelle) < taille_pop:
                    nouvelle.append(e)
        population = nouvelle
    return meilleur, historique
def optimum_exact():
    meilleur, perf_max = None, -1
    for combi in itertools.product(*GENES):
        p = performance(list(combi))
        if p > perf_max:
            meilleur, perf_max = list(combi), p
    return meilleur, perf_max


def afficher(chrom):
    print("  chromosome :", " ".join(chrom))
    print("  puissance en maintenance :", puissance_en_maintenance(chrom))
    print("  réserves                 :", reserves(chrom),
          "-> performance =", performance(chrom))
def comparer(mutations, nb_runs, perf_opt, **params):
    print(f"{'mutation':32s} {'moy.':>6s} {'min':>4s} {'max':>4s} {'optimum atteint':>18s}")
    for nom, mut in mutations.items():
        res = [performance(algo_genetique(mutation=mut, graine=s, **params)[0])
               for s in range(nb_runs)]
        print(f"{nom:32s} {sum(res)/nb_runs:6.2f} {min(res):4d} {max(res):4d} "
              f"{sum(r == perf_opt for r in res):14d}/{nb_runs}")


def tracer_convergence(nb_runs=100, fichier="convergence.png", **params):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib non installé : courbe ignorée (pip install matplotlib)")
        return
    plt.figure(figsize=(7, 4))
    for nom, mut in MUTATIONS.items():
        courbes = [[b for _, b, _ in algo_genetique(mutation=mut, graine=s, **params)[1]]
                   for s in range(nb_runs)]
        moyenne = [sum(c[g] for c in courbes) / nb_runs for g in range(len(courbes[0]))]
        plt.plot(moyenne, label=nom)
    plt.xlabel("Génération")
    plt.ylabel("Meilleure performance moyenne (MW)")
    plt.title(f"Convergence moyenne sur {nb_runs} exécutions")
    plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig(fichier, dpi=150)
    print("Courbe enregistrée :", fichier)

if __name__ == "__main__":
    # a) Vérification sur l'exemple du cours
    exemple = ["0110", "0011", "0001", "1000", "0100", "0010", "1000"]
    print("Exemple du cours (attendu : réserves 20, 25, 35, 30 -> perf 20)")
    afficher(exemple)

    # b) Optimum exact
    opt, perf_opt = optimum_exact()
    print("\nOptimum exact (énumération de 9216 plannings) :")
    afficher(opt)

    # c) Un run de l'AG (sélection loterie + mutation par inversion)
    print("\nAlgorithme génétique (loterie + inversion), graine 1 :")
    best, hist = algo_genetique(graine=1)
    for g, b, moy in hist[::10]:
        print(f"  génération {g:3d} : meilleure perf = {b:2d}   moyenne = {moy:5.2f}")
    afficher(best)

    # d) Comparaison des mutations : population de 50, 100 générations
    print("\nComparaison des mutations (pop 50, 100 générations, 30 exécutions) :")
    comparer(MUTATIONS, 30, perf_opt, taille_pop=50, generations=100)

    # e) Même comparaison avec une petite population (problème plus difficile)
    print("\nComparaison des mutations (pop 10, 40 générations, 100 exécutions) :")
    comparer(MUTATIONS, 100, perf_opt, taille_pop=10, generations=40)

    # f) Courbe de convergence (facultatif)
    tracer_convergence(nb_runs=100, taille_pop=10, generations=40)
