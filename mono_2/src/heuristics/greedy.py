import copy
import random

from utils.cost import solution_cost
from movements.allocate import allocate
from movements.deallocate import deallocate

def generate_greedy_solution(original_solution, best_solution=None, percentage=0.07, ordered_meetings=None):
    # print("[INFO] Generating greedy solution")

    solution = copy.deepcopy(original_solution)

    copy_meetings = sorted(solution['meetings'], key=lambda meeting: meeting.demand, reverse=True) if not ordered_meetings else ordered_meetings
    copy_classrooms = sorted(solution['classrooms'], key=lambda classroom: classroom.capacity, reverse=True)

    if best_solution:
        for i in range (len(best_solution['meetings'])):
            probability = random.random()

            if probability <= percentage and best_solution['meetings'][i].classroom_id:
                allocate(solution, best_solution['meetings'][i].id, best_solution['meetings'][i].classroom_id)
        
        initial_cost = solution_cost(solution['objectives'])
    # return solution

    for i in range(len(copy_meetings)):
        allocated = False
        classroom_idx = None
        actual_cost = solution_cost(solution['objectives'])

        meeting_id = copy_meetings[i].id
        if solution['meetings'][meeting_id - 1].classroom_id:
            continue

        probability = random.random()

        if probability >= percentage:
            for j in range(len(copy_classrooms)):
                allocated = allocate(solution, copy_meetings[i].id, copy_classrooms[j].id)

                if allocated:
                    cost = solution_cost(solution['objectives'])
                    if cost < actual_cost:
                        actual_cost = cost
                        classroom_idx = j
                    deallocate(solution, copy_meetings[i].id)

            if classroom_idx or classroom_idx == 0:
                allocate(solution, copy_meetings[i].id, copy_classrooms[classroom_idx].id)
        else:
            # for j in range(len(copy_classrooms) - 1, -1, -1):
            for j in range(len(copy_classrooms)):
                allocated = allocate(solution, copy_meetings[i].id, copy_classrooms[j].id)

                if allocated:
                    break

    return solution