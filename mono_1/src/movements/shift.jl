export Shift

mutable struct Shift

    meeting::SolutionMeeting
    classroom_origin::Classroom
    classroom_destination::Classroom
    objectives::Objectives

    day::Day

    allowed::Bool

    Shift() = new()

end

function startMove(move::Shift, solution::Solution, problem::Problem)
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

    meetingCode = 0
    meetingCount = rand(1:length(move.day.meetings))

    for i = 1:length(move.day.meetings)
        if (move.day.meetings[meetingCount].classroomID != 0)
            meetingCode = move.day.meetings[meetingCount].ID
            break
        end

        if (meetingCount == length(move.day.meetings))
            meetingCount = 1
        else
            meetingCount += 1
        end
    end

    if (meetingCode == 0 || meetings[meetingCode].demand == 0)
        return
    end

    classroomCount = rand(1:sizeClassrooms)

    for i = 1:sizeClassrooms
        if (verifyClassroomAvailability(move.day, classrooms[classroomCount].ID, meetings[meetingCode].schedules))
            if (checkRestrictions(meetings[meetingCode].restrictions, classrooms[classroomCount]))
                move.meeting = meetings[meetingCode]
                move.classroom_origin = classrooms[meetings[meetingCode].classroomID]
                move.classroom_destination = classrooms[classroomCount]
                move.objectives = solution.objectives
                move.allowed = true
    
                return
            end
        end

        if (classroomCount == sizeClassrooms)
            classroomCount = 1
        else
            classroomCount += 1
        end
    end
end

function doMove(move::Shift)
    
    # creating auxiliar variables to count the objectives
    oldObjectives = Objectives()
    newObjectives = Objectives()
    returnObjectives = deepcopy(move.objectives)

    # calculating the objectives when the meeting is allocated in the original classroom
    x = calculateAllocationObjective(move.meeting, move.classroom_origin)
    oldObjectives.idleness += x.idleness
    oldObjectives.deallocated += x.deallocated
    oldObjectives.lessThan10 += x.lessThan10
    oldObjectives.moreThan10 += x.moreThan10
    oldObjectives.preferences += x.preferences
    for i in eachindex(move.meeting.professors)
        if length(move.meeting.professors[i].classrooms) > 1
            oldObjectives.professors += length(move.meeting.professors[i].classrooms) - 1
        end
    end
    
    # calculating the objectives when the meeting is shifted to the new classroom
    y = calculateAllocationObjective(move.meeting, move.classroom_destination)
    newObjectives.idleness += y.idleness
    newObjectives.deallocated += y.deallocated
    newObjectives.lessThan10 += y.lessThan10
    newObjectives.moreThan10 += y.moreThan10
    newObjectives.preferences += y.preferences
    y = calculateProfessorObjective(move.meeting, move.classroom_destination)
    newObjectives.professors += y.professors

    # calculating preferences objectives if the meeting has preferences
    if length(move.meeting.preferences) > 0
        x = calculatePreferenceObjective(move.meeting, move.classroom_origin)
        oldObjectives.preferences += x.preferences

        y = calculatePreferenceObjective(move.meeting, move.classroom_destination)
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

function acceptMove(move::Shift)

    day::Day = move.day

    schedules = move.meeting.schedules

    for i in eachindex(schedules)
        day.matrix[schedules[i].ID, move.classroom_origin.ID].meetingID = 0
        day.matrix[schedules[i].ID, move.classroom_origin.ID].status = 0
        
        day.matrix[schedules[i].ID, move.classroom_destination.ID].meetingID = move.meeting.ID
        day.matrix[schedules[i].ID, move.classroom_destination.ID].status = 1
    end
    
    move.meeting.classroomID = move.classroom_destination.ID
    move.meeting.buildingID = move.classroom_destination.buildingID

    # removing classroom from professor
    for i in eachindex(move.meeting.professors)
        found = false
        position = 0
        for j in eachindex(move.meeting.professors[i].classrooms)
            if move.classroom_origin.ID == move.meeting.professors[i].classrooms[j].classroomID
                position = j
                found = true
                break
            end
        end

        if found
            if move.meeting.professors[i].classrooms[position].quantity > 1
                move.meeting.professors[i].classrooms[position].quantity -= 1
            else
                deleteat!(move.meeting.professors[i].classrooms, position)
            end
        else
            println("ERRO shift - removing classroom when accepted")
        end
    end

    # adding classroom to professor
    for i in eachindex(move.meeting.professors)
        found = false
        position = 0
        for j in eachindex(move.meeting.professors[i].classrooms)
            if move.classroom_destination.ID == move.meeting.professors[i].classrooms[j].classroomID
                position = j
                found = true
                break
            end
        end

        if found
            move.meeting.professors[i].classrooms[position].quantity += 1
        else
            push!(move.meeting.professors[i].classrooms, TaughtClassrooms(move.classroom_destination.ID, 1))
        end
    end

end

function checkShift(move::Shift, solution::Solution)
    # println(move.classroom_origin.ID, ", ", move.classroom_destination.ID, ", ", move.meeting.classroomID)
    id = move.meeting.ID

    pos = 0
    for i in eachindex(move.day.meetings)
        if move.day.meetings[i].ID == id
            pos = i
            break
        end
    end

    if move.meeting.classroomID != move.day.meetings[pos].classroomID || move.meeting.classroomID != solution.meetings[id].classroomID || move.day.meetings[pos].classroomID != solution.meetings[id].classroomID
        println("ERRO SHIFT")
        println(move.meeting.classroomID, ", ", move.day.meetings[pos].classroomID, ", ", solution.meetings[id].classroomID)
        println("========================================================================================================")
    end
end