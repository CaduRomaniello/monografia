import os
import sys
import copy
import json
import plotly.graph_objects as go
import numpy
import datetime

from mip import *
# from heuristics.mip import mipPy
from utils.pareto import dominates
from movements.allocate import allocate
from classes.objectives import Objectives
from classes.classroom import Classroom
from classes.meeting import Meeting
from pymoo.indicators.hv import Hypervolume
from utils.instance import parse_data, read_instance
from utils.population import generate_first_population
from utils.verifier import remove_objectives_duplicates, verifier
from utils.dataManipulation import allocate_professors, allocate_reservations, create_variable_classrooms, create_variable_meetings, create_variable_professors, find_preferences, find_relatives_meetings
import mips_epsilon as mips

import os
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'


original_filename = sys.argv[1]

def serialize(obj):
    if isinstance(obj, (Meeting, Classroom, Objectives)):
        return obj.toJSON()
    
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

def deallocated_allocation_cost(meeting, classrooms):
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
instance_data = read_instance(original_filename)

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

def max_objectives(filename):
    idleness = []
    standing = []
    deallocated = []

    current_directory = os.getcwd()
    print('Diretório de Trabalho Atual:', current_directory)

    if filename != 'instance.json':
        path = filename.split('.')[0].split('input-')[1]
    else:
        path = filename.split('.')[0]
    
    for i in range(5):
        with open(f'../json/output/lahc-multi/output-instance-{path}-params-seed-{i + 1}-time-900.json', 'r') as file:
            data = json.load(file)
            for i in data[0]:
                idleness.append(i['idleness'])
                standing.append(i['standing'])
                deallocated.append(i['deallocated'])

    for i in range(5):
        with open(f'../json/output/nsgaII/output-instance-{path}-params-seed-{i + 1}-time-900.json', 'r') as file:
            data = json.load(file)
            for i in data[0]:
                idleness.append(i['idleness'])
                standing.append(i['standing'])
                deallocated.append(i['deallocated'])

    return max(idleness), max(standing), max(deallocated)

