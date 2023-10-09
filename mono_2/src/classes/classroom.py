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
        self.days[day_name][schedule - 1]['is_reservation'] = True