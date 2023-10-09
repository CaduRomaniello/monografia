import json
import os
import copy

from classes.objectives import Objectives
from utils.dataManipulation import allocate_professors, allocate_reservations, create_variable_classrooms, create_variable_meetings, create_variable_professors, find_preferences, find_relatives_meetings
from utils.instance import parse_data, read_instance

def pas(filename):
    objectives = Objectives()

    instance_data = read_instance(filename)

    instance = parse_data(instance_data)
    classrooms = create_variable_classrooms(instance)
    professors = create_variable_professors(instance)
    meetings = create_variable_meetings(instance, objectives)

    relatives_meetings = find_relatives_meetings(meetings)
    allocate_professors(meetings, professors)
    allocate_reservations(classrooms, instance["reservations"])
    find_preferences(meetings, instance["preferences"])

    original_meetings = copy.deepcopy(meetings)
    original_classrooms = copy.deepcopy(classrooms)

    print(len(meetings))
    print(len(relatives_meetings))
    for r in relatives_meetings:
        if len(r['meetings']) > 2:
            for m in r['meetings']:
                meetings[m-1].print()
                print('-----------------------------')
            print()
            print('================================================================')

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
