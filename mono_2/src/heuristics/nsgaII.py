import copy
import random

from tqdm import tqdm
from decouple import config
from movements.swap import swap
from movements.shift import shift
from movements.allocate import allocate
from utils.pareto import nondominated_sort
from movements.deallocate import deallocate

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

    print(f"-------------------------> {len(sorted_fronts)}")
    print(f"-------------------------> {len(sorted_fronts[0])}")
    print(f"-------------------------> {len(new_population)}")

    return population

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
            if (meeting_index_1 == meeting_index_2) or (solution['meetings'][meeting_index_1].schedules != solution['meetings'][meeting_index_2].schedules) or (solution['meetings'][meeting_index_1].day_of_week != solution['meetings'][meeting_index_2].day_of_week):
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