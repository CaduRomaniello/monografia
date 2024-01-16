class Objectives():
    def __init__(self, idleness=0, deallocated=0, standing=0):
        self.idleness = idleness
        self.deallocated = deallocated
        self.standing = standing

    def print(self):
        print('\n====================== Objectives ======================')
        print('Idleness   : ', self.idleness)
        print('Deallocated: ', self.deallocated)
        print('Standing   : ', self.standing)
        print('========================================================')

    def compare(self, other, move, move_response, meetings):
        if self.idleness == other.idleness and self.deallocated == other.deallocated and self.standing == other.standing:
            return True
        else:
            print(move)
            print(move_response)
            meetings[move_response['meeting_1'] - 1].print()
            meetings[move_response['meeting_2'] - 1].print()
            self.print()
            print('--------------------------------------------------')
            other.print()
            print()
            return False
        
    def isEqual(self, other):
        if self.idleness == other.idleness and self.deallocated == other.deallocated and self.standing == other.standing:
            return True
        else:
            return False
        
    def toJSON(self):
        return {
            'idleness': self.idleness,
            'deallocated': self.deallocated,
            'standing': self.standing
        }
    
    def dominates(self, other):
        if self.idleness <= other.idleness and self.deallocated <= other.deallocated and self.standing <= other.standing:
            if self.idleness < other.idleness or self.deallocated < other.deallocated or self.standing < other.standing:
                return True
            else:
                return False
        else:
            return False