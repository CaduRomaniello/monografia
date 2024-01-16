import json
import os

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

def write_solutions_multi(solutions, seed, max_time, algorithm, filename):
    print(f"\n[INFO] Writing solution")
    current_directory = os.getcwd()
    print('Diretório de Trabalho Atual:', current_directory)

    result = []
    for i in range(len(solutions)):
        result.append([])
        for j in range(len(solutions[i])):
            result[i].append(solutions[i][j]['objectives'])

    if filename != 'instance.json':
        filename = filename.split('.')[0].split('input-')[1]
    else:
        filename = filename.split('.')[0]

    try:
        with open(f'./json/output/{algorithm}/output-instance-{filename}-params-seed-{seed}-time-{max_time}.json', 'w') as f:
            f.write(json.dumps(result, default=serialize))
    except:
        with open(f'../json/output/{algorithm}/output-instance-{filename}-params-seed-{seed}-time-{max_time}.json', 'w') as f:
            f.write(json.dumps(result, default=serialize))