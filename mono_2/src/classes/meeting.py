class Meeting():
    def __init__(self, is_practical=None, day_of_week=None, vacancies=None, demand=None, subject_code=None, classes=None, schedules=None, id=None, professors=None, classroom_id=None, preferences=None, relatives_id=None):
        self.is_practical = is_practical
        self.day_of_week = day_of_week
        self.vacancies = vacancies
        self.demand = demand
        self.subject_code = subject_code
        self.classes = classes
        self.schedules = schedules
        self.id = id
        self.professors = professors
        self.classroom_id = classroom_id
        self.preferences = preferences
        self.relatives_id = relatives_id

    def print(self):
        print('\n====================== Meeting ======================')
        print('Id          : ', self.id)
        print('Self        : ', self)
        print('Is practical: ', self.is_practical)
        print('Day of week : ', self.day_of_week)
        print('Vacancies   : ', self.vacancies)
        print('Demand      : ', self.demand)
        print('Subject code: ', self.subject_code)
        print('Classes     : ', self.classes)
        print('schedules   : ', self.schedules)
        print('Classroom id: ', self.classroom_id)
        print('Relatives id: ', self.relatives_id)
        print('=======================================================')

    def day_name(self):
        if self.day_of_week == 2:
            return 'monday'
        elif self.day_of_week == 3:
            return 'thursday'
        elif self.day_of_week == 4:
            return 'wednesday'
        elif self.day_of_week == 5:
            return 'tuesday'
        elif self.day_of_week == 6:
            return 'friday'
        elif self.day_of_week == 7:
            return 'saturday'
        else:
            raise Exception(f'Day of week has as invalid value. It must be a number between [2, 6] but it has value = {self.day_of_week}.')