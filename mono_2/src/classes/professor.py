class Professor():
    def __init__(self, code=None, name=None, days=None):
        self.code = code
        self.name = name
        self.days = days
    
    def check_availability_and_allocate(self, day_name, schedules, meeting_id):
        available = True
        for schedule in schedules:
            if self.days[day_name][schedule - 1]["occupied"]:
                available = False
                break

        if available:
            self.allocate_meeting_for_professor(day_name, schedules, meeting_id)
        
        return available
    
    def allocate_meeting_for_professor(self, day_name, schedules, meeting_id):
        for schedule in schedules:
            self.days[day_name][schedule - 1]["occupied"] = True
            self.days[day_name][schedule - 1]["meeting_id"] = meeting_id

    def toJSON(self):
        return {
            "code": self.code,
            "name": self.name,
            "days": self.days
        }
