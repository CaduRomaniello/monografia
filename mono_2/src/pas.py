import json
import os

from utils.instance import parse_data, read_instance

def pas(filename):
    print('PAS')
    instance_data = read_instance(filename)

    parsed_data = parse_data(instance_data)

    print(instance_data["schedules"][0])