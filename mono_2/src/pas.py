import json
import os

from utils.dataManipulation import create_variable_classrooms, create_variable_meetings, create_variable_professors
from utils.instance import parse_data, read_instance

def pas(filename):
    print('PAS')
    instance_data = read_instance(filename)

    instance = parse_data(instance_data)
    classrooms = create_variable_classrooms(instance)
    professors = create_variable_professors(instance)
    meetings = create_variable_meetings(instance)


    print(meetings[0].classrooms)
    classrooms[0].days['monday'][0]['occupied'] = True
    print()
    print(meetings[0].classrooms)