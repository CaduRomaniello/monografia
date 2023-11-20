import numpy
from mip import *

def allocation_cost(meeting, classrooms):
    cost = []
    for m in meeting:
        cost.append([])
        for c in classrooms:
            alocation_cost = 0
            alocation_cost += (c.capacity - m.demand if c.capacity - m.demand > 0 else 0) if c.capacity - m.demand > c.capacity / 2 else 0
            alocation_cost += m.demand - c.capacity if m.demand - c.capacity > 0 else 0
            cost[-1].append(alocation_cost)
        cost[-1].append(m.demand)
    return cost

def isReservated(classroom, schedule, day_name):
    return classroom.days[day_name][schedule]['is_reservation']

def mipPy(solution, instance):
    print("[INFO] Starting MIP")

    grouped_schedules = []

    for i in range(len(solution['meetings'])):
        aux = []
        for j in range(len(solution['meetings'][i].schedules) - 1):
            for k in range(j + 1, len(solution['meetings'][i].schedules)):
                aux.append([solution['meetings'][i].schedules[j], solution['meetings'][i].schedules[k]])
        grouped_schedules.append(aux)

    cost = allocation_cost(solution['meetings'], solution['classrooms'])

    m = Model()
    m.verbose = 0

    E = len(solution['meetings'])
    S = len(solution['classrooms']) + 1
    H = len(instance['schedules'])

    ehs = []
    for e in range(E):
        ehs.append([])
        for s in range(S):
            ehs[e].append([])
            for h in range(H):
                reservated = isReservated(solution['classrooms'][s], h, solution['meetings'][e].day_name()) if s < S - 1 else False
                if ((h + 1 in solution['meetings'][e].schedules) and not reservated):
                    ehs[e][s].append(m.add_var(var_type=BINARY, name=f"x({e},{s},{h})"))
                else:
                    ehs[e][s].append(0)

    m.objective = xsum(cost[e][s] * ehs[e][s][solution['meetings'][e].schedules[0] - 1]  for e in range(E) for s in range(S))

    for e in range(E):
        for h in solution['meetings'][e].schedules:
            m += xsum(ehs[e][s][h - 1] for s in range(S)) == 1

    for s in range(S - 1):
        for h in range(H):
            m += xsum(ehs[e][s][h] for e in range(E)) <= 1

    for e in range(E):
        for s in range(S):
            for h in range(len(grouped_schedules[e])):
                restricao = ehs[e][s][grouped_schedules[e][h][0] - 1] == ehs[e][s][grouped_schedules[e][h][1] - 1]
                if not isinstance(restricao, bool):
                    m += ehs[e][s][grouped_schedules[e][h][0] - 1] == ehs[e][s][grouped_schedules[e][h][1] - 1]

    m.optimize()  
    m.write("mip_lb.lp")

    allocations = []

    for e in range(E):
        aux = {
            'meeting_id': solution['meetings'][e].id,
            'classroom_id': 0
        }
        for s in range(S - 1):
            if (isinstance(ehs[e][s][solution['meetings'][e].schedules[0] - 1], Var) and ehs[e][s][solution['meetings'][e].schedules[0] - 1].x > 0.5):
            # if (ehs[e][s][solution['meetings'][e].schedules[0] - 1].x > 0.5):
                aux['classroom_id'] = s + 1
        allocations.append(aux)

    print("[INFO] MIP finished")

    return m.objective_value, allocations