def mipPy(instance, classrooms, monday, tuesday, wednesday, thursday, friday, saturday, epsilon=200):
    print("[INFO] Starting MIP")

    ## READING MAX OF EACH OBJECTIVE
    max_idleness, max_standing, max_deallocated = max_objectives(original_filename)
    max_idleness += 200
    max_standing += 200
    max_deallocated += 200

    ## GROUPED SCHEDULES

    # Monday grouped schedules
    monday_grouped_schedules = []
    for i in range(len(monday)):
        aux = []
        for j in range(len(monday[i].schedules) - 1):
            for k in range(j + 1, len(monday[i].schedules)):
                aux.append([monday[i].schedules[j], monday[i].schedules[k]])
        monday_grouped_schedules.append(aux)
    # Tuesday grouped schedules
    tuesday_grouped_schedules = []
    for i in range(len(tuesday)):
        aux = []
        for j in range(len(tuesday[i].schedules) - 1):
            for k in range(j + 1, len(tuesday[i].schedules)):
                aux.append([tuesday[i].schedules[j], tuesday[i].schedules[k]])
        tuesday_grouped_schedules.append(aux)
    # Wednesday grouped schedules
    wednesday_grouped_schedules = []
    for i in range(len(wednesday)):
        aux = []
        for j in range(len(wednesday[i].schedules) - 1):
            for k in range(j + 1, len(wednesday[i].schedules)):
                aux.append([wednesday[i].schedules[j], wednesday[i].schedules[k]])
        wednesday_grouped_schedules.append(aux)
    # Thursday grouped schedules
    thursday_grouped_schedules = []
    for i in range(len(thursday)):
        aux = []
        for j in range(len(thursday[i].schedules) - 1):
            for k in range(j + 1, len(thursday[i].schedules)):
                aux.append([thursday[i].schedules[j], thursday[i].schedules[k]])
        thursday_grouped_schedules.append(aux)
    # Friday grouped schedules
    friday_grouped_schedules = []
    for i in range(len(friday)):
        aux = []
        for j in range(len(friday[i].schedules) - 1):
            for k in range(j + 1, len(friday[i].schedules)):
                aux.append([friday[i].schedules[j], friday[i].schedules[k]])
        friday_grouped_schedules.append(aux)
    # Saturday grouped schedules
    saturday_grouped_schedules = []
    for i in range(len(saturday)):
        aux = []
        for j in range(len(saturday[i].schedules) - 1):
            for k in range(j + 1, len(saturday[i].schedules)):
                aux.append([saturday[i].schedules[j], saturday[i].schedules[k]])
        saturday_grouped_schedules.append(aux)

    ## MATRIX OF ALOCATION COSTS

    # Idleness allocation cost
    monday_idleness_cost = idleness_allocation_cost(monday, classrooms)
    tuesday_idleness_cost = idleness_allocation_cost(tuesday, classrooms)
    wednesday_idleness_cost = idleness_allocation_cost(wednesday, classrooms)
    thursday_idleness_cost = idleness_allocation_cost(thursday, classrooms)
    friday_idleness_cost = idleness_allocation_cost(friday, classrooms)
    saturday_idleness_cost = idleness_allocation_cost(saturday, classrooms)

    # Deallocated allocation cost
    monday_deallocated_cost = deallocated_allocation_cost(monday, classrooms)
    tuesday_deallocated_cost = deallocated_allocation_cost(tuesday, classrooms)
    wednesday_deallocated_cost = deallocated_allocation_cost(wednesday, classrooms)
    thursday_deallocated_cost = deallocated_allocation_cost(thursday, classrooms)
    friday_deallocated_cost = deallocated_allocation_cost(friday, classrooms)
    saturday_deallocated_cost = deallocated_allocation_cost(saturday, classrooms)

    # Standing allocation cost
    monday_standing_cost = standing_allocation_cost(monday, classrooms)
    tuesday_standing_cost = standing_allocation_cost(tuesday, classrooms)
    wednesday_standing_cost = standing_allocation_cost(wednesday, classrooms)
    thursday_standing_cost = standing_allocation_cost(thursday, classrooms)
    friday_standing_cost = standing_allocation_cost(friday, classrooms)
    saturday_standing_cost = standing_allocation_cost(saturday, classrooms)

    # Creating model
    m = Model()
    m.verbose = 0

    # Defining fixed variables
    S = len(classrooms) + 1
    H = len(instance['schedules'])

    ## VARIABLES

    # Monday variables
    monday_variables = []
    for e in range(len(monday)):
        monday_variables.append([])
        for s in range(S):
            monday_variables[e].append([])
            for h in range(H):
                reservated = isReservated(classrooms[s], h, monday[e].day_name()) if s < S - 1 else False
                if ((h + 1 in monday[e].schedules) and not reservated):
                    monday_variables[e][s].append(m.add_var(var_type=BINARY, name=f"x({e},{s},{h})"))
                else:
                    monday_variables[e][s].append(0)
    # Tuesday variables
    tuesday_variables = []
    for e in range(len(tuesday)):
        tuesday_variables.append([])
        for s in range(S):
            tuesday_variables[e].append([])
            for h in range(H):
                reservated = isReservated(classrooms[s], h, tuesday[e].day_name()) if s < S - 1 else False
                if ((h + 1 in tuesday[e].schedules) and not reservated):
                    tuesday_variables[e][s].append(m.add_var(var_type=BINARY, name=f"x({e},{s},{h})"))
                else:
                    tuesday_variables[e][s].append(0)
    # Wednesday variables
    wednesday_variables = []
    for e in range(len(wednesday)):
        wednesday_variables.append([])
        for s in range(S):
            wednesday_variables[e].append([])
            for h in range(H):
                reservated = isReservated(classrooms[s], h, wednesday[e].day_name()) if s < S - 1 else False
                if ((h + 1 in wednesday[e].schedules) and not reservated):
                    wednesday_variables[e][s].append(m.add_var(var_type=BINARY, name=f"x({e},{s},{h})"))
                else:
                    wednesday_variables[e][s].append(0)
    # Thursday variables
    thursday_variables = []
    for e in range(len(thursday)):
        thursday_variables.append([])
        for s in range(S):
            thursday_variables[e].append([])
            for h in range(H):
                reservated = isReservated(classrooms[s], h, thursday[e].day_name()) if s < S - 1 else False
                if ((h + 1 in thursday[e].schedules) and not reservated):
                    thursday_variables[e][s].append(m.add_var(var_type=BINARY, name=f"x({e},{s},{h})"))
                else:
                    thursday_variables[e][s].append(0)
    # Friday variables
    friday_variables = []
    for e in range(len(friday)):
        friday_variables.append([])
        for s in range(S):
            friday_variables[e].append([])
            for h in range(H):
                reservated = isReservated(classrooms[s], h, friday[e].day_name()) if s < S - 1 else False
                if ((h + 1 in friday[e].schedules) and not reservated):
                    friday_variables[e][s].append(m.add_var(var_type=BINARY, name=f"x({e},{s},{h})"))
                else:
                    friday_variables[e][s].append(0)
    # Saturday variables
    saturday_variables = []
    for e in range(len(saturday)):
        saturday_variables.append([])
        for s in range(S):
            saturday_variables[e].append([])
            for h in range(H):
                reservated = isReservated(classrooms[s], h, saturday[e].day_name()) if s < S - 1 else False
                if ((h + 1 in saturday[e].schedules) and not reservated):
                    saturday_variables[e][s].append(m.add_var(var_type=BINARY, name=f"x({e},{s},{h})"))
                else:
                    saturday_variables[e][s].append(0)

    ## OBJECTIVE FUNCTIONS

    # Monday
    monday_standing = xsum(monday_standing_cost[e][s] * monday_variables[e][s][monday[e].schedules[0] - 1] for e in range(len(monday)) for s in range(S))
    monday_idleness = xsum(monday_idleness_cost[e][s] * monday_variables[e][s][monday[e].schedules[0] - 1] for e in range(len(monday)) for s in range(S))
    monday_deallocated = xsum(monday_deallocated_cost[e][s] * monday_variables[e][s][monday[e].schedules[0] - 1] for e in range(len(monday)) for s in range(S))

    # Tuesday
    tuesday_standing = xsum(tuesday_standing_cost[e][s] * tuesday_variables[e][s][tuesday[e].schedules[0] - 1] for e in range(len(tuesday)) for s in range(S))
    tuesday_idleness = xsum(tuesday_idleness_cost[e][s] * tuesday_variables[e][s][tuesday[e].schedules[0] - 1] for e in range(len(tuesday)) for s in range(S))
    tuesday_deallocated = xsum(tuesday_deallocated_cost[e][s] * tuesday_variables[e][s][tuesday[e].schedules[0] - 1] for e in range(len(tuesday)) for s in range(S))

    # Wednesday
    wednesday_standing = xsum(wednesday_standing_cost[e][s] * wednesday_variables[e][s][wednesday[e].schedules[0] - 1] for e in range(len(wednesday)) for s in range(S))
    wednesday_idleness = xsum(wednesday_idleness_cost[e][s] * wednesday_variables[e][s][wednesday[e].schedules[0] - 1] for e in range(len(wednesday)) for s in range(S))
    wednesday_deallocated = xsum(wednesday_deallocated_cost[e][s] * wednesday_variables[e][s][wednesday[e].schedules[0] - 1] for e in range(len(wednesday)) for s in range(S))

    # Thursday
    thursday_standing = xsum(thursday_standing_cost[e][s] * thursday_variables[e][s][thursday[e].schedules[0] - 1] for e in range(len(thursday)) for s in range(S))
    thursday_idleness = xsum(thursday_idleness_cost[e][s] * thursday_variables[e][s][thursday[e].schedules[0] - 1] for e in range(len(thursday)) for s in range(S))
    thursday_deallocated = xsum(thursday_deallocated_cost[e][s] * thursday_variables[e][s][thursday[e].schedules[0] - 1] for e in range(len(thursday)) for s in range(S))

    # Friday
    friday_standing = xsum(friday_standing_cost[e][s] * friday_variables[e][s][friday[e].schedules[0] - 1] for e in range(len(friday)) for s in range(S))
    friday_idleness = xsum(friday_idleness_cost[e][s] * friday_variables[e][s][friday[e].schedules[0] - 1] for e in range(len(friday)) for s in range(S))
    friday_deallocated = xsum(friday_deallocated_cost[e][s] * friday_variables[e][s][friday[e].schedules[0] - 1] for e in range(len(friday)) for s in range(S))

    # Saturday
    saturday_standing = xsum(saturday_standing_cost[e][s] * saturday_variables[e][s][saturday[e].schedules[0] - 1] for e in range(len(saturday)) for s in range(S))
    saturday_idleness = xsum(saturday_idleness_cost[e][s] * saturday_variables[e][s][saturday[e].schedules[0] - 1] for e in range(len(saturday)) for s in range(S))
    saturday_deallocated = xsum(saturday_deallocated_cost[e][s] * saturday_variables[e][s][saturday[e].schedules[0] - 1] for e in range(len(saturday)) for s in range(S))

    # General functions
    idleness = monday_idleness + tuesday_idleness + wednesday_idleness + thursday_idleness + friday_idleness + saturday_idleness
    standing = monday_standing + tuesday_standing + wednesday_standing + thursday_standing + friday_standing + saturday_standing
    deallocated = monday_deallocated + tuesday_deallocated + wednesday_deallocated + thursday_deallocated + friday_deallocated + saturday_deallocated

    ## MAIN OBJECTIVE FUNCTION

    m.objective = minimize(monday_deallocated + tuesday_deallocated + wednesday_deallocated + thursday_deallocated + friday_deallocated + saturday_deallocated)

    ## FIXED RESTRICTIONS

    # All meetings should be alocated
    # Monday
    for e in range(len(monday)):
            for h in monday[e].schedules:
                m += xsum(monday_variables[e][s][h - 1] for s in range(S)) == 1
    # Tuesday
    for e in range(len(tuesday)):
            for h in tuesday[e].schedules:
                m += xsum(tuesday_variables[e][s][h - 1] for s in range(S)) == 1
    # Wednesday
    for e in range(len(wednesday)):
            for h in wednesday[e].schedules:
                m += xsum(wednesday_variables[e][s][h - 1] for s in range(S)) == 1
    # Thursday
    for e in range(len(thursday)):
            for h in thursday[e].schedules:
                m += xsum(thursday_variables[e][s][h - 1] for s in range(S)) == 1
    # Friday
    for e in range(len(friday)):
            for h in friday[e].schedules:
                m += xsum(friday_variables[e][s][h - 1] for s in range(S)) == 1
    # Saturday
    for e in range(len(saturday)):
            for h in saturday[e].schedules:
                m += xsum(saturday_variables[e][s][h - 1] for s in range(S)) == 1

    # Classrooms can have a maximum of one meeting per schedule
    # Monday
    for s in range(S - 1):
        for h in range(H):
            m += xsum(monday_variables[e][s][h] for e in range(len(monday))) <= 1
    # Tuesday
    for s in range(S - 1):
        for h in range(H):
            m += xsum(tuesday_variables[e][s][h] for e in range(len(tuesday))) <= 1
    # Wednesday
    for s in range(S - 1):
        for h in range(H):
            m += xsum(wednesday_variables[e][s][h] for e in range(len(wednesday))) <= 1
    # Thursday
    for s in range(S - 1):
        for h in range(H):
            m += xsum(thursday_variables[e][s][h] for e in range(len(thursday))) <= 1
    # Friday
    for s in range(S - 1):
        for h in range(H):
            m += xsum(friday_variables[e][s][h] for e in range(len(friday))) <= 1
    # Saturday
    for s in range(S - 1):
        for h in range(H):
            m += xsum(saturday_variables[e][s][h] for e in range(len(saturday))) <= 1

    # Twinned times must be allocated in the same room
    # Monday
    for e in range(len(monday)):
        for s in range(S):
            for h in range(len(monday_grouped_schedules[e])):
                restricao = monday_variables[e][s][monday_grouped_schedules[e][h][0] - 1] == monday_variables[e][s][monday_grouped_schedules[e][h][1] - 1]
                if not isinstance(restricao, bool):
                    m += monday_variables[e][s][monday_grouped_schedules[e][h][0] - 1] == monday_variables[e][s][monday_grouped_schedules[e][h][1] - 1]
    # Tuesday
    for e in range(len(tuesday)):
        for s in range(S):
            for h in range(len(tuesday_grouped_schedules[e])):
                restricao = tuesday_variables[e][s][tuesday_grouped_schedules[e][h][0] - 1] == tuesday_variables[e][s][tuesday_grouped_schedules[e][h][1] - 1]
                if not isinstance(restricao, bool):
                    m += tuesday_variables[e][s][tuesday_grouped_schedules[e][h][0] - 1] == tuesday_variables[e][s][tuesday_grouped_schedules[e][h][1] - 1]
    # Wednesday
    for e in range(len(wednesday)):
        for s in range(S):
            for h in range(len(wednesday_grouped_schedules[e])):
                restricao = wednesday_variables[e][s][wednesday_grouped_schedules[e][h][0] - 1] == wednesday_variables[e][s][wednesday_grouped_schedules[e][h][1] - 1]
                if not isinstance(restricao, bool):
                    m += wednesday_variables[e][s][wednesday_grouped_schedules[e][h][0] - 1] == wednesday_variables[e][s][wednesday_grouped_schedules[e][h][1] - 1]
    # Thursday
    for e in range(len(thursday)):
        for s in range(S):
            for h in range(len(thursday_grouped_schedules[e])):
                restricao = thursday_variables[e][s][thursday_grouped_schedules[e][h][0] - 1] == thursday_variables[e][s][thursday_grouped_schedules[e][h][1] - 1]
                if not isinstance(restricao, bool):
                    m += thursday_variables[e][s][thursday_grouped_schedules[e][h][0] - 1] == thursday_variables[e][s][thursday_grouped_schedules[e][h][1] - 1]
    # Friday
    for e in range(len(friday)):
        for s in range(S):
            for h in range(len(friday_grouped_schedules[e])):
                restricao = friday_variables[e][s][friday_grouped_schedules[e][h][0] - 1] == friday_variables[e][s][friday_grouped_schedules[e][h][1] - 1]
                if not isinstance(restricao, bool):
                    m += friday_variables[e][s][friday_grouped_schedules[e][h][0] - 1] == friday_variables[e][s][friday_grouped_schedules[e][h][1] - 1]
    # Saturday
    for e in range(len(saturday)):
        for s in range(S):
            for h in range(len(saturday_grouped_schedules[e])):
                restricao = saturday_variables[e][s][saturday_grouped_schedules[e][h][0] - 1] == saturday_variables[e][s][saturday_grouped_schedules[e][h][1] - 1]
                if not isinstance(restricao, bool):
                    m += saturday_variables[e][s][saturday_grouped_schedules[e][h][0] - 1] == saturday_variables[e][s][saturday_grouped_schedules[e][h][1] - 1]

    # Upper bound for each objective
    # m.add_constr(idleness <= max_idleness)
    # m.add_constr(standing <= max_standing)
    m.add_constr(deallocated <= max_deallocated) # Maybe remove this restriction

    ## NESTED RESTRICTED EPSILON

    # Variables
    deallocated_axis = []
    idleness_axis = []
    standing_axis = []
    solutions = 0
    idleness_continue_flag = True

    # Optimization phase
    print(f"[INFO] Starting restricted epsilon optimization for IDLENESS objective")
    idleness_constr_value = max_idleness + epsilon
    while idleness_continue_flag:
        print(f"[INFO] Solutions: {solutions} - {datetime.datetime.now()}")
        m.add_constr(idleness <= idleness_constr_value - epsilon, 'idleness_boundary')

        standing_continue_flag = True
        standing_constr_value = max_standing + epsilon
        while standing_continue_flag:
            if (solutions % 10 == 0):
                print(f"    [INFO] Solutions: {solutions} - {datetime.datetime.now()} - idleness_constr_value {idleness_constr_value} - standing_constr_value {standing_constr_value}")
                print(f'    {m.status}, {deallocated.x}, {idleness.x}, {standing.x}')

            m.add_constr(standing <= standing_constr_value - epsilon, 'standing_boundary')

            m.optimize(max_seconds=60)
            
            m.remove(m.constr_by_name("standing_boundary"))

            if deallocated.x != None and idleness.x != None and standing.x != None:
                deallocated_axis.append(deallocated.x)
                idleness_axis.append(idleness.x)
                standing_axis.append(standing.x)

            if m.status == OptimizationStatus.INFEASIBLE:
                break

            solutions += 1

            standing_constr_value -= epsilon
            if (standing.x == None or standing.x == 0 or standing_constr_value - epsilon < 0):
                standing_continue_flag = False

        m.remove(m.constr_by_name("idleness_boundary"))
        idleness_constr_value -= epsilon
        if (idleness.x == 0 or idleness_constr_value - epsilon < 0):
            idleness_continue_flag = False

    print()
    print('-----------------------------------------')
    print('-----------------------------------------')
    print(f'Total solutions: {solutions}')

    return m.objective_value, {}, deallocated_axis, idleness_axis, standing_axis

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

