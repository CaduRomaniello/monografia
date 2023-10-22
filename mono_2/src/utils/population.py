import copy
import random
from decouple import config
from tqdm import tqdm

from movements.allocate import allocate
from utils.verifier import verifier

INDIVIDUALS_PER_POPULATION = int(config('INDIVIDUALS_PER_POPULATION'))

def generate_first_population(original_solution):
    print(f"\n[INFO] Generating first population with {INDIVIDUALS_PER_POPULATION} individuals")

    population = []
    for i in tqdm(range(INDIVIDUALS_PER_POPULATION)):
        individual = copy.deepcopy(original_solution)
        allocated = False

        meetings_left = [x + 1 for x in range(len(individual['meetings']))]
        random.shuffle(meetings_left)
        while meetings_left:
            try:
                verifier(individual)
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