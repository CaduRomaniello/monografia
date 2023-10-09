class InstanceReservation():
    def __init__(self, classroom_id=None, day_of_week=None, schedule_id=None):
        self.classroom_id = classroom_id
        self.day_of_week = day_of_week
        self.schedule_id = schedule_id

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