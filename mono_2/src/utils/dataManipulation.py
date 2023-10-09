import copy
import random

from classes.classroom import Classroom
from classes.meeting import Meeting
from classes.professor import Professor


def create_variable_classrooms(instance):
    classrooms = []

    for classroom in instance['classrooms']:
        monday = []
        thursday = []
        wednesday = []
        tuesday = []
        friday = []
        saturday = []

        for i in range(len(instance['schedules'])):
            monday.append({
                "occupied": False,
                "meeting_id": None,
                "is_reservation": False
            })
            thursday.append({
                "occupied": False,
                "meeting_id": None,
                "is_reservation": False
            })
            wednesday.append({
                "occupied": False,
                "meeting_id": None,
                "is_reservation": False
            })
            tuesday.append({
                "occupied": False,
                "meeting_id": None,
                "is_reservation": False
            })
            friday.append({
                "occupied": False,
                "meeting_id": None,
                "is_reservation": False
            })
            saturday.append({
                "occupied": False,
                "meeting_id": None,
                "is_reservation": False
            })

        days = {
            "monday": monday,
            "thursday": thursday,
            "wednesday": wednesday,
            "tuesday": tuesday,
            "friday": friday,
            "saturday": saturday,
        }

        classrooms.append(Classroom(classroom.id, classroom.is_lab, classroom.capacity, classroom.building_id, classroom.description, classroom.floor, classroom.board, classroom.projector, days))

    return classrooms

def create_variable_professors(instance):
    professors = []

    for professor in instance['professors']:
        monday = []
        thursday = []
        wednesday = []
        tuesday = []
        friday = []
        saturday = []

        for i in range(len(instance['schedules'])):
            monday.append({
                "occupied": False,
                "meeting_id": None,
            })
            thursday.append({
                "occupied": False,
                "meeting_id": None,
            })
            wednesday.append({
                "occupied": False,
                "meeting_id": None,
            })
            tuesday.append({
                "occupied": False,
                "meeting_id": None,
            })
            friday.append({
                "occupied": False,
                "meeting_id": None,
            })
            saturday.append({
                "occupied": False,
                "meeting_id": None,
            })

        days = {
            "monday": monday,
            "thursday": thursday,
            "wednesday": wednesday,
            "tuesday": tuesday,
            "friday": friday,
            "saturday": saturday,
        }

        professors.append(Professor(professor.code, professor.name, days))

    return professors

def create_variable_meetings(instance, objectives):
    meetings = []

    for i in range(len(instance['meetings'])):
        objectives.deallocated += instance['meetings'][i].demand

        meetings.append(Meeting(instance['meetings'][i].is_practical, instance['meetings'][i].day_of_week, instance['meetings'][i].vacancies, instance['meetings'][i].demand, instance['meetings'][i].subject_code, instance['meetings'][i].classes, instance['meetings'][i].schedules, i + 1, [], None, [], None))

    return meetings
        
def find_relatives_meetings(meetings):
    relatives = []
    relatives_count = 1

    meetings_copy = copy.deepcopy(meetings)

    while meetings_copy:
        meeting = meetings_copy.pop(0)

        meeting_id = meeting.id
        subject_code = meeting.subject_code
        classes = meeting.classes

        ############################################## just a sily print
        # print(f"Meeting id: {meeting_id}, original id: {meetings[meeting_id-1].id}")
        # print(f"Subject code: {subject_code}, original subject code: {meetings[meeting_id-1].subject_code}")
        # print(f"Classes: {classes}, original classes: {meetings[meeting_id-1].classes}")
        # print(f"Day of week: {day_of_week}, original day of week: {meetings[meeting_id-1].day_of_week}")
        # print()
        # print('--------------------------------------------------------------------------------------------')
        # print()
        ############################################## just a sily print

        found = False
        relative_index = None
        for i in range(len(relatives)):
            if relatives[i]["subject_code"] == subject_code and relatives[i]["classes"] == classes:
                found = True
                relative_index = i
                break

        if found:
            relatives[relative_index]["meetings"].append(meetings[meeting_id - 1].id)
            meetings[meeting_id - 1].relatives_id = relative_index + 1
        else:
            relatives.append({
                "subject_code": subject_code,
                "classes": classes,
                "meetings": [meetings[meeting_id - 1].id]
            })

            meetings[meeting_id - 1].relatives_id = relatives_count
            relatives_count += 1

    return relatives

def allocate_professors(meetings, professors):
    for meeting in meetings:
        schedules = meeting.schedules
        meeting_id = meeting.id
        day_name = meeting.day_name()

        professor_index = random.randrange(0, len(professors))
        allocated = False
        for i in range(len(professors)):
            allocated = professors[professor_index].check_availability_and_allocate(day_name, schedules, meeting_id)

            if allocated:
                meeting.professors.append(professors[professor_index])
                break

            if professor_index == len(professors) - 1:
                professor_index = 0
            else:
                professor_index += 1

        if not allocated:
            raise Exception(f"Could not find a professor for meeting with id {meeting.id}")

def allocate_reservations(classrooms, reservations):
    for r in reservations:
        classrooms[r.classroom_id - 1].allocate_reservation(r.schedule_id, r.day_name())

def find_preferences(meetings, preferences):
    for p in preferences:
        code = p.category_code
        category = p.category

        for m in meetings:
            if category == 'professor':
                for pr in m.professors:
                    if pr.code == code:
                        m.preferences.append(p)
                        break
            elif category == 'class':
                for c in m.classes:
                    if code == m.subject_code + '-' + c:
                        m.preferences.append(p)
                        break
            else:
                raise Exception(f"Preference category invalid, it must be 'professor' or 'class'. It has category {category}")
