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

def create_variable_meetings(instance):
    meetings = []

    for i in range(len(instance['meetings'])):
        number_of_classes = len(instance['meetings'][i].classes)

        professors = []
        classrooms = []
        preferences = []
        for j in range(number_of_classes):
            professors.append(None)
            classrooms.append(None)
            preferences.append(None)

        meetings.append(Meeting(instance['meetings'][i].is_practical, instance['meetings'][i].day_of_week, instance['meetings'][i].vacancies, instance['meetings'][i].demand, instance['meetings'][i].subject_code, instance['meetings'][i].classes, instance['meetings'][i].schedules, professors, i + 1, classrooms, preferences))

    return meetings
        

