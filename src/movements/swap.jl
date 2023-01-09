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
        if move.day.meetings[meetingCount].ID == meetingCode_1
            continue
        end

        if (move.day.meetings[meetingCount].classroomID != 0 && equalSchedules(move.day.meetings[meetingCount].schedules, meetings[meetingCode_1].schedules))
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
    # println("---------------------------------------------------------")
    
    day::Day = move.day

    schedules = move.meeting_1.schedules
    
    # println("ID encontro 1: $(move.meeting_1.ID), ID sala 1: $(move.classroom_1.ID), Sala alocada: $(move.meeting_1.classroomID)")
    # println("ID encontro 2: $(move.meeting_2.ID), ID sala 2: $(move.classroom_2.ID), Sala alocada: $(move.meeting_2.classroomID)")
    # # println("ID encontro 1: $(move.meeting_1.ID), ID encontro 2: $(move.meeting_2.ID), ID sala 1: $(move.classroom_1.ID), ID sala 2: $(move.classroom_2.ID)")
    # println("Matriz sala 1 antes: $(day.matrix[schedules[1].ID, move.classroom_1.ID].meetingID), Matriz sala 2 antes: $(day.matrix[schedules[1].ID, move.classroom_2.ID].meetingID)")
    
    for i in eachindex(schedules)
        day.matrix[schedules[i].ID, move.classroom_1.ID].meetingID = move.meeting_2.ID
        day.matrix[schedules[i].ID, move.classroom_1.ID].status = 1
        
        day.matrix[schedules[i].ID, move.classroom_2.ID].meetingID = move.meeting_1.ID
        day.matrix[schedules[i].ID, move.classroom_2.ID].status = 1
    end

    # println("Matriz sala 1 depois: $(day.matrix[schedules[1].ID, move.classroom_1.ID].meetingID), Matriz sala 2 depois: $(day.matrix[schedules[1].ID, move.classroom_2.ID].meetingID)")
    
    move.meeting_1.classroomID = move.classroom_2.ID
    move.meeting_1.buildingID = move.classroom_2.buildingID
    
    move.meeting_2.classroomID = move.classroom_1.ID
    move.meeting_2.buildingID = move.classroom_1.buildingID

    # println("ID encontro 1: $(move.meeting_1.ID), ID sala 1: $(move.classroom_1.ID), Sala alocada: $(move.meeting_1.classroomID)")
    # println("ID encontro 2: $(move.meeting_2.ID), ID sala 2: $(move.classroom_2.ID), Sala alocada: $(move.meeting_2.classroomID)")
    # # println("ID encontro 1: $(move.meeting_1.ID), ID encontro 2: $(move.meeting_2.ID), ID sala 1: $(move.classroom_1.ID), ID sala 2: $(move.classroom_2.ID)")

    # println("---------------------------------------------------------")

end

function checkSwap(move::Swap, solution::Solution)
    id_1 = move.meeting_1.ID
    id_2 = move.meeting_2.ID

    pos_1 = 0
    for i in eachindex(move.day.meetings)
        if move.day.meetings[i].ID == id_1
            pos_1 = i
            break
        end
    end
    pos_2 = 0
    for i in eachindex(move.day.meetings)
        if move.day.meetings[i].ID == id_2
            pos_2 = i
            break
        end
    end

    if move.meeting_1.classroomID != move.day.meetings[pos_1].classroomID || move.meeting_1.classroomID != solution.meetings[id_1].classroomID || move.day.meetings[pos_1].classroomID != solution.meetings[id_1].classroomID
        println("ERRO SWAP")
        println(move.meeting_1.classroomID, ", ", move.day.meetings[pos_1].classroomID, ", ", solution.meetings[id_1].classroomID)
        println("========================================================================================================")
    end

    if move.meeting_2.classroomID != move.day.meetings[pos_2].classroomID || move.meeting_2.classroomID != solution.meetings[id_2].classroomID || move.day.meetings[pos_2].classroomID != solution.meetings[id_2].classroomID
        println("ERRO SWAP")
        println(move.meeting_2.classroomID, ", ", move.day.meetings[pos_2].classroomID, ", ", solution.meetings[id_2].classroomID)
        println("========================================================================================================")
    end
end