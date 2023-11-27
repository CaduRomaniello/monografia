import json
import os
import copy
import random
from classes.classroom import Classroom
from classes.meeting import Meeting

from classes.objectives import Objectives
from heuristics.lahc_mono import lahc_mono
from heuristics.lahc_multi import lahc_multi
from heuristics.mip import mipPy
from heuristics.nsgaII import nsgaII
from movements.allocate import allocate
from movements.deallocate import deallocate
from movements.shift import shift
from movements.swap import swap
from utils.dataManipulation import allocate_professors, allocate_reservations, create_variable_classrooms, create_variable_meetings, create_variable_professors, find_preferences, find_relatives_meetings
from utils.files import write_solution
from utils.graphics import generate_graphic, generate_graphic_lahc_mono
from utils.instance import parse_data, read_instance
from utils.population import generate_first_population
from utils.verifier import verifier

def serialize(obj):
    if isinstance(obj, (Meeting, Classroom, Objectives)):
        return obj.toJSON()

def pas(filename, seed, max_time):
    random.seed(int(seed))

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

    # Separating solution in subparts to solve it using MIP
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

    ###############################################################################################################################################
    # # Solving subparts using MIP
    # mip_solution = copy.deepcopy(original_solution)

    # ## Monday
    # monday_cost, monday_allocations = mipPy({'meetings': monday, "classrooms": original_classrooms, "objectives": original_objectives}, instance)
    # for i in monday_allocations:
    #     if i['classroom_id'] != 0:
    #         allocate(mip_solution, i['meeting_id'], i['classroom_id'])

    # ## Tuesday
    # tuesday_cost, tuesday_allocations = mipPy({'meetings': tuesday, "classrooms": original_classrooms, "objectives": original_objectives}, instance)
    # for i in tuesday_allocations:
    #     if i['classroom_id'] != 0:
    #         allocate(mip_solution, i['meeting_id'], i['classroom_id'])

    # ## Wednesday
    # wednesday_cost, wednesday_allocations = mipPy({'meetings': wednesday, "classrooms": original_classrooms, "objectives": original_objectives}, instance)
    # for i in wednesday_allocations:
    #     if i['classroom_id'] != 0:
    #         allocate(mip_solution, i['meeting_id'], i['classroom_id'])

    # ## Thursday
    # thursday_cost, thursday_allocations = mipPy({'meetings': thursday, "classrooms": original_classrooms, "objectives": original_objectives}, instance)
    # for i in thursday_allocations:
    #     if i['classroom_id'] != 0:
    #         allocate(mip_solution, i['meeting_id'], i['classroom_id'])

    # ## Friday
    # friday_cost, friday_allocations = mipPy({'meetings': friday, "classrooms": original_classrooms, "objectives": original_objectives}, instance)
    # for i in friday_allocations:
    #     if i['classroom_id'] != 0:
    #         allocate(mip_solution, i['meeting_id'], i['classroom_id'])

    # ## Saturday
    # saturday_cost, saturday_allocations = mipPy({'meetings': saturday, "classrooms": original_classrooms, "objectives": original_objectives}, instance)
    # for i in saturday_allocations:
    #     if i['classroom_id'] != 0:
    #         allocate(mip_solution, i['meeting_id'], i['classroom_id'])

    # ## Verifying MIP solution
    # verifier(mip_solution)
    # mip_solution['objectives'].print()
    # total_cost = monday_cost + tuesday_cost + wednesday_cost + thursday_cost + friday_cost + saturday_cost
    # print(f'[INFO] Total cost: {total_cost}')
    ###############################################################################################################################################

    ###############################################################################################################################################
    # # LAHC-MONO
    # best_solution, graphics = lahc_mono(original_solution, 300, int(max_time))
    # verifier(best_solution)
    # print("[INFO] Verifier passed after LAHC-mono")
    # best_solution['objectives'].print()

    # write_solution(best_solution, seed, max_time, graphics)
    ###############################################################################################################################################

    ###############################################################################################################################################
    # # NSGA-II
    # ## Creating first population
    # population = generate_first_population(original_solution)
    # first_population = copy.deepcopy(population)

    # for p in population:
    #     verifier(p)
    # print("[INFO] Verifier passed before NSGAII")

    # population, fronts, full_population, full_fronts = nsgaII(population, original_solution)
    # print(full_fronts)

    # for p in population:
    #     verifier(p)
    # print("[INFO] Verifier passed after NSGAII")

    # generate_graphic(first_population, population)
    ###############################################################################################################################################

    ###############################################################################################################################################
    # LAHC-MULTI
    best_solutions = lahc_multi(original_solution, 300, int(max_time))

    for solution in best_solutions:
        verifier(solution, verbose=False)
    print("[INFO] Verifier passed after LAHC-multi")
    print(len(best_solutions))

    for solution in best_solutions:
        solution['objectives'].print()
    ###############################################################################################################################################

    # exit()

    # best_solution_value, best_allocations = mipPy(original_solution, instance)
    # print(best_solution_value)

    # for i in best_allocations:
    #     if i['classroom_id'] != 0:
    #         allocate(original_solution, i['meeting_id'], i['classroom_id'])

    # verifier(original_solution)
    # original_solution['objectives'].print()

    # exit()

    # ID == 23
    # for m in meetings:
    #     if m.schedules == original_meetings[0].schedules and m.id != original_meetings[0].id and m.day_of_week == original_meetings[0].day_of_week:
    #         m.print()
    #         break
    # exit()

    # original_meetings[0].print()
    # original_meetings[22].print()
    # print(original_classrooms[0].capacity)
    # print(original_classrooms[2].capacity)
    # original_objectives.print()

    # allocate(original_solution, 1, 1)
    # allocate(original_solution, 23, 3)

    # original_meetings[0].print()
    # original_meetings[22].print()
    # print(original_classrooms[0].days['thursday'][0:4])
    # print(original_classrooms[2].days['thursday'][0:4])
    # original_objectives.print()

    # # allocate(original_solution, 23, 1)

    # shifted = swap(original_solution, 1, 23)
    # # deallocate(original_solution, 1, 2)

    # original_meetings[0].print()
    # original_meetings[22].print()
    # print(original_classrooms[0].days['thursday'][0:4])
    # print(original_classrooms[2].days['thursday'][0:4])
    # original_objectives.print()

    # exit()

    # best_solution, graphics = lahc_mono(original_solution, 300, int(max_time))
    # verifier(best_solution)
    # print("[INFO] Verifier passed after LAHC-mono")
    # best_solution['objectives'].print()

    # write_solution(best_solution, seed, max_time, graphics)
    # # generate_graphic_lahc_mono(graphics)
    exit()

    # Ceating first population
    population = generate_first_population(original_solution)
    first_population = copy.deepcopy(population)
    # population[0]['objectives'].print()
    # population[1]['objectives'].print()
    # population[2]['objectives'].print()
    # population[3]['objectives'].print()
    # population[4]['objectives'].print()

    for p in population:
        verifier(p)
    print("[INFO] Verifier passed before NSGAII")

    population, fronts, full_population, full_fronts = nsgaII(population, original_solution)
    print(full_fronts)

    for p in population:
        verifier(p)
    print("[INFO] Verifier passed after NSGAII")

    generate_graphic(first_population, population)

    # print(len(meetings))
    # print(len(relatives_meetings))
    # for r in relatives_meetings:
    #     if len(r['meetings']) > 2:
    #         for m in r['meetings']:
    #             meetings[m-1].print()
    #             print('-----------------------------')
    #         print()
    #         print('================================================================')

    # relatives_id = meetings[0].relatives_id
    # meetings[0].print()
    # print(meetings[0].professors)
    # print('==========================================')
    # for m in relatives_meetings[relatives_id - 1]["meetings"]:
    #     m.print()
    #     print(m.professors)
    #     print('-------------------------------------------------')

    # print(classrooms[1].days['thursday'])
    print(objectives.deallocated)

    # for m in meetings:
    #     if len(m.preferences) > 0:
    #         print(m.preferences)
