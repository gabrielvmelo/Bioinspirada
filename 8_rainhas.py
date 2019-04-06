from random import randint
from random import shuffle
import math

def new_fenotipo(perm=False):
    if not perm:
        x = [randint(0, 7) for p in range(0, 7)]
    else:
        x = []
        i = 0
        while len(x) < 8:
            n = randint(0, 7)
            if n not in x:
                x.append(n)
    return x

def bin_fenotipo(fen):
    bin_fen = []
    
    for i in fen:
        binary = bin(i)[2:]
        if len(binary) < 3:
            for j in range(3-len(binary)):
                binary = "0{}".format(binary)
        for b in binary:
            bin_fen.append(b)

    return bin_fen


def fitness(gen):
    colisions = 0

    for i in gen:
        colisions += gen.count(i) - 1
    
    for i in range(len(gen)):
        if i + 1 < len(gen):
            right = gen[i+1:]
            aux = 1
            for j in right:
                if j == int(gen[i]) + aux:
                    #print("i: {}, x: {}, j: {}".format(i, gen[i], j))
                    colisions += 1
                if j == int(gen[i]) - aux:
                    colisions += 1
                aux += 1
        if i > 0:
            left = gen[:i]
            left.reverse()
            aux = 1

            for j in left:
                if j == int(gen[i]) + aux:
                    #print("i: {}, x: {}, j: {}".format(i, gen[i], j))
                    colisions += 1
                if j == int(gen[i]) - aux:
                    colisions += 1
                aux += 1

        
    
    return 1/(colisions + 1)


def bin_to_int(b):
    r = 0
    p = len(b) - 1
    for i in b:
        #print(i)
        if i == "1":
            r += math.pow(2, p)
        p -= 1
    #print(p)
    return int(r)

def fen_to_int(fen_bin):
    i = 0
    locus = []
    while i < len(fen_bin):
         #print(fen_bin[i:i+3])
         locus.append(bin_to_int(fen_bin[i:i+3]))
         i += 3

    return locus


def generate_parents(n_parents=100, perm=False, binary_rep=True):
    parents = []

    while len(parents) < 100:
        fenotipo = new_fenotipo(perm)
        if binary_rep:
            bin_representation = bin_fenotipo(fenotipo)
            if bin_representation not in parents:
                parents.append(bin_representation)
        else:
            if fenotipo not in parents:
                parents.append(fenotipo)
    return parents

def init_population(n_parents=100, perm=False, binary_rep=True):
    population = []
    
    parents = generate_parents(n_parents=n_parents, perm=perm, binary_rep=binary_rep)
    
    for p in parents:
        if binary_rep:
            population.append((p, fitness(fen_to_int(p)), "p"))
        else:
            population.append((p, fitness(p), "p"))
    return population

def mutation(p, mode="all", prob=10, binary_rep=True):
    gen = p[0]
    if binary_rep:
        gen = fen_to_int(gen)
    #print(gen)

    if mode == "all":
        for i in range(len(gen)):
            r = randint(1, 100)
            if r <= prob:
                s = randint(0, 7)
                aux = gen[s]
                gen[s] = gen[i]
                gen[i] = aux

    elif mode == "one":
        r = randint(1, 100)
        if r <= prob:
            s = randint(0, 7)
            z = randint(0, 7)
            aux = gen[s]
            gen[s] = gen[z]
            gen[z] = aux

    elif mode == "disturb":
        r = randint(0, 7)
        s = randint(r, 7)
        if r < s:
            temp = gen[r:s]
            shuffle(temp)
            gen[r:s] = temp

    if binary_rep:
        response = (bin_fenotipo(gen), fitness(gen), "m")
    else:
        response = (gen, fitness(gen), "m")             

    return response


def select_prob(l, n):
    for i in range(len(l)):
        if n < l[i]:
            return i
    return -1

def parent_selection(population, n_parents=2, mode="elitismo", sub_set=5):
    parents = []
    population_size = len(population)

    if mode == "elitismo":
        population.sort(reverse=True, key=lambda x: x[1])
        parents = population[:n_parents]
    
    elif mode == "random_elitismo":
        sub_sample = []
        for i in range(sub_set):
            r = randint(0, population_size-1)
            sub_sample.append(population[r])
        sub_sample.sort(reverse=True, key=lambda x: x[1])
        parents = sub_sample[:n_parents]
    
    elif mode == "random":
        for i in range(n_parents):
            r = randint(0, population_size-1)
            parents.append(population[r])

    elif mode == "roleta":
        sub_sample = []
        for i in range(sub_set):
            r = randint(0, population_size-1)
            sub_sample.append(population[r])
        sub_sample.sort(key=lambda x: x[1])
        fit_total = 0
        for i in range(n_parents):
            for p in sub_sample:
                fit_total += p[1]
                fit_total *= 100
            prob = []
            for p in sub_sample:
                prob.append((p[1]*100)/fit_total)
            r = randint(0, 99)
            select_parent = select_prob(prob, r)
            parents.append(sub_sample[select_parent])
            sub_sample.remove(sub_sample[select_parent])       

    return parents

def crossover(parent1, parent2, binary_rep=True, mode="one_cut", cut=4):
    if binary_rep:
        parent1 = fen_to_int(parent1[0])
        parent2 = fen_to_int(parent2[0])
    
    child1 = []
    child2 = []
    
    if mode == "one_cut":
        child1 = parent1[:cut]
        child2 = parent2[:cut]
        l1 = parent2[cut:] + parent2[:cut]
        l2 = parent1[cut:] + parent1[:cut]

        for l in l1:
            if l not in child1:
                child1.append(l)
        for l in l2:
            if l not in child2:
                child2.append(l)
    
    elif mode == "ordem1":
        for i in range(len(parent1)):
            child1.append(-1)
            child2.append(-1)
        r = randint(0, 7)
        print(r)
        child1[r:r+cut] = parent1[r:r+cut]
        child2[r:r+cut] = parent2[r:r+cut]
        l1 = parent2[r+cut:] + parent2[:r+cut]
        l2 = parent1[r+cut:] + parent1[:r+cut]
        if r + cut > 8:
            aux = 0
        else:
            aux = (r + cut ) % 8

        for i in l1:
            if i not in child1:
                child1[aux] = i
                aux = (aux+1)%8

        if r + cut > 8:
            aux = 0
        else:
            aux = (r + cut) % 8


        for i in l2:
            if i not in child2:
                child2[aux] = i
                aux = (aux+1)%8

    if binary_rep:
        response = ((bin_fenotipo(child1), fitness(child1), "c"), (bin_fenotipo(child2), fitness(child2), "c"))
    else:
        response = ((child1, fitness(child1), "c"), (child2, fitness(child2), "c"))
    
    return response


def main():
    population = init_population(perm=True,binary_rep=False)

    for i in range(10000):
        population.sort(reverse=True, key=lambda x: x[2])
        parents = parent_selection(population)
        childs = crossover(parents[0][0], parents[1][0], binary_rep=False)
        for child in childs:
            if child[1] == 1:
                print("Iteração {} fitness 1".format(i))
                print(child)
                return
            child = mutation(child,binary_rep=False)
            if child[1] == 1:
                print("Iteração {} fitness 1".format(i))
                print(child)
                return
        population[len(population)-len(childs):] = childs
        
            


if __name__ == "__main__":
    main()