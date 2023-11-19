import copy
from datetime import datetime, timedelta
import random
from time import sleep
from heuristics.learning_automaton import automaton_F1, automaton_F2
from movements.allocate import allocate
from movements.deallocate import deallocate
from movements.shift import shift
from movements.swap import swap
from utils.population import generate_first_population

ALLOCATE = 0
DEALOCATE = 1
SHIFT = 2
SWAP_OR_REPLACE = 3

IDLENESS_WEIGHT = 1
DEALLOCATED_WEIGHT = 1
STANDING_WEIGHT = 1

ALPHA = 10**(-2)

def lahc_mono(original_solution, list_size, max_time):
    print("[INFO] LAHC mono objective")

    solution = copy.deepcopy(generate_first_population(original_solution)[0])

    list = [solution_cost(solution['objectives']) for _ in range(list_size)]
    best_solution = copy.deepcopy(solution)
    first_cost = solution_cost(solution['objectives'])
    print(f"[INFO] LAHC mono objective: {first_cost}")

    start_time = datetime.now()
    probabilities = [0.25, 0.25, 0.25, 0.25]

    list_index = 0
    
    while(datetime.now() - start_time < timedelta(seconds=max_time)):
        move_selector = random.random()
        move = None

        if move_selector < sum(probabilities[0:1]):
            move = ALLOCATE
        elif move_selector < sum(probabilities[0:2]):
            move = DEALOCATE
        elif move_selector < sum(probabilities[0:3]):
            move = SHIFT
        else:
            move = SWAP_OR_REPLACE

        if move == ALLOCATE:
            move_response = draw_allocate(solution)
        elif move == DEALOCATE:
            move_response = draw_deallocate(solution)
        elif move == SHIFT:
            move_response = draw_shift(solution)
        elif move == SWAP_OR_REPLACE:
            move_response = draw_swap_or_replace(solution)
        else:
            raise Exception('Invalid move at LAHC-MONO')
        
        if move_response["move_done"]:
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
                elif move == DEALOCATE:
                    allocate(solution, move_response["meeting_1"], move_response["classroom_1"])
                elif move == SHIFT:
                    shift(solution, move_response["meeting_1"], move_response["classroom_1"])
                elif move == SWAP_OR_REPLACE:
                    undo_swap_or_replace(solution, move_response)
                else:
                    raise Exception('Invalid move at LAHC-MONO (undo move)')
                
                automaton_F1(probabilities, ALPHA, 0, move)

                for i in range(len(probabilities)):
                    if (i != move):
                        automaton_F2(probabilities, ALPHA, 0, i)
            
            if new_cost < solution_cost(best_solution["objectives"]):
                print(f"[INFO] LAHC mono objective: {new_cost}")
                best_solution = copy.deepcopy(solution)

        if list_index == len(list) - 1:
            list_index = 0
        else:
            list_index += 1

    print(f"[INFO] LAHC mono objective: {first_cost} -> {solution_cost(best_solution['objectives'])}")

    return best_solution

def solution_cost(objectives):
    return (IDLENESS_WEIGHT * objectives.idleness) + (DEALLOCATED_WEIGHT * objectives.deallocated) + (STANDING_WEIGHT * objectives.standing)

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
            classroom_index = random.randrange(0, len(solution['classrooms']))

            for j in range(len(solution['classrooms'])):
                shifted = False
                if solution["classrooms"][classroom_index].check_availability(meeting.schedules, meeting.day_name()):
                    shifted = shift(solution, meeting_index + 1, classroom_index + 1)

                if shifted:
                    return {
                        "move_done": True,
                        "meeting_1": meeting_index + 1,
                        "classroom_1": meeting.classroom_id,
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
            if (meeting_index_1 == meeting_index_2) or (solution['meetings'][meeting_index_1].schedules != solution['meetings'][meeting_index_2].schedules):
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