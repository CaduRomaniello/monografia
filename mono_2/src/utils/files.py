import json

from classes.meeting import Meeting
from classes.classroom import Classroom
from classes.objectives import Objectives

def serialize(obj):
    if isinstance(obj, (Meeting, Classroom, Objectives)):
        return obj.toJSON()

def write_solution(solution, seed, max_time, graphics):
    print(f"\n[INFO] Writing solution")
    result = {
        'objectives': solution['objectives'],
        'meetings': solution['meetings']
    }
    with open(f'../json/output/output-seed-{seed}-time-{max_time}.json', 'w') as f:
        f.write(json.dumps(result, default=serialize))

    with open(f'../json/output/graphics/graphics-seed-{seed}-time-{max_time}.json', 'w') as f:
        f.write(json.dumps(graphics))