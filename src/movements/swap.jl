export Swap

mutable struct Swap

    meeting_1::SolutionMeeting
    classroom_1::Classroom
    meeting_2::SolutionMeeting
    classroom_2::Classroom
    objectives::Objectives

    day::Day

    allowed::Bool

    Swap() = new()

end

function startMove(move::Swap, solution::Solution, problem::Problem)
    move.allowed = false

    sizeClassrooms = length(problem.classrooms)
    meetings = solution.meetings
    classrooms = problem.classrooms
    move.objectives = solution.objectives

    local day::Day
    randomDay = rand(2:7)

    if (randomDay == 2)
        move.day = solution.monday
    elseif (randomDay == 3)
        move.day = solution.thursday
    elseif (randomDay == 4)
        move.day = solution.wednesday
    elseif (randomDay == 5)
        move.day = solution.tuesday
    elseif (randomDay == 6)
        move.day = solution.friday
    elseif (randomDay == 7)
        move.day = solution.saturday
    else
    end

    meetingCode_1 = 0
    meetingCount = rand(1:length(move.day.meetings))

    for i = 1:length(move.day.meetings)
        if (move.day.meetings[meetingCount].classroomID != 0)
            meetingCode_1 = move.day.meetings[meetingCount].ID
            break
        end

        if (meetingCount == length(move.day.meetings))
            meetingCount = 1
        else
            meetingCount += 1
        end
    end

    if (meetingCode_1 == 0 || meetings[meetingCode_1].demand == 0)
        return
    end

    meetingCode_2 = 0
    meetingCount = rand(1:length(move.day.meetings))
    for i = 1:length(move.day.meetings)
        if (move.day.meetings[meetingCount].classroomID != 0 && move.day.meetings[meetingCount].schedules == move.day.meetings[meetingCode_1].schedules)
            meetingCode_2 = move.day.meetings[meetingCount].ID
            break
        end

        if (meetingCount == length(move.day.meetings))
            meetingCount = 1
        else
            meetingCount += 1
        end
    end

    if (meetingCode_2 == 0 || meetings[meetingCode_2].demand == 0)
        return
    end

    if (checkRestrictions(meetings[meetingCode_1].restrictions, classrooms[meetings[meetingCode_2].classroomID]) && checkRestrictions(meetings[meetingCode_2].restrictions, classrooms[meetings[meetingCode_1].classroomID]))
        move.meeting_1 = meetings[meetingCode_1]
        move.classroom_1 = classrooms[meetings[meetingCode_1].classroomID]
        move.meeting_2 = meetings[meetingCode_2]
        move.classroom_2 = classrooms[meetings[meetingCode_2].classroomID]
        move.objectives = solution.objectives
        move.allowed = true

        return
    end

end

function doMove(move::Swap)
    
    # creating auxiliar variables to count the objectives
    oldObjectives = Objectives()
    newObjectives = Objectives()
    returnObjectives = deepcopy(move.objectives)

    # calculating the objectives for the two meetings in their original classrooms
    x = calculateAllocationObjective(move.meeting_1, move.classroom_1)
    oldObjectives.idleness += x.idleness
    oldObjectives.deallocated += x.deallocated
    oldObjectives.lessThan10 += x.lessThan10
    oldObjectives.preferences += x.preferences
    x = calculateAllocationObjective(move.meeting_2, move.classroom_2)
    oldObjectives.idleness += x.idleness
    oldObjectives.deallocated += x.deallocated
    oldObjectives.lessThan10 += x.lessThan10
    oldObjectives.preferences += x.preferences
    
    # calculating the objectives for the two meetings swaping their classrooms
    y = calculateAllocationObjective(move.meeting_1, move.classroom_2)
    newObjectives.idleness += y.idleness
    newObjectives.deallocated += y.deallocated
    newObjectives.lessThan10 += y.lessThan10
    newObjectives.preferences += y.preferences
    y = calculateAllocationObjective(move.meeting_2, move.classroom_1)
    newObjectives.idleness += y.idleness
    newObjectives.deallocated += y.deallocated
    newObjectives.lessThan10 += y.lessThan10
    newObjectives.preferences += y.preferences

    # calculating preferences objectives for the two meetings before and after the swap
    if length(move.meeting_1.preferences) > 0
        x = calculatePreferenceObjective(move.meeting_1, move.classroom_1)
        oldObjectives.preferences += x.preferences

        y = calculatePreferenceObjective(move.meeting_1, move.classroom_2)
        newObjectives.preferences += y.preferences
    end

    if length(move.meeting_2.preferences) > 0
        x = calculatePreferenceObjective(move.meeting_2, move.classroom_2)
        oldObjectives.preferences += x.preferences

        y = calculatePreferenceObjective(move.meeting_2, move.classroom_1)
        newObjectives.preferences += y.preferences
    end

    # calculating the resulting value of the objectives
    returnObjectives.idleness += (newObjectives.idleness - oldObjectives.idleness)
    returnObjectives.deallocated += (newObjectives.deallocated - oldObjectives.deallocated)
    returnObjectives.lessThan10 += (newObjectives.lessThan10 - oldObjectives.lessThan10)
    returnObjectives.moreThan10 += (newObjectives.moreThan10 - oldObjectives.moreThan10)
    returnObjectives.preferences += (newObjectives.preferences - oldObjectives.preferences)

    return returnObjectives

end

function acceptMove(move::Swap)

    day::Day = move.day

    schedules = move.meeting_1.schedules

    for i in eachindex(schedules)
        day.matrix[schedules[i].ID, move.classroom_1.ID].meetingID = move.meeting_2.ID
        day.matrix[schedules[i].ID, move.classroom_1.ID].status = 1

        day.matrix[schedules[i].ID, move.classroom_2.ID].meetingID = move.meeting_1.ID
        day.matrix[schedules[i].ID, move.classroom_2.ID].status = 1
    end

    move.meeting_1.classroomID = move.classroom_2.ID
    move.meeting_1.buildingID = move.classroom_2.buildingID

    move.meeting_2.classroomID = move.classroom_1.ID
    move.meeting_2.buildingID = move.classroom_1.buildingID

end