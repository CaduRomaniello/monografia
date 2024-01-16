import copy
import math
import random

from time import sleep
from movements.swap import swap
from movements.shift import shift
from utils.verifier import verifier
from utils.cost import solution_cost
from movements.allocate import allocate
from datetime import datetime, timedelta
from movements.deallocate import deallocate
from heuristics.greedy import generate_greedy_solution
from utils.population import generate_first_population
from heuristics.learning_automaton import automaton_F1, automaton_F2

ALLOCATE = 0
DEALLOCATE = 1
SHIFT = 2
SWAP_OR_REPLACE = 3

ALPHA = 10**(-2)

def lahc_multi(original_solution, list_size, max_time):
    print("[INFO] LAHC multi objective")
    print(f"[INFO] Started at: {datetime.now()}")

    # solution = copy.deepcopy(generate_first_population(original_solution)[0])
    solution = copy.deepcopy(generate_greedy_solution(original_solution))
    verifier(solution)

    list = [copy.deepcopy(solution['objectives']) for _ in range(list_size)]
    pareto_front = [copy.deepcopy(solution)]
    # best_solution = copy.deepcopy(solution)

    start_time = datetime.now()
    probabilities = [0.25, 0.25, 0.25, 0.25]

    list_index = 0
    max_time_with_no_improvement = 45
    last_improvement = datetime.now()
    
    while(datetime.now() - start_time < timedelta(seconds=max_time)):
    # while(True):
        actual_objectives = copy.deepcopy(solution['objectives'])

        move_selector = random.random()
        move = None

        if move_selector < sum(probabilities[0:1]):
            move = ALLOCATE
        elif move_selector < sum(probabilities[0:2]):
            move = DEALLOCATE
        elif move_selector < sum(probabilities[0:3]):
            move = SHIFT
        else:
            move = SWAP_OR_REPLACE

        if move == ALLOCATE:
            move_response = draw_allocate(solution)
        elif move == DEALLOCATE:
            move_response = draw_deallocate(solution)
        elif move == SHIFT:
            move_response = draw_shift(solution)
        elif move == SWAP_OR_REPLACE:
            move_response = draw_swap_or_replace(solution)
        else:
            raise Exception('Invalid move at LAHC-MULTI')
        
        if move_response["move_done"]:
            if check_new_solution_acceptance(solution['objectives'], actual_objectives, list[list_index]):
                dominates, isDominatedBy = evaluate_new_solution_dominance(solution['objectives'], pareto_front)

                if len(isDominatedBy) == 0:
                    update_pareto_front(solution, dominates, pareto_front)

                list[list_index] = copy.deepcopy(solution['objectives'])
            else:
                if move == ALLOCATE:
                    deallocate(solution, move_response["meeting_1"])
                elif move == DEALLOCATE:
                    allocate(solution, move_response["meeting_1"], move_response["classroom_1"])
                elif move == SHIFT:
                    shift(solution, move_response["meeting_1"], move_response["classroom_1"])
                elif move == SWAP_OR_REPLACE:
                    undo_swap_or_replace(solution, move_response)
                else:
                    raise Exception('Invalid move at LAHC-MULTI (undo move)')
                
                if not actual_objectives.compare(solution['objectives'], move, move_response, solution['meetings']):
                    raise Exception('Invalid undo move at LAHC-MULTI (objectives)')

        if list_index == len(list) - 1:
            list_index = 0
        else:
            list_index += 1

        verifier(solution, verbose=False)

        # if datetime.now() - last_improvement > timedelta(seconds=max_time_with_no_improvement):
        #     max_time_with_no_improvement += 10
        #     probabilities = [0.25, 0.25, 0.25, 0.25]
        #     perturbation(solution)

    print(f"[INFO] Finished at: {datetime.now()}")

    return pareto_front

def draw_allocate(solution):
    meeting_index = random.randrange(0, len(solution['meetings']))
    for i in range(len(solution['meetings'])):
        if not solution['meetings'][meeting_index].classroom_id:
            classroom_index = random.randrange(0, len(solution['classrooms']))

            for j in range(len(solution['classrooms'])):
                allocated = allocate(solution, meeting_index + 1, classroom_index + 1)

                if allocated:
                    return {
                        "move_done": True,
                        "meeting_1": meeting_index + 1,
                        "classroom_1": classroom_index + 1,
                        "move_type": "allocate"
                    }
                
                if classroom_index == len(solution['classrooms']) - 1:
                    classroom_index = 0
                else:
                    classroom_index += 1

        if meeting_index == len(solution['meetings']) - 1:
            meeting_index = 0
        else:
            meeting_index += 1

    return {
        "move_done": False
    }

def draw_deallocate(solution):
    meeting_index = random.randrange(0, len(solution['meetings']))
    for i in range(len(solution['meetings'])):
        if solution['meetings'][meeting_index].classroom_id:
            classroom_id = solution['meetings'][meeting_index].classroom_id
            deallocate(solution, meeting_index + 1)
            return {
                "move_done": True,
                "meeting_1": meeting_index + 1,
                "classroom_1": classroom_id,
                "move_type": "deallocate"
            }

        if meeting_index == len(solution['meetings']) - 1:
            meeting_index = 0
        else:
            meeting_index += 1

    return {
        "move_done": False
    }

