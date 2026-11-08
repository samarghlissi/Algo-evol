
import math, random, itertools

N = 8
INF = 10**4   # arête absente ('-') : pénalité très forte
brut = {  (1,2):14,(1,3):15,(1,8):17,
          (2,3):13,(2,4):14,(2,5):20,(2,8):21,
          (3,4):11,(3,5):21,(3,6):17,(3,7):9,(3,8):9,
          (4,5):11,(4,6):10,(4,7):8,(4,8):20,
          (5,6):15,(5,7):18,(6,7):9,(7,8):13 }
D = [[INF]*N for _ in range(N)]
for (a,b),v in brut.items(): D[a-1][b-1] = D[b-1][a-1] = v
for i in range(N): D[i][i] = 0

def cout(t):
    return sum(D[t[i]][t[(i+1) % N]] for i in range(N))

def fmt(t): return "-".join(str(v+1) for v in t+[t[0]])

def voisins_2opt(t):
    for i in range(1, N-1):
        for j in range(i+1, N):
            if i == 1 and j == N-1: continue   # inversion totale = même circuit parcouru à l'envers
            yield (i, j), t[:i] + t[i:j+1][::-1] + t[j+1:]

# ---------- 1) Tabou ----------
def tabou(init, taille=3, max_iter=5):
    s, best = init[:], init[:]; liste = [tuple(s)]; trace = []
    for k in range(1, max_iter+1):
        cand = [(cout(y), m, y) for m, y in voisins_2opt(s) if tuple(y) not in liste]
        c, m, s = min(cand, key=lambda z: z[0])
        liste.append(tuple(s)); liste = liste[-taille:]
        if c < cout(best): best = s[:]
        trace.append((k, m, fmt(s), c, cout(best)))
    return best, trace

# ---------- 2) Recuit simulé ----------
def recuit(init, T0=20.0, alpha=0.5, paliers=5, K=10, graine=1):
    random.seed(graine)
    s, best, T = init[:], init[:], T0; trace = []
    for p in range(1, paliers+1):
        acc = 0
        for _ in range(K):
            i, j = sorted(random.sample(range(1, N), 2))
            y = s[:i] + s[i:j+1][::-1] + s[j+1:]
            d = cout(y) - cout(s)
            if d <= 0 or random.random() < math.exp(-d/T):
                s = y; acc += 1
                if cout(s) < cout(best): best = s[:]
        trace.append((p, T, acc, fmt(s), cout(s), cout(best)))
        T *= alpha
    return best, trace

# ---------- 3) Génétique ----------
def ox(p1, p2):
    a, b = sorted(random.sample(range(N), 2))
    enfant = [None]*N; enfant[a:b+1] = p1[a:b+1]
    reste = [v for v in p2 if v not in enfant]
    for i in range(N):
        if enfant[i] is None: enfant[i] = reste.pop(0)
    return enfant

def genetique(taille_pop=30, generations=50, pm=0.2, graine=1):
    random.seed(graine)
    pop = [random.sample(range(N), N) for _ in range(taille_pop)]
    trace = []
    for g in range(generations+1):
        pop.sort(key=cout)
        trace.append((g, fmt(pop[0]), cout(pop[0]), sum(map(cout, pop))/len(pop)))
        elite = pop[:2]; enfants = []
        while len(enfants) < taille_pop-2:
            p1 = min(random.sample(pop, 3), key=cout)
            p2 = min(random.sample(pop, 3), key=cout)
            e = ox(p1, p2)
            if random.random() < pm:
                i, j = random.sample(range(N), 2); e[i], e[j] = e[j], e[i]
            enfants.append(e)
        pop = elite + enfants
    return pop[0], trace

def optimum():
    return min(([0]+list(p) for p in itertools.permutations(range(1, N))), key=cout)

if __name__ == "__main__":
    init = list(range(N)); print("init", fmt(init), cout(init))
    b, tr = tabou(init)
    for r in tr: print(r)
    print("TABOU", fmt(b), cout(b))
    b, tr = recuit(init)
    for r in tr: print(r)
    print("RECUIT", fmt(b), cout(b))
    b, tr = genetique()
    for r in tr[::10]: print(r)
    print("GA", fmt(b), cout(b))
    o = optimum(); print("OPT", fmt(o), cout(o))
