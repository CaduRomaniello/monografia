import json
import os
from datetime import datetime

from classes.schedule import Schedule

def read_instance(filename):
    actual_path = os.path.dirname(__file__)
    instance_path = os.path.join(actual_path, f"..\..\json\input\{filename}")

    f = open(instance_path)
    data = json.load(f)

    return data

def parse_data(data):
    obj = {}

    obj["schedules"] = parse_schedules(data.get("schedules"))

def parse_schedules(schedules):
    if not schedules:
        raise Exception("No schedules in data file")
    
    parsed_schedules = []
    for schedule in schedules:
        start_time = datetime.strptime(f"{schedule['startTime'].split(':')[0]}:{schedule['startTime'].split(':')[1]}", "%H:%M")
        end_tine = datetime.strptime(f"{schedule['endTime'].split(':')[0]}:{schedule['endTime'].split(':')[1]}", "%H:%M")

        parsed_schedules.append(Schedule(schedule["ID"], start_time, end_tine))
    
    return parsed_schedules
