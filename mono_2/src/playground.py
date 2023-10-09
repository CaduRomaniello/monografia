from classes.instanceReservation import Reservation

class Teste():
    def __init__(self, reservation=None):
        self.reservation = reservation

def createReservation():
    a = Reservation(1, 4, 10)
    return a

def playground():
    r = createReservation()
    t = Teste(r)

    print(t.reservation.day_of_week)
    print(r.day_of_week)

    # t.reservation.day_of_week = 2
    r.day_of_week = 7

    print(t.reservation.day_of_week)
    print(r.day_of_week)
    
playground()