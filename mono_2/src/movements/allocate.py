import copy
import random
from decouple import config

def allocate(solution, meeting_id, classroom_id):
    if not classroom_id:
        raise Exception(f"[Error] Classroom id {classroom_id} is invalid")

    if ((classroom_id > len(solution['classrooms'])) or (classroom_id < 1)):
        raise Exception(f"[Error] Classroom id {classroom_id} is invalid")

    meeting = solution['meetings'][meeting_id - 1]
    schedules = meeting.schedules
    day_name = meeting.day_name()
    classroom = solution['classrooms'][classroom_id - 1]

    allocated = classroom.allocate_meeting(meeting_id, schedules, day_name)

    if allocated:
        meeting.classroom_id = classroom.id
        update_objectives_allocate_move(solution['objectives'], meeting.demand, classroom.capacity)

    return allocated

def update_objectives_allocate_move(objectives, demand, capacity):
    objectives.deallocated -= demand
    objectives.idleness += capacity - demand if capacity - demand > 0 else 0
    objectives.standing += demand - capacity if demand - capacity > 0 else 0