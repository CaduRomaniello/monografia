import json
import os
from datetime import datetime

from classes.instanceClassroom import InstanceClassroom
from classes.instanceBuilding import InstanceBuilding
from classes.instanceMeeting import InstanceMeeting
from classes.instancePreference import InstancePreference
from classes.instanceProfessor import InstanceProfessor
from classes.instanceReservation import InstanceReservation
from classes.instanceRestriction import InstanceRestriction
from classes.instanceSchedule import InstanceSchedule
from classes.instanceSubject import InstanceSubject

def read_instance(filename):
    actual_path = os.path.dirname(__file__)
    instance_path = os.path.join(actual_path, f"..\..\json\input\{filename}")

    f = open(instance_path)
    data = json.load(f)

    return data

def parse_data(data):
    instance = {}

    instance["schedules"] = parse_schedules(data.get("schedules"))
    instance["buildings"] = parse_buildings(data.get("buildings"))
    instance["classrooms"] = parse_classrooms(data.get("classrooms"))
    instance["professors"] = parse_professors(data.get("professors"))
    instance["subjects"] = parse_subjects(data.get("subjects"))
    instance["meetings"] = parse_meetings(data.get("meetings"))
    instance["preferences"] = parse_preferences(data.get("preferences"))
    instance["restrictions"] = parse_restrictions(data.get("restrictions"))
    instance["reservations"] = parse_reservations(data.get("reservations"))

    return instance

def parse_schedules(schedules):
    if not schedules:
        raise Exception("No schedules in data file")
    
    parsed_schedules = []
    for schedule in schedules:
        start_time = datetime.strptime(f"{schedule['startTime'].split(':')[0]}:{schedule['startTime'].split(':')[1]}", "%H:%M")
        end_tine = datetime.strptime(f"{schedule['endTime'].split(':')[0]}:{schedule['endTime'].split(':')[1]}", "%H:%M")

        parsed_schedules.append(InstanceSchedule(schedule["ID"], start_time, end_tine))
    
    return parsed_schedules

def parse_buildings(buildings):
    if not buildings:
        raise Exception("No buildings in data file")
    
    parsed_buildings = []
    for building in buildings:
        parsed_buildings.append(InstanceBuilding(building['ID'], building['name']))

    return parsed_buildings

def parse_classrooms(classrooms):
    if not classrooms:
        raise Exception("No classrooms in data file")
    
    parsed_classrooms = []
    for classroom in classrooms:
        parsed_classrooms.append(InstanceClassroom(classroom['ID'], classroom['isLab'], classroom['capacity'], classroom['buildingID'], classroom['description'], classroom['floor'], classroom['board'], classroom['projector']) )

    return parsed_classrooms

def parse_professors(professors):
    if not professors:
        raise Exception("No professors in data file")
    
    parsed_professors = []
    for professor in professors:
        parsed_professors.append(InstanceProfessor(professor['code'], professor['name']))

    return parsed_professors

def parse_subjects(subjects):
    if not subjects:
        raise Exception("No subjects in data file")
    
    parsed_subjects = []
    for subject in subjects:
        parsed_subjects.append(InstanceSubject(subject['code'], subject['name']))

    return parsed_subjects

def parse_meetings(meetings):
    if not meetings:
        raise Exception("No meetings in data file")
    
    parsed_meetings = []
    meeting_count = 0
    for meeting in meetings:
        parsed_meetings.append(InstanceMeeting(meeting['isPractical'], meeting['dayOfWeek'], meeting['vacancies'], meeting['demand'], meeting['subjectCode'], meeting['classes'], meeting['schedules'], meeting['professors']))
        parsed_meetings[meeting_count].schedules.sort()
        parsed_meetings[meeting_count].classes.sort()
        meeting_count += 1

    return parsed_meetings

def parse_preferences(preferences):
    if not preferences:
        raise Exception("No preferences in data file")
    
    parsed_preferences = []
    for preference in preferences:
        parsed_preferences.append(InstancePreference(preference['category'], preference['categoryCode'], preference['building'], preference['floor'], preference['board'], preference['projector']))

    return parsed_preferences

def parse_restrictions(restrictions):
    if not restrictions:
        raise Exception("No restrictions in data file")
    
    parsed_restrictions = []
    for restriction in restrictions:
        parsed_restrictions.append(InstanceRestriction(restriction['category'], restriction['categoryCode'], restriction['building'], restriction['floor'], restriction['board'], restriction['projector']))

    return parsed_restrictions

def parse_reservations(reservations):
    if not reservations:
        raise Exception("No reservationsin data file")
    
    parsed_reservations = []
    for reservation in reservations:
        parsed_reservations.append(InstanceReservation(reservation['classroomID'], reservation['dayOfWeek'], reservation['scheduleID']))

    return parsed_reservations
