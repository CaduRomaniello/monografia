import copy
from utils.cost import solution_cost

from movements.allocate import allocate
from movements.deallocate import deallocate

def generate_greedy_solutoin(original_solution):
    print("[INFO] Generating greedy solution")

    solution = copy.deepcopy(original_solution)
    initial_cost = solution_cost(solution['objectives'])

    copy_meetings = sorted(solution['meetings'], key=lambda meeting: meeting.demand, reverse=True)
    copy_classrooms = sorted(solution['classrooms'], key=lambda classroom: classroom.capacity, reverse=True)

    for i in range(len(copy_meetings)):
        allocated = False
        lowest_cost = initial_cost
        classroom_idx = None
        for j in range(len(copy_classrooms)):
            allocated = allocate(solution, copy_meetings[i].id, copy_classrooms[j].id)

            if allocated:
                cost = solution_cost(solution['objectives'])
                if cost < lowest_cost:
                    lowest_cost = cost
                    classroom_idx = j
                deallocate(solution, copy_meetings[i].id)

        if classroom_idx:
            allocate(solution, copy_meetings[i].id, copy_classrooms[classroom_idx].id)
        else:
            for j in range(len(copy_classrooms)):
                allocated = allocate(solution, copy_meetings[i].id, copy_classrooms[j].id)

                if allocated:
                    break

    return solution