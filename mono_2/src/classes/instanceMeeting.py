class InstanceMeeting():
    def __init__(self, is_practical=None, day_of_week=None, vacancies=None, demand=None, subject_code=None, classes=None, schedules=None, professors=None):
        self.is_practical = is_practical
        self.day_of_week = day_of_week
        self.vacancies = vacancies
        self.demand = demand
        self.subject_code = subject_code
        self.classes = classes
        self.schedules = schedules
        self.professors = professors