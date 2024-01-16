def dominates(objectives_1, objectives_2):
    if (objectives_1.deallocated < objectives_2.deallocated) and (objectives_1.idleness < objectives_2.idleness) and (objectives_1.standing < objectives_2.standing):
        return True
    else:
        return False

def nondominated_sort(solutions):
    fronts = []
    domination_count = [0] * len(solutions)
    dominated_solutions = [[] for _ in range(len(solutions))]

    for i in range(len(solutions)):
        for j in range(i + 1, len(solutions)):
            if dominates(solutions[i]["objectives"], solutions[j]["objectives"]):
                dominated_solutions[i].append(j)
                domination_count[j] += 1
            elif dominates(solutions[j]["objectives"], solutions[i]["objectives"]):
                dominated_solutions[j].append(i)
                domination_count[i] += 1

    front = []
    for i in range(len(solutions)):
        if domination_count[i] == 0:
            front.append(i)

    while front:
        next_front = []
        for i in front:
            for j in dominated_solutions[i]:
                domination_count[j] -= 1
                if domination_count[j] == 0:
                    next_front.append(j)
        fronts.append(front)
        front = next_front

    return fronts

    # sorted_solutions = []
    # for front in fronts:
    #     sorted_solutions.extend([solutions[i] for i in front])

    # return sorted_solutions