cost, allocation, deallocated, idleness, standing = mipPy(instance, original_classrooms, monday, tuesday, wednesday, thursday, friday, saturday, 30)

def nondominated_sort(solutions):
    fronts = []
    domination_count = [0] * len(solutions)
    dominated_solutions = [[] for _ in range(len(solutions))]

    for i in range(len(solutions)):
        for j in range(i + 1, len(solutions)):
            if dominates(solutions[i], solutions[j]):
                dominated_solutions[i].append(j)
                domination_count[j] += 1
            elif dominates(solutions[j], solutions[i]):
                dominated_solutions[j].append(i)
                domination_count[i] += 1

    front = []
    for i in range(len(solutions)):
        if domination_count[i] == 0:
            front.append(i)

    while front:
        next_front = []
        for i in front:
            for j in dominated_solutions[i]:
                domination_count[j] -= 1
                if domination_count[j] == 0:
                    next_front.append(j)
        fronts.append(front)
        front = next_front

    return fronts

filename = original_filename

print(f"\n[INFO] Writing solution")
current_directory = os.getcwd()
print('Diretório de Trabalho Atual:', current_directory)
print(len(deallocated), len(idleness), len(standing))

results = []
for i in range(len(deallocated)):
    results.append(Objectives(idleness[i], deallocated[i], standing[i]))

results = remove_objectives_duplicates(results)
fronts = nondominated_sort(results)
print(fronts)

output = []
for i in range(len(fronts)):
    output.append([])
    for j in fronts[i]:
        output[i].append(results[j])

# results[9].print()
print(filename)

if filename != 'instance.json':
    print(filename.split('.'))
    print(filename.split('.')[0].split('input-'))
    filename = filename.split('.')[0].split('input-')[1]
else:
    filename = filename.split('.')[0]

try:
    with open(f'./json/output/epsilon/output-instance-{filename}-params-epsilon.json', 'w') as f:
        f.write(json.dumps([results], default=serialize))
except:
    with open(f'../json/output/epsilon/output-instance-{filename}-params-epsilon.json', 'w') as f:
        f.write(json.dumps([results], default=serialize))