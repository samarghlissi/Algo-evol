"""
Exercice 1 : Robot dans un labyrinthe resolu par algorithme genetique.

1) Codage      : individu = liste de L deplacements (0=haut, 1=bas, 2=gauche, 3=droite)
2) Fitness     : on simule le robot ; il s'arrete s'il touche un mur, sort de la grille,
                 revisite une case ou atteint la sortie. Plus il finit proche de la sortie
                 (et plus il a avance sans erreur), meilleure est la fitness.
3) Mutation    : remplacer un gene par un deplacement aleatoire (mutation ponctuelle)
4) Operateurs  : selection par tournoi, croisement a un point, mutation, elitisme.
"""
import random

# Labyrinthe (0 = case blanche, 1 = mur/case tramee)
# Depart : case (1,1) en haut a gauche -> indice [0][0]
# Sortie : case (10,10) en bas a droite -> indice [9][9]
# >>> Adaptez cette grille a la Figure 1 de votre sujet (1 = case grisee). <<<
LABY = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 1, 1, 1, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 1, 1, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [1, 1, 1, 1, 1, 0, 0, 0, 1, 0],
]
N = len(LABY)
DEPART = (0, 0)
SORTIE = (N - 1, N - 1)
MOUVEMENTS = {0: (-1, 0), 1: (1, 0), 2: (0, -1), 3: (0, 1)}  # haut, bas, gauche, droite

#Parametres de l'AG
L = 40               # longueur d'un individu (nb de deplacements)
TAILLE_POP = 100
NB_GENERATIONS = 300
P_CROISEMENT = 0.9
P_MUTATION = 0.05    # probabilite de mutation par gene
TAILLE_TOURNOI = 3
ELITES = 2


# 1) Codage
def creer_individu():
    return [random.randint(0, 3) for _ in range(L)]


def creer_population():
    return [creer_individu() for _ in range(TAILLE_POP)]


# Simulation du robot
def parcours(ind):
    """Retourne la liste des cases visitees par le robot."""
    pos = DEPART
    visites = [pos]
    for g in ind:
        dx, dy = MOUVEMENTS[g]
        nx, ny = pos[0] + dx, pos[1] + dy
        if not (0 <= nx < N and 0 <= ny < N):   # sortie de la grille
            break
        if LABY[nx][ny] == 1:                    # mur
            break
        if (nx, ny) in visites:                  # case deja visitee
            break
        pos = (nx, ny)
        visites.append(pos)
        if pos == SORTIE:
            break
    return visites


# 2) Fonction fitness (a maximiser)
def fitness(ind):
    visites = parcours(ind)
    fin = visites[-1]
    dist = abs(fin[0] - SORTIE[0]) + abs(fin[1] - SORTIE[1])   # distance de Manhattan
    f = 2 * (N - 1) - dist            # 0 .. 18 : proximite de la sortie
    f += 0.1 * len(visites)           # petit bonus pour les chemins longs sans erreur
    if fin == SORTIE:
        f += 100 - len(visites)       # gros bonus + preference au chemin court
    return f


# Selection
def selection_tournoi(pop, fits):
    candidats = random.sample(range(len(pop)), TAILLE_TOURNOI)
    meilleur = max(candidats, key=lambda i: fits[i])
    return pop[meilleur][:]


# Croisement (un point)
def croisement(p1, p2):
    if random.random() < P_CROISEMENT:
        pt = random.randint(1, L - 1)
        return p1[:pt] + p2[pt:], p2[:pt] + p1[pt:]
    return p1[:], p2[:]


# 3) Mutation
def mutation(ind):
    for i in range(L):
        if random.random() < P_MUTATION:
            ind[i] = random.randint(0, 3)
    return ind


# 4) Alogorithme genetique
def algorithme_genetique():
    pop = creer_population()
    meilleur, meilleur_fit = None, -1
    for gen in range(NB_GENERATIONS):
        fits = [fitness(i) for i in pop]
        idx = max(range(len(pop)), key=lambda i: fits[i])
        if fits[idx] > meilleur_fit:
            meilleur, meilleur_fit = pop[idx][:], fits[idx]
        if gen % 20 == 0:
            print(f"Generation {gen:3d} | meilleure fitness = {meilleur_fit:.1f}")
        if parcours(meilleur)[-1] == SORTIE:
            print(f"Sortie trouvee a la generation {gen}")
            break

        # elitisme
        tri = sorted(range(len(pop)), key=lambda i: fits[i], reverse=True)
        nouvelle = [pop[i][:] for i in tri[:ELITES]]
        while len(nouvelle) < TAILLE_POP:
            p1 = selection_tournoi(pop, fits)
            p2 = selection_tournoi(pop, fits)
            e1, e2 = croisement(p1, p2)
            nouvelle += [mutation(e1), mutation(e2)]
        pop = nouvelle[:TAILLE_POP]
    return meilleur, meilleur_fit


def afficher(ind):
    chemin = parcours(ind)
    for i in range(N):
        ligne = ""
        for j in range(N):
            if (i, j) == DEPART:
                ligne += " D "
            elif (i, j) == SORTIE:
                ligne += " S "
            elif (i, j) in chemin:
                ligne += " . "
            elif LABY[i][j] == 1:
                ligne += "###"
            else:
                ligne += "   "
        print(ligne)
    print("Chemin (ligne, colonne) :", [(a + 1, b + 1) for a, b in chemin])


if __name__ == "__main__":
    sol, f = algorithme_genetique()
    print("\nMeilleur individu :", sol)
    print("Fitness :", f)
    afficher(sol)