import json
import sys
import copy
import random
from utils.instance import read_instance

def instance_generator():
    if len(sys.argv) != 4:
        print("[Warning] You must pass three and only three parameters for the program to run, the first is the input file, the second is the total number of meetings to generate and the third is the seed")

    if sys.argv[1].split('.')[1] != 'json':
        print(f"[Error] The input file must be a '.json' file, the argument has extension '.{sys.argv[1].split('.')[1]}'")

    filename = sys.argv[1]
    number_of_meetings = int(sys.argv[2])
    seed = int(sys.argv[3])

    instance_data = read_instance(filename)
    random.seed(seed)

    meetings = []
    subjects_count = {}
    schedule_length_probability = [1, 7, 1, 1]
    total_week_repetitions_probability = [1, 8, 1]

    while len(meetings) < number_of_meetings:
        for i in range(len(instance_data['subjects'])):
            if len(meetings) >= number_of_meetings:
                break

            meeting = {
                'isPractical': False,
                'professors': [],
                'subjectCode': instance_data['subjects'][i]['code'],
                'classes': [],
                'schedules': []
            }
            
            if i not in subjects_count:
                subjects_count[instance_data['subjects'][i]['code']] = 1
            else:
                subjects_count[instance_data['subjects'][i]['code']] += 1

            meeting['classes'].append(str(subjects_count[instance_data['subjects'][i]['code']]))

            demand = random.randint(10, 70)
            meeting['demand'] = demand
            meeting['vacancies'] = demand

            schedule_length = random.choices(range(1, 5), schedule_length_probability)[0]
            first_schedule = random.choices(range(1, ((len(instance_data['schedules']) + 1) - (schedule_length - 1))))[0]

            for j in range(first_schedule, first_schedule + schedule_length):
                if  j > len(instance_data['schedules']):
                    raise Exception('The schedule length is too big for the number of schedules in the instance')
                meeting['schedules'].append(j)

            week_repetitions = random.choices(range(1, 4), total_week_repetitions_probability)[0]
            days = [2, 3, 4, 5, 6, 7]
            for i in range(week_repetitions):
                if len(meetings) >= number_of_meetings:
                    break

                day_of_week = random.choices(days)[0]
                days.remove(day_of_week)

                meeting['dayOfWeek'] = day_of_week
                meetings.append(copy.deepcopy(meeting))

    print(len(meetings))

    instance_data['meetings'] = meetings

    with open(f'../json/input/input-seed-{seed}-size-{number_of_meetings}.json', 'w') as f:
        f.write(json.dumps(instance_data))

instance_generator()