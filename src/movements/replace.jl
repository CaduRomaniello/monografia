export Replace

mutable struct Replace

    meeting_1::SolutionMeeting # allocated
    meeting_2::SolutionMeeting # deallocated
    classroom::Classroom
    objectives::Objectives

    day::Day

    allowed::Bool

    Replace() = new()

end

function startMove(move::Replace, solution::Solution, problem::Problem)
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

    x = 0
    meetingCode_1 = 0
    meetingCount = rand(1:length(move.day.meetings))

    for i = 1:length(move.day.meetings)
        if (move.day.meetings[meetingCount].classroomID != 0)
            meetingCode_1 = move.day.meetings[meetingCount].ID
            x = meetingCount
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

        if (move.day.meetings[meetingCount].classroomID == 0 && equalSchedules(move.day.meetings[meetingCount].schedules, meetings[meetingCode_1].schedules))
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

    if (checkRestrictions(meetings[meetingCode_2].restrictions, classrooms[meetings[meetingCode_1].classroomID]))
        move.meeting_1 = meetings[meetingCode_1]
        move.meeting_2 = meetings[meetingCode_2]
        move.classroom = classrooms[meetings[meetingCode_1].classroomID]
        move.objectives = solution.objectives
        move.allowed = true

        return
    end

end

function doMove(move::Replace)
    
    # creating auxiliar variables to count the objectives
    oldObjectives = Objectives()
    newObjectives = Objectives()
    returnObjectives = deepcopy(move.objectives)

    # calculating the objectives for the two meetings in their original classrooms
    x = calculateAllocationObjective(move.meeting_1, move.classroom)
    oldObjectives.idleness += x.idleness
    oldObjectives.deallocated += x.deallocated
    oldObjectives.lessThan10 += x.lessThan10
    oldObjectives.preferences += x.preferences
    for i in eachindex(move.meeting_1.professors)
        if length(move.meeting_1.professors[i].classrooms) > 1
            oldObjectives.professors += length(move.meeting_1.professors[i].classrooms) - 1
        end
    end

    oldObjectives.deallocated += move.meeting_2.demand
    oldObjectives.preferences += length(move.meeting_2.preferences)
    for i in eachindex(move.meeting_2.professors)
        if length(move.meeting_2.professors[i].classrooms) > 1
            oldObjectives.professors += length(move.meeting_2.professors[i].classrooms) - 1
        end
    end
    
    # calculating the objectives for the two meetings after replacement
    y = calculateAllocationObjective(move.meeting_2, move.classroom)
    newObjectives.idleness += y.idleness
    newObjectives.deallocated += y.deallocated
    newObjectives.lessThan10 += y.lessThan10
    newObjectives.preferences += y.preferences
    y = calculateProfessorObjective(move.meeting_2, move.classroom)
    newObjectives.professors += y.professors
    
    newObjectives.deallocated += move.meeting_1.demand
    newObjectives.preferences += length(move.meeting_1.preferences)
    y = calculateProfessorObjective(move.meeting_1, move.classroom)
    newObjectives.professors += y.professors

    # calculating preferences objectives for the two meetings before and after the swap
    if length(move.meeting_1.preferences) > 0
        x = calculatePreferenceObjective(move.meeting_1, move.classroom)
        oldObjectives.preferences += x.preferences
    end

    if length(move.meeting_2.preferences) > 0
        y = calculatePreferenceObjective(move.meeting_2, move.classroom)
        newObjectives.preferences += y.preferences
    end

    # calculating the resulting value of the objectives
    returnObjectives.idleness += (newObjectives.idleness - oldObjectives.idleness)
    returnObjectives.deallocated += (newObjectives.deallocated - oldObjectives.deallocated)
    returnObjectives.lessThan10 += (newObjectives.lessThan10 - oldObjectives.lessThan10)
    returnObjectives.moreThan10 += (newObjectives.moreThan10 - oldObjectives.moreThan10)
    returnObjectives.preferences += (newObjectives.preferences - oldObjectives.preferences)
    returnObjectives.professors += (newObjectives.professors - oldObjectives.professors)

    return returnObjectives

end

function acceptMove(move::Replace)

    day::Day = move.day

    schedules = move.meeting_1.schedules

    for i in eachindex(schedules)
        day.matrix[schedules[i].ID, move.classroom.ID].meetingID = move.meeting_2.ID
        day.matrix[schedules[i].ID, move.classroom.ID].status = 1
    end

    move.meeting_1.classroomID = 0
    move.meeting_1.buildingID = 0

    move.meeting_2.classroomID = move.classroom.ID
    move.meeting_2.buildingID = move.classroom.buildingID

    for i in eachindex(move.meeting_1.professors)
        found = false
        position = 0
        for j in eachindex(move.meeting_1.professors[i].classrooms)
            if move.classroom.ID == move.meeting_1.professors[i].classrooms[j].classroomID
                position = j
                found = true
                break
            end
        end

        if found
            if move.meeting_1.professors[i].classrooms[position].quantity > 1
                move.meeting_1.professors[i].classrooms[position].quantity -= 1
            else
                deleteat!(move.meeting_1.professors[i].classrooms, position)
            end
        else
            println("ERRO replace - removing classroom when accepted")
        end
    end

    for i in eachindex(move.meeting_2.professors)
        found = false
        position = 0
        for j in eachindex(move.meeting_2.professors[i].classrooms)
            if move.classroom.ID == move.meeting_2.professors[i].classrooms[j].classroomID
                position = j
                found = true
                break
            end
        end

        if found
            move.meeting_2.professors[i].classrooms[position].quantity += 1
        else
            push!(move.meeting_2.professors[i].classrooms, TaughtClassrooms(move.classroom.ID, 1))
        end
    end

end

function checkReplace(move::Replace, solution::Solution)
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
        println("ERRO REPLACE")
        println(move.meeting_1.classroomID, ", ", move.day.meetings[pos_1].classroomID, ", ", solution.meetings[id_1].classroomID)
        println("========================================================================================================")
    end

    if move.meeting_2.classroomID != move.day.meetings[pos_2].classroomID || move.meeting_2.classroomID != solution.meetings[id_2].classroomID || move.day.meetings[pos_2].classroomID != solution.meetings[id_2].classroomID
        println("ERRO REPLACE")
        println(move.meeting_2.classroomID, ", ", move.day.meetings[pos_2].classroomID, ", ", solution.meetings[id_2].classroomID)
        println("========================================================================================================")
    end
end