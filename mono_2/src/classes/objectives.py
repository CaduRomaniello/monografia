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