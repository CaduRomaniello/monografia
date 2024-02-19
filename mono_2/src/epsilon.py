import os
import copy
import json
import plotly.graph_objects as go
import numpy

from mip import *
# from heuristics.mip import mipPy
from utils.pareto import dominates
from movements.allocate import allocate
from classes.objectives import Objectives
from pymoo.indicators.hv import Hypervolume
from utils.instance import parse_data, read_instance
from utils.population import generate_first_population
from utils.verifier import remove_objectives_duplicates, verifier
from utils.dataManipulation import allocate_professors, allocate_reservations, create_variable_classrooms, create_variable_meetings, create_variable_professors, find_preferences, find_relatives_meetings
import mips_epsilon as mips

import os
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'


filename = 'input-seed-1-size-1000.json'

def idleness_allocation_cost(meeting, classrooms):
    cost = []
    for m in meeting:
        cost.append([])
        for c in classrooms:
            alocation_cost = 0
            alocation_cost += (c.capacity - m.demand if c.capacity - m.demand > 0 else 0) if c.capacity - m.demand > c.capacity / 2 else 0
            cost[-1].append(alocation_cost)
        cost[-1].append(0)
    return cost

def dealocated_allocation_cost(meeting, classrooms):
    cost = []
    for m in meeting:
        cost.append([])
        for c in classrooms:
            alocation_cost = 0
            cost[-1].append(alocation_cost)
        cost[-1].append(m.demand)
    return cost

def standing_allocation_cost(meeting, classrooms):
    cost = []
    for m in meeting:
        cost.append([])
        for c in classrooms:
            alocation_cost = 0
            alocation_cost += m.demand - c.capacity if m.demand - c.capacity > 0 else 0
            cost[-1].append(alocation_cost)
        cost[-1].append(0)
    return cost

def isReservated(classroom, schedule, day_name):
    return classroom.days[day_name][schedule]['is_reservation']

objectives = Objectives()

# Reading instance data
instance_data = read_instance(filename)

# Creating variables
instance = parse_data(instance_data)
classrooms = create_variable_classrooms(instance)
professors = create_variable_professors(instance)
meetings = create_variable_meetings(instance, objectives)

# Allocating professors, reservations, preferences and looking for relatives meetings
relatives_meetings = find_relatives_meetings(meetings)
allocate_professors(meetings, professors)
allocate_reservations(classrooms, instance["reservations"])
find_preferences(meetings, instance["preferences"])

# Saving original solution
print(f"[INFO] Saving original solution")
original_meetings = copy.deepcopy(meetings)
original_classrooms = copy.deepcopy(classrooms)
original_objectives = copy.deepcopy(objectives)
original_solution = {
    "meetings": original_meetings,
    "classrooms": original_classrooms,
    "objectives": original_objectives
}
verifier(original_solution)

print(len(original_meetings))
print(len(classrooms))
print(len(instance_data['schedules']))

def mipPy(solution, instance):
    print("[INFO] Starting MIP")

    grouped_schedules = []

    for i in range(len(solution['meetings'])):
        aux = []
        for j in range(len(solution['meetings'][i].schedules) - 1):
            for k in range(j + 1, len(solution['meetings'][i].schedules)):
                aux.append([solution['meetings'][i].schedules[j], solution['meetings'][i].schedules[k]])
        grouped_schedules.append(aux)

    idleness_cost = idleness_allocation_cost(solution['meetings'], solution['classrooms'])
    dealocated_cost = dealocated_allocation_cost(solution['meetings'], solution['classrooms'])
    standing_cost = standing_allocation_cost(solution['meetings'], solution['classrooms'])

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

    standing = xsum(standing_cost[e][s] * ehs[e][s][solution['meetings'][e].schedules[0] - 1] for e in range(E) for s in range(S))
    idleness = xsum(idleness_cost[e][s] * ehs[e][s][solution['meetings'][e].schedules[0] - 1] for e in range(E) for s in range(S))
    dealocated = xsum(dealocated_cost[e][s] * ehs[e][s][solution['meetings'][e].schedules[0] - 1] for e in range(E) for s in range(S))

    m.objective = minimize(idleness)

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
    # m.write("mip_lb.lp")

    actual_value = dealocated.x
    last_value = dealocated.x
    continue_flag = True
    x_axis = []
    y_axis = []
    x_axis.append(dealocated.x)
    y_axis.append(idleness.x)
    solutions = 1

    while (continue_flag):
        # if (solutions % 10 == 0):
        #     print(solutions)
        #     print(f'last_value: {last_value}')
        #     print(f'actual_value: {actual_value}')
        #     print('---------------------------')
        last_value = actual_value

        dealocated_boundary = m.add_constr(dealocated <= last_value - 100, 'dealocated_boundary')
        
        result = m.optimize(max_seconds=40)

        m.remove(m.constr_by_name("dealocated_boundary"))
        if dealocated.x != None:
            x_axis.append(dealocated.x)
        if idleness.x != None:
            y_axis.append(idleness.x)

        if m.status == OptimizationStatus.INFEASIBLE:
            break
        solutions += 1

        actual_value = dealocated.x
        if (actual_value == last_value or actual_value == 0 or actual_value - 100 < 0):
            continue_flag = False

    # print(m.objective_value)
    # print('idleness: ', idleness.x)
    # print('standing: ', standing.x)
    # print('dealocated: ', dealocated.x)
            
    print('Solutions: ', solutions)

    allocations = []

    if m.status == OptimizationStatus.INFEASIBLE:
        return m.objective_value, allocations, x_axis, y_axis

    for e in range(E):
        aux = {
            'meeting_id': solution['meetings'][e].id,
            'classroom_id': 0
        }
        for s in range(S - 1):
            try:
                if (isinstance(ehs[e][s][solution['meetings'][e].schedules[0] - 1], Var) and ehs[e][s][solution['meetings'][e].schedules[0] - 1].x > 0.5):
                # if (ehs[e][s][solution['meetings'][e].schedules[0] - 1].x > 0.5):
                    aux['classroom_id'] = s + 1
            except:
                print('erro')
                print(e, ' - ', s, ' - ', solution['meetings'][e].schedules[0] - 1)
                print(type(ehs[e][s][solution['meetings'][e].schedules[0] - 1]))
                print(isinstance(ehs[e][s][solution['meetings'][e].schedules[0] - 1], Var))
                print(ehs[e][s][solution['meetings'][e].schedules[0] - 1])
                print(ehs[e][s][solution['meetings'][e].schedules[0] - 1].x)
                exit()
        allocations.append(aux)

    print("[INFO] MIP finished")

    return m.objective_value, allocations, x_axis, y_axis

monday = []
tuesday = []
wednesday = []
thursday = []
friday = []
saturday = []
for meeting in original_meetings:
    if meeting.day_name() == 'monday':
        monday.append(meeting)
    elif meeting.day_name() == 'tuesday':
        tuesday.append(meeting)
    elif meeting.day_name() == 'wednesday':
        wednesday.append(meeting)
    elif meeting.day_name() == 'thursday':
        thursday.append(meeting)
    elif meeting.day_name() == 'friday':
        friday.append(meeting)
    elif meeting.day_name() == 'saturday':
        saturday.append(meeting)
    else:
        raise Exception('Invalid day of week')

# Solving subparts using MIP
mip_solution = copy.deepcopy(original_solution)

## Monday
monday_cost, monday_allocations, x, y = mipPy({'meetings': monday, "classrooms": original_classrooms, "objectives": original_objectives}, instance)
for i in monday_allocations:
    if i['classroom_id'] != 0:
        allocate(mip_solution, i['meeting_id'], i['classroom_id'])
print(mip_solution['objectives'].print())

## Tuesday
# tuesday_cost, tuesday_allocations, x, y = mipPy({'meetings': tuesday, "classrooms": original_classrooms, "objectives": original_objectives}, instance)
# for i in tuesday_allocations:
#     if i['classroom_id'] != 0:
#         allocate(mip_solution, i['meeting_id'], i['classroom_id'])
# print(mip_solution['objectives'].print())

## Wednesday
# wednesday_cost, wednesday_allocations, x, y = mipPy({'meetings': wednesday, "classrooms": original_classrooms, "objectives": original_objectives}, instance)
# for i in wednesday_allocations:
#     if i['classroom_id'] != 0:
#         allocate(mip_solution, i['meeting_id'], i['classroom_id'])
# print(mip_solution['objectives'].print())

## Thursday
# thursday_cost, thursday_allocations, x, y = mipPy({'meetings': thursday, "classrooms": original_classrooms, "objectives": original_objectives}, instance)
# for i in thursday_allocations:
#     if i['classroom_id'] != 0:
#         allocate(mip_solution, i['meeting_id'], i['classroom_id'])
# print(mip_solution['objectives'].print())

## Friday
# friday_cost, friday_allocations, x, y = mipPy({'meetings': friday, "classrooms": original_classrooms, "objectives": original_objectives}, instance)
# for i in friday_allocations:
#     if i['classroom_id'] != 0:
#         allocate(mip_solution, i['meeting_id'], i['classroom_id'])
# print(mip_solution['objectives'].print())

## Saturday
# saturday_cost, saturday_allocations, x, y = mipPy({'meetings': saturday, "classrooms": original_classrooms, "objectives": original_objectives}, instance)
# for i in saturday_allocations:
#     if i['classroom_id'] != 0:
#         allocate(mip_solution, i['meeting_id'], i['classroom_id'])
# print(mip_solution['objectives'].print())

# ## Verifying MIP solution
# verifier(mip_solution)
# mip_solution['objectives'].print()
# total_cost = monday_cost + tuesday_cost + wednesday_cost + thursday_cost + friday_cost + saturday_cost
# print(f'[INFO] Total cost: {total_cost}')

# verifier(mip_solution)
# sum = 0
# for i in mip_solution['meetings']:
#     sum += i.demand
# print(sum)