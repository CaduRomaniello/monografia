import json
import os
import copy

from classes.objectives import Objectives
from heuristics.nsgaII import nsgaII
from movements.allocate import allocate
from movements.deallocate import deallocate
from movements.shift import shift
from movements.swap import swap
from utils.dataManipulation import allocate_professors, allocate_reservations, create_variable_classrooms, create_variable_meetings, create_variable_professors, find_preferences, find_relatives_meetings
from utils.graphics import generate_graphic
from utils.instance import parse_data, read_instance
from utils.population import generate_first_population
from utils.verifier import verifier

def pas(filename):
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