def draw_shift(solution):
    meeting_index = random.randrange(0, len(solution['meetings']))
    for i in range(len(solution['meetings'])):
        meeting = solution['meetings'][meeting_index]
        if meeting.classroom_id:
            classroom_id = meeting.classroom_id
            classroom_index = random.randrange(0, len(solution['classrooms']))

            for j in range(len(solution['classrooms'])):
                shifted = False
                if solution["classrooms"][classroom_index].check_availability(meeting.schedules, meeting.day_name()):
                    shifted = shift(solution, meeting_index + 1, classroom_index + 1)

                if shifted:
                    return {
                        "move_done": True,
                        "meeting_1": meeting_index + 1,
                        "classroom_1": classroom_id,
                        "classroom_2": classroom_index + 1,
                        "move_type": "shift"
                    }
                
                if classroom_index == len(solution['classrooms']) - 1:
                    classroom_index = 0
                else:
                    classroom_index += 1

        if meeting_index == len(solution['meetings']) - 1:
            meeting_index = 0
        else:
            meeting_index += 1

    return {
        "move_done": False
    }

def draw_swap_or_replace(solution):
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
                    return {
                        "move_done": True,
                        "meeting_1": meeting_index_1 + 1,
                        "meeting_2": meeting_index_2 + 1,
                        "move_type": "swap"
                    }
            elif solution['meetings'][meeting_index_1].classroom_id and not solution['meetings'][meeting_index_2].classroom_id:
                classroom_id = solution['meetings'][meeting_index_1].classroom_id
                deallocate(solution, meeting_index_1 + 1)
                allocated = allocate(solution, meeting_index_2 + 1, classroom_id)
                if allocated:
                    return {
                        "move_done": True,
                        "meeting_1": meeting_index_1 + 1,
                        "meeting_2": meeting_index_2 + 1,
                        "classroom_1": classroom_id,
                        "move_type": "replace_1"
                    }
            elif not solution['meetings'][meeting_index_1].classroom_id and solution['meetings'][meeting_index_2].classroom_id:
                classroom_id = solution['meetings'][meeting_index_2].classroom_id
                deallocate(solution, meeting_index_2 + 1)
                allocated = allocate(solution, meeting_index_1 + 1, classroom_id)
                if allocated:
                    return {
                        "move_done": True,
                        "meeting_1": meeting_index_1 + 1,
                        "meeting_2": meeting_index_2 + 1,
                        "classroom_1": classroom_id,
                        "move_type": "replace_2"
                    }
            else:
                pass

            if meeting_index_2 == len(solution['meetings']) - 1:
                meeting_index_2 = 0
            else:
                meeting_index_2 += 1

    return {
        "move_done": False
    }

def undo_swap_or_replace(solution, move_response):
    if move_response["move_type"] == "swap":
        swap(solution, move_response["meeting_1"], move_response["meeting_2"])
    elif move_response["move_type"] == "replace_1":
        deallocate(solution, move_response["meeting_2"])
        allocate(solution, move_response["meeting_1"], move_response["classroom_1"])
    elif move_response["move_type"] == "replace_2":
        deallocate(solution, move_response["meeting_1"])
        allocate(solution, move_response["meeting_2"], move_response["classroom_1"])
    else:
        raise Exception('Invalid move at LAHC-MULTI (undo swap or replace)')
    
def perturbation(solution):
    print("[INFO] LAHC multi objective: Perturbation")

    movements_count = 0
    while movements_count < 10:
        mutation_happened = False
        movements = [ALLOCATE, DEALLOCATE, SHIFT, SWAP_OR_REPLACE]

        while not mutation_happened and movements:
            random.shuffle(movements)
            movement = movements.pop()

            if movement == ALLOCATE:
                mutation_happened = perturbation_allocate(solution)
            elif movement == DEALLOCATE:
                mutation_happened = perturbation_deallocate(solution)
            elif movement == SHIFT:
                mutation_happened = perturbation_shift(solution)
            else:
                mutation_happened = perturbation_swap_or_replace(solution)

            if mutation_happened:
                movements_count += 1

def perturbation_allocate(solution):
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

def perturbation_deallocate(solution):
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

def perturbation_shift(solution):
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

def perturbation_swap_or_replace(solution):
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

def check_new_solution_acceptance(new_solution_objectives, actual_solution_objectives, list_solution_objectives):
    if new_solution_objectives.dominates(actual_solution_objectives):
        return True

    if new_solution_objectives.dominates(list_solution_objectives):
        return True

    return False

def evaluate_new_solution_dominance(new_solution_objectives, pareto_front):
    dominates = []
    isDominatedBy = []

    for i in range(len(pareto_front)):
        if new_solution_objectives.dominates(pareto_front[i]['objectives']):
            dominates.append(i)

        if pareto_front[i]['objectives'].dominates(new_solution_objectives):
            isDominatedBy.append(i)

    return dominates, isDominatedBy

def update_pareto_front(new_solution, dominates, pareto_front):
    for i in range(len(dominates) - 1, -1, -1):
        pareto_front.pop(dominates[i])
    
    pareto_front.append(copy.deepcopy(new_solution))
