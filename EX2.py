
import itertools, random

COUT = [[5, 3, 4],      # D1 -> M1, M2, M3
        [6, 7, 2]]      # D2 -> M1, M2, M3
OFFRE = [8, 9]          # colonne "Dépôt" : containers disponibles
DEMANDE = [4, 5, 8]     # demandes des magasins

def cout_total(x):
    return sum(COUT[i][j] * x[i][j] for i in range(2) for j in range(3))

def solution_initiale():
    off, dem = OFFRE[:], DEMANDE[:]
    x = [[0]*3 for _ in range(2)]
    for c, i, j in sorted((COUT[i][j], i, j) for i in range(2) for j in range(3)):
        q = min(off[i], dem[j]); x[i][j] += q; off[i] -= q; dem[j] -= q
    return x

def coin_nord_ouest():
    off, dem = OFFRE[:], DEMANDE[:]
    x = [[0]*3 for _ in range(2)]
    i = j = 0
    while i < 2 and j < 3:
        q = min(off[i], dem[j]); x[i][j] = q; off[i] -= q; dem[j] -= q
        if off[i] == 0: i += 1
        else: j += 1
    return x

def voisins(x):
    res = []
    for j, l in itertools.permutations(range(3), 2):
        # i=0,k=1 : +1 en (0,j),(1,l) ; -1 en (0,l),(1,j)
        if x[0][l] > 0 and x[1][j] > 0:
            y = [r[:] for r in x]
            y[0][j] += 1; y[1][l] += 1; y[0][l] -= 1; y[1][j] -= 1
            res.append(((0, j, l), y))
    return res

def tabou(taille_tabou=5, max_iter=10, init=None):
    s = init if init else solution_initiale(); best = [r[:] for r in s]
    tabou = [str(s)]
    historique = [(0, cout_total(s), None)]
    for k in range(1, max_iter+1):
        cand = [(cout_total(y), m, y) for m, y in voisins(s) if str(y) not in tabou]
        if not cand: break
        c, m, s = min(cand, key=lambda t: t[0])
        tabou.append(str(s)); tabou = tabou[-taille_tabou:]
        if c < cout_total(best): best = [r[:] for r in s]
        historique.append((k, c, m))
    return best, historique

def optimum_exact():
    meilleur = None
    for a in range(0, 9):
        for b in range(0, 6):
            for c in range(0, 9):
                if a+b+c == OFFRE[0]:
                    x = [[a, b, c], [DEMANDE[0]-a, DEMANDE[1]-b, DEMANDE[2]-c]]
                    if min(x[1]) >= 0 and sum(x[1]) == OFFRE[1]:
                        if meilleur is None or cout_total(x) < cout_total(meilleur): meilleur = x
    return meilleur

if __name__ == "__main__":
    s0 = coin_nord_ouest()
    print("Solution initiale", s0, "cout =", cout_total(s0))
    best, h = tabou(init=s0)
    for k, c, m in h: print(k, c, m)
    print("Meilleure solution tabou", best, "cout =", cout_total(best))
    ex = optimum_exact(); print("Optimum exact", ex, "cout =", cout_total(ex))

