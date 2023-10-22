import copy
import random
from decouple import config

from movements.allocate import allocate
from movements.deallocate import deallocate

def swap(solution, meeting_id_1, meeting_id_2):
    meeting_1 = solution['meetings'][meeting_id_1 - 1]
    meeting_2 = solution['meetings'][meeting_id_2 - 1]
    classroom_id_1 = meeting_1.classroom_id
    classroom_id_2 = meeting_2.classroom_id

    deallocate(solution, meeting_id_1)
    deallocate(solution, meeting_id_2)

    allocated_1 = allocate(solution, meeting_id_1, classroom_id_2)
    if not allocated_1:
        allocate(solution, meeting_id_1, classroom_id_1)
        allocate(solution, meeting_id_2, classroom_id_2)
        return False
    
    allocated_2 = allocate(solution, meeting_id_2, classroom_id_1)
    if not allocated_2:
        deallocate(solution, meeting_id_1)
        allocate(solution, meeting_id_1, classroom_id_1)
        allocate(solution, meeting_id_2, classroom_id_2)
        return False

    return True