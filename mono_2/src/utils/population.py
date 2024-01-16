import copy
import random

from tqdm import tqdm
from decouple import config
from utils.verifier import verifier
from movements.allocate import allocate
from heuristics.greedy import generate_greedy_solution

INDIVIDUALS_PER_POPULATION = int(config('INDIVIDUALS_PER_POPULATION'))
# INDIVIDUALS_PER_POPULATION = 5

def generate_first_population(original_solution, greedy=False, percentage=0.07):
    print(f"\n[INFO] Generating first population with {INDIVIDUALS_PER_POPULATION} individuals")

    population = []
    for i in tqdm(range(INDIVIDUALS_PER_POPULATION)):
        individual = copy.deepcopy(original_solution)
        allocated = False

        if greedy:
            population.append(generate_greedy_solution(individual, percentage=percentage, ordered_meetings=random.shuffle(individual['meetings'].copy())))
        else:
            meetings_left = [x + 1 for x in range(len(individual['meetings']))]
            random.shuffle(meetings_left)
            while meetings_left:
                try:
                    verifier(individual, verbose=False)
                except Exception as e:
                    print(e)
                    if allocated:
                        print(f"[ERROR] Error while allocating meeting {meeting_id} in classroom {classroom_index + 1}")
                    exit()
                meeting_id = meetings_left.pop()

                classroom_index = random.randrange(0, len(individual['classrooms']))
                allocated = False
                for j in range(len(individual['classrooms'])):
                    allocated = allocate(individual, meeting_id, classroom_index + 1)

                    if allocated:
                        break
                    else:
                        if classroom_index == len(individual['classrooms']) - 1:
                            classroom_index = 0
                        else:
                            classroom_index += 1
            
            population.append(individual)
        
    return population