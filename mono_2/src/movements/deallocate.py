import copy
import random
from decouple import config

def deallocate(solution, meeting_id):
    meeting = solution['meetings'][meeting_id - 1]

    if meeting.classroom_id is None:
        raise Exception(f"[Error] Meeting {meeting_id} is not allocated")

    schedules = meeting.schedules
    day_name = meeting.day_name()
    classroom = solution['classrooms'][meeting.classroom_id - 1]

    classroom.deallocate_meeting(meeting_id, schedules, day_name)

    meeting.classroom_id = None
    update_objectives_deallocate_move(solution['objectives'], meeting.demand, classroom.capacity)


def update_objectives_deallocate_move(objectives, demand, capacity):
    objectives.deallocated += demand
    objectives.idleness -= (capacity - demand if capacity - demand > 0 else 0) if capacity - demand > capacity / 2 else 0
    objectives.standing -= demand - capacity if demand - capacity > 0 else 0