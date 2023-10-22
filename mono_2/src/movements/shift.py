import copy
import random
from decouple import config

from movements.allocate import allocate
from movements.deallocate import deallocate

def shift(solution, meeting_id, destiny_classroom_id):
    meeting = solution['meetings'][meeting_id - 1]
    origin_classroom_id = meeting.classroom_id

    deallocate(solution, meeting_id)
    shifted = allocate(solution, meeting_id, destiny_classroom_id)

    if not shifted:
        allocate(solution, meeting_id, origin_classroom_id)
        raise Exception("Could not shift meeting to destiny classroom")

    return shifted