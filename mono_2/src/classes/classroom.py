class Classroom():
    def __init__(self, id=None, is_lab=None, capacity=None, building_id=None, description=None, floor=None, board=None, projector=None, days=None):
        self.id = id
        self.is_lab = is_lab
        self.capacity = capacity
        self.building_id = building_id
        self.description = description
        self.floor = floor
        self.board = board
        self.projector = projector
        self.days = days

    def allocate_reservation(self, schedule, day_name):
        self.days[day_name][schedule - 1]['occupied'] = True
        self.days[day_name][schedule - 1]['meeting_id'] = None
        self.days[day_name][schedule - 1]['is_reservation'] = True

    def check_availability(self, schedules, day_name):
        for s in schedules:
            if self.days[day_name][s - 1]['occupied'] or self.days[day_name][s - 1]['is_reservation']:
                return False
        return True
    
    def allocate_meeting(self, meeting_id, schedules, day_name):
        can_allocate = self.check_availability(schedules, day_name)

        if not can_allocate:
            return False

        for s in schedules:
            self.days[day_name][s - 1]['occupied'] = True
            self.days[day_name][s - 1]['meeting_id'] = meeting_id
            self.days[day_name][s - 1]['is_reservation'] = False

        return True
    
    def deallocate_meeting(self, meeting_id, schedules, day_name):
        for s in schedules:
            if self.days[day_name][s - 1]['meeting_id'] != meeting_id:
                raise Exception("Meeting ID does not match in classroom deallocation")
            
            self.days[day_name][s - 1]['occupied'] = False
            self.days[day_name][s - 1]['meeting_id'] = None
            self.days[day_name][s - 1]['is_reservation'] = False

    def toJSON(self):
        return {
            'id': self.id,
            'is_lab': self.is_lab,
            'capacity': self.capacity,
            'building_id': self.building_id,
            'description': self.description,
            'floor': self.floor,
            'board': self.board,
            'projector': self.projector,
            # 'days': self.days
        }