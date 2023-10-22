import copy
import random
from decouple import config
from tqdm import tqdm

from movements.allocate import allocate
from movements.deallocate import deallocate
from movements.shift import shift
from movements.swap import swap

GENERATIONS = int(config('GENERATIONS'))
CHANCE_OF_MUTATION = float(config('CHANCE_OF_MUTATION'))
INDIVIDUALS_PER_POPULATION = int(config('INDIVIDUALS_PER_POPULATION'))

ALLOCATE = 0
DEALLOCATE = 1
SHIFT = 2
SWAP_OR_REPLACE = 3

def nsgaII(population, original_solution):
    print("[INFO] NSGA-II")

    if len(population) % 2 != 0:
        print(f"[INFO] Population size is an odd number ({len(population)}), removing last individual")
        population.pop()

    print(f"\n[INFO] Generating {GENERATIONS} generations")
    for i in tqdm(range(GENERATIONS)):
        new_population = crossover(population, original_solution)
        sorted_fronts = nondominated_sort(new_population)
        # print(sorted_fronts)
        next_generation = []
        while len(next_generation) < INDIVIDUALS_PER_POPULATION:
            for front in sorted_fronts:
                for solution_index in front:
                    if len(next_generation) == INDIVIDUALS_PER_POPULATION:
                        break
                    next_generation.append(new_population[solution_index])

        population = next_generation

    return population, nondominated_sort(population), new_population, sorted_fronts

def crossover(parents, original_solution):
    random.shuffle(parents)
    for i in range(0, len(parents), 2):
        parent_1 = parents[i]
        parent_2 = parents[i + 1]
        child_1 = copy.deepcopy(original_solution)
        child_2 = copy.deepcopy(original_solution)

        meetings_left = [x + 1 for x in range(len(parent_1['meetings']))]

        while meetings_left:
            meeting_id = meetings_left.pop(0)

            if random.random() < 0.5:
                if parent_1['meetings'][meeting_id - 1].classroom_id:
                    allocate(child_1, meeting_id, parent_1['meetings'][meeting_id - 1].classroom_id)
                if parent_2['meetings'][meeting_id - 1].classroom_id:
                    allocate(child_2, meeting_id, parent_2['meetings'][meeting_id - 1].classroom_id)
            else:
                if parent_2['meetings'][meeting_id - 1].classroom_id:
                    allocate(child_1, meeting_id, parent_2['meetings'][meeting_id - 1].classroom_id)
                if parent_1['meetings'][meeting_id - 1].classroom_id:
                    allocate(child_2, meeting_id, parent_1['meetings'][meeting_id - 1].classroom_id)

        if random.random() < CHANCE_OF_MUTATION:
            mutation(child_1)
        if random.random() < CHANCE_OF_MUTATION:
            mutation(child_2)
        
        parents.append(child_1)
        parents.append(child_2)

    return parents

def mutation(solution):
    mutation_happened = False
    movements = [ALLOCATE, DEALLOCATE, SHIFT, SWAP_OR_REPLACE]

    while not mutation_happened and movements:
        random.shuffle(movements)
        movement = movements.pop()

        if movement == ALLOCATE:
            mutation_happened = mutation_allocate(solution)
        elif movement == DEALLOCATE:
            mutation_happened = mutation_deallocate(solution)
        elif movement == SHIFT:
            mutation_happened = mutation_shift(solution)
        else:
            mutation_happened = mutation_swap_or_replace(solution)

def mutation_allocate(solution):
    meeting_index = random.randrange(0, len(solution['meetings']))
    for i in range(len(solution['meetings'])):
        if not solution['meetings'][meeting_index].classroom_id:
            classroom_index = random.randrange(0, len(solution['classrooms']))

            for j in range(len(solution['classrooms'])):
                allocated = allocate(solution, meeting_index + 1, classroom_index + 1)

                if allocated:
                    return True
                
                if classroom_index == len(solution['classrooms']) - 1:
                    classroom_index = 0
                else:
                    classroom_index += 1

        if meeting_index == len(solution['meetings']) - 1:
            meeting_index = 0
        else:
            meeting_index += 1

    return False

def mutation_deallocate(solution):
    meeting_index = random.randrange(0, len(solution['meetings']))
    for i in range(len(solution['meetings'])):
        if solution['meetings'][meeting_index].classroom_id:
            deallocate(solution, meeting_index + 1)
            return True

        if meeting_index == len(solution['meetings']) - 1:
            meeting_index = 0
        else:
            meeting_index += 1

    return False

def mutation_shift(solution):
    meeting_index = random.randrange(0, len(solution['meetings']))
    for i in range(len(solution['meetings'])):
        meeting = solution['meetings'][meeting_index]
        if meeting.classroom_id:
            classroom_index = random.randrange(0, len(solution['classrooms']))

            for j in range(len(solution['classrooms'])):
                shifted = False
                if solution["classrooms"][classroom_index].check_availability(meeting.schedules, meeting.day_name()):
                    shifted = shift(solution, meeting_index + 1, classroom_index + 1)

                if shifted:
                    return True
                
                if classroom_index == len(solution['classrooms']) - 1:
                    classroom_index = 0
                else:
                    classroom_index += 1

        if meeting_index == len(solution['meetings']) - 1:
            meeting_index = 0
        else:
            meeting_index += 1

    return False

def mutation_swap_or_replace(solution):
    meeting_index_1 = random.randrange(0, len(solution['meetings']))

    for i in range(len(solution['meetings'])):
        meeting_index_2 = random.randrange(0, len(solution['meetings']))

        for j in range(len(solution['meetings'])):
            if (meeting_index_1 == meeting_index_2) or (solution['meetings'][meeting_index_1].schedules != solution['meetings'][meeting_index_2].schedules):
                if meeting_index_2 == len(solution['meetings']) - 1:
                    meeting_index_2 = 0
                else:
                    meeting_index_2 += 1
                continue

            if solution['meetings'][meeting_index_1].classroom_id and solution['meetings'][meeting_index_2].classroom_id:
                swapped = swap(solution, meeting_index_1 + 1, meeting_index_2 + 1)
                if swapped:
                    return True
            elif solution['meetings'][meeting_index_1].classroom_id and not solution['meetings'][meeting_index_2].classroom_id:
                classroom_id = solution['meetings'][meeting_index_1].classroom_id
                deallocate(solution, meeting_index_1 + 1)
                allocated = allocate(solution, meeting_index_2 + 1, classroom_id)
                if allocated:
                    return True
            elif not solution['meetings'][meeting_index_1].classroom_id and solution['meetings'][meeting_index_2].classroom_id:
                classroom_id = solution['meetings'][meeting_index_2].classroom_id
                deallocate(solution, meeting_index_2 + 1)
                allocated = allocate(solution, meeting_index_1 + 1, classroom_id)
                if allocated:
                    return True
            else:
                pass

            if meeting_index_2 == len(solution['meetings']) - 1:
                meeting_index_2 = 0
            else:
                meeting_index_2 += 1

    return False

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