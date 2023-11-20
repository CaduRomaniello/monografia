from classes.objectives import Objectives

DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']

def verifier(solution, verbose=True):
    if verbose:
        print("[INFO] Verifying solution")

    verifier_objectives = Objectives()

    for meeting in solution["meetings"]:
        if meeting.classroom_id:
            day_name = meeting.day_name()
            classroom = solution["classrooms"][meeting.classroom_id - 1]
            schedules = meeting.schedules
            for s in schedules:
                if classroom.days[day_name][s - 1]['occupied']:
                    if classroom.days[day_name][s - 1]['meeting_id'] != meeting.id:
                        raise Exception(f"Meeting with id '{meeting.id}' is supposed to be allocated in classroom '{classroom.id}' but it is not. Meeting id '{classroom.days[day_name][s - 1]['meeting_id']}' is allocated instead")
                else:
                    raise Exception(f"Meeting with id '{meeting.id}' is supposed to be allocated in classroom '{classroom.id}' but it is not.")
            demand = meeting.demand
            capacity = classroom.capacity
            verifier_objectives.idleness += (capacity - demand if capacity - demand > 0 else 0) if capacity - demand > capacity / 2 else 0
            verifier_objectives.standing += demand - capacity if demand - capacity > 0 else 0
        else:
            verifier_objectives.deallocated += meeting.demand

    verify_by_classroom(solution)

    if verifier_objectives.idleness != solution["objectives"].idleness:
        raise Exception(f"Idleness objective is not correct. Expected: {verifier_objectives.idleness}, Actual: {solution['objectives'].idleness}")
    
    if verifier_objectives.standing != solution["objectives"].standing:
        raise Exception(f"Standing objective is not correct. Expected: {verifier_objectives.standing}, Actual: {solution['objectives'].standing}")
    
    if verifier_objectives.deallocated != solution["objectives"].deallocated:
        raise Exception(f"Deallocated objective is not correct. Expected: {verifier_objectives.deallocated}, Actual: {solution['objectives'].deallocated}")
    
    if verbose:
        print("[INFO] Solution is correct")
    
def verify_by_classroom(solution):
    for classroom in solution["classrooms"]:
        for day_name in DAYS:
            for schedule in classroom.days[day_name]:
                if schedule['occupied']:
                    if schedule['is_reservation']:
                        continue

                    meeting = solution["meetings"][schedule['meeting_id'] - 1]
                    if meeting.classroom_id != classroom.id:
                        raise Exception(f"Classroom with id '{classroom.id}' is supposed to have meeting with id '{meeting.id}' but it is not. Meeting with id '{meeting.id}' is allocated at '{meeting.classroom_id}' instead.")