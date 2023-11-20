IDLENESS_WEIGHT = 1
DEALLOCATED_WEIGHT = 1
STANDING_WEIGHT = 1

def solution_cost(objectives):
    return (IDLENESS_WEIGHT * objectives.idleness) + (DEALLOCATED_WEIGHT * objectives.deallocated) + (STANDING_WEIGHT * objectives.standing)