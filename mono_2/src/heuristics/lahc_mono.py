import copy
import math
from datetime import datetime, timedelta
import random
from time import sleep
from heuristics.greedy import generate_greedy_solutoin
from heuristics.learning_automaton import automaton_F1, automaton_F2
from movements.allocate import allocate
from movements.deallocate import deallocate
from movements.shift import shift
from movements.swap import swap
from utils.cost import solution_cost
from utils.population import generate_first_population
from utils.verifier import verifier

ALLOCATE = 0
DEALLOCATE = 1
SHIFT = 2
SWAP_OR_REPLACE = 3

ALPHA = 10**(-2)

def lahc_mono(original_solution, list_size, max_time):
    print("[INFO] LAHC mono objective")
    print(f"[INFO] Started at: {datetime.now()}")

    # solution = copy.deepcopy(generate_first_population(original_solution)[0])
    solution = copy.deepcopy(generate_greedy_solutoin(original_solution))
    verifier(solution)

    list = [solution_cost(solution['objectives']) for _ in range(list_size)]
    best_solution = copy.deepcopy(solution)
    first_cost = solution_cost(solution['objectives'])
    print(f"[INFO] LAHC mono objective: {first_cost}")

    start_time = datetime.now()
    probabilities = [0.25, 0.25, 0.25, 0.25]

    list_index = 0
    max_time_with_no_improvement = 20
    last_improvement = datetime.now()

    graphics = []
    graphics.append({
        'value': first_cost,
        'time': 0
    })
    
    while(datetime.now() - start_time < timedelta(seconds=max_time)):
        objectives = copy.deepcopy(solution['objectives'])

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
            raise Exception('Invalid move at LAHC-MONO')
        
        if move_response["move_done"]:
            # print(f'----------------> {solution_cost(solution["objectives"])}')
            new_cost = solution_cost(solution["objectives"])
            if new_cost <= list[list_index]:
                list[list_index] = new_cost

                automaton_F1(probabilities, ALPHA, 1, move)
                for i in range(len(probabilities)):
                    if (i != move):
                        automaton_F2(probabilities, ALPHA, 1, i)
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
                    raise Exception('Invalid move at LAHC-MONO (undo move)')
                
                if not objectives.compare(solution['objectives'], move, move_response, solution['meetings']):
                    raise Exception('Invalid undo move at LAHC-MONO (objectives)')

                automaton_F1(probabilities, ALPHA, 0, move)

                for i in range(len(probabilities)):
                    if (i != move):
                        automaton_F2(probabilities, ALPHA, 0, i)
            
            if new_cost < solution_cost(best_solution["objectives"]):
                # print(f"[INFO] LAHC mono objective: {new_cost}")
                graphics.append({
                    'value': new_cost,
                    'time': float(str((datetime.now() - start_time).seconds) + '.' + str((datetime.now() - start_time).microseconds))
                })
                best_solution = copy.deepcopy(solution)
                last_improvement = datetime.now()

        if list_index == len(list) - 1:
            list_index = 0
        else:
            list_index += 1

        verifier(solution, verbose=False)

        if datetime.now() - last_improvement > timedelta(seconds=max_time_with_no_improvement):
            max_time_with_no_improvement += 10
            probabilities = [0.25, 0.25, 0.25, 0.25]
            # solution['objectives'].print()
            # print(f'------> {solution_cost(solution["objectives"])}')
            perturbation(solution)
            # print(f'------> {solution_cost(solution["objectives"])}')
            print()
            # solution['objectives'].print()

    print(f"[INFO] Finished at: {datetime.now()}")
    print(f"[INFO] LAHC mono objective: {first_cost} -> {solution_cost(best_solution['objectives'])}")

    graphics.append({
        'value': solution_cost(best_solution['objectives']),
        'time': max_time
    })

    return best_solution, graphics

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
        raise Exception('Invalid move at LAHC-MONO (undo swap or replace)')
    
def perturbation(solution):
    print("[INFO] LAHC mono objective: Perturbation")

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
