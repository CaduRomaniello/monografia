# include("../movements/allocate.jl")

"""
Get a string in the format hh:mm and converts it to a variable of Time type
"""
function stringToTime(timeString::String)
    
    aux = split(timeString, ':')
    hours = parse(Int, aux[1])
    minutes = parse(Int, aux[2])

    time = DateTime(2022, 1, 1, hours, minutes, 0)
    return Time(time)

end

"""
Initialize the variables that represent an entire day
"""
function createDay(dayOfWeek, schedulesSize, classroomsSize)

    day = ""
    if (dayOfWeek == 2)
        day = "Monday"
    elseif (dayOfWeek == 3)
        day = "Thursday"
    elseif (dayOfWeek == 4)
        day = "Wednesday"
    elseif (dayOfWeek == 5)
        day = "Tuesday"
    elseif (dayOfWeek == 6)
        day = "Friday"
    elseif (dayOfWeek == 7)
        day = "Saturday"
    else
    end

    matrix = Array{Cell, 2}(undef, schedulesSize, classroomsSize)
    for i = 1:schedulesSize
        for j = 1:classroomsSize
            aux = Cell(0, 0)
            matrix[i, j] = deepcopy(aux)
        end
    end
    return Day(day, dayOfWeek, [], matrix)

end

"""
Allocating the reservations
"""
function allocateReservations(reservations::Array{Reservation, 1}, monday::Day, thursday::Day, wednesday::Day, tuesday::Day, friday::Day, saturday::Day)

    for i in eachindex(reservations)

        if (reservations[i].dayOfWeek == 2)
            monday.matrix[reservations[i].scheduleID, reservations[i].classroomID].status = 2
        elseif (reservations[i].dayOfWeek == 3)
            thursday.matrix[reservations[i].scheduleID, reservations[i].classroomID].status = 2
        elseif (reservations[i].dayOfWeek == 4)
            wednesday.matrix[reservations[i].scheduleID, reservations[i].classroomID].status = 2
        elseif (reservations[i].dayOfWeek == 5)
            tuesday.matrix[reservations[i].scheduleID, reservations[i].classroomID].status = 2
        elseif (reservations[i].dayOfWeek == 6)
            friday.matrix[reservations[i].scheduleID, reservations[i].classroomID].status = 2
        elseif (reservations[i].dayOfWeek == 7)
            saturday.matrix[reservations[i].scheduleID, reservations[i].classroomID].status = 2
        else
        end

    end

end

"""
Creating the meetings that will be in the Solution variable using the instance meetings
"""
function createSolutionMeetings(problem::Problem)
    
    x = Array{SolutionMeeting, 1}()

    for i in eachindex(problem.meetings)

        # push to SolutionMeeting Array
        push!(x, SolutionMeeting(i, problem.meetings[i].isPractical, problem.meetings[i].dayOfWeek, problem.meetings[i].subjectCode, problem.meetings[i].classesCodes, [], 0, 0, [], "", 0, 0, [], []))

        # push each schedule into SolutionMeeting
        for j in eachindex(problem.meetings[i].schedules)
            push!(x[i].schedules, problem.schedules[problem.meetings[i].schedules[j]])
        end

        # finding all the classes that this meeting have
        for j in eachindex(problem.meetings[i].classesCodes)
            meetingCode = string(problem.meetings[i].subjectCode, "-", problem.meetings[i].classesCodes[j])
            for k in eachindex(problem.classes)
                classCode = string(problem.classes[k].subjectCode, "-", problem.classes[k].classCode)

                if meetingCode == classCode
                    # println(meetingCode, " / ", classCode)
                    x[i].vacancies += problem.classes[k].vacancies
                    x[i].demand += problem.classes[k].demand

                    # finding all professors for this meeting
                    for m in eachindex(problem.classes[k].professors)
                        for n in eachindex(problem.professors)
                            if problem.classes[k].professors[m] == problem.professors[n].code
                                push!(x[i].professors, problem.professors[n])

                                # finding all professor preferences for this meeting
                                for t in eachindex(problem.preferences)
                                    if problem.professors[n].code == problem.preferences[t].categoryCode
                                        push!(x[i].preferences, problem.preferences[t])
                                        break
                                    end
                                end
                    
                                # finding all professor restrictions for this meeting
                                for t in eachindex(problem.restrictions)
                                    if problem.professors[n].code == problem.restrictions[t].categoryCode
                                        push!(x[i].restrictions, problem.restrictions[t])
                                        break
                                    end
                                end

                                break
                            end
                        end
                    end
                    
                    break
                end
            end

            # finding all class preferences for this meeting
            for k in eachindex(problem.preferences)
                if meetingCode == problem.preferences[k].categoryCode
                    push!(x[i].preferences, problem.preferences[k])
                    break
                end
            end

            # finding all class restrictions for this meeting
            for k in eachindex(problem.restrictions)
                if meetingCode == problem.restrictions[k].categoryCode
                    push!(x[i].restrictions, problem.restrictions[k])
                    break
                end
            end
        end

    end

    return x

end

"""
Calculating initial objectives values with all meetings deallocated
"""
function initialObjectives(solution::Solution)
    for i in eachindex(solution.meetings)
        solution.objectives.deallocated += solution.meetings[i].demand
        if length(solution.meetings[i].preferences) > 0
            solution.objectives.preferences += length(solution.meetings[i].preferences)
        end
    end
end

"""
Verify if classroom is available for a specific time
"""
function verifyClassroomAvailability(day::Day, classroomID::Int64, schedules::Array)
    for i in eachindex(schedules)
        if (day.matrix[schedules[i].ID, classroomID].status != 0)
            return false
        end
    end
    return true
end

"""
Verify if classroom attends meeting restrictions
"""
function checkRestrictions(restrictions::Array{Restriction, 1}, classroom::Classroom)
    for i in eachindex(restrictions)
        if (restrictions[i].building !== nothing)
            if (restrictions[i].building != classroom.buildingID)
                return false
            end
        end
        if (restrictions[i].floor !== nothing)
            if (restrictions[i].floor != classroom.floor)
                return false
            end
        end
        if (restrictions[i].board !== nothing)
            if (restrictions[i].board != classroom.board)
                return false
            end
        end
        if (restrictions[i].projector !== nothing)
            if (restrictions[i].projector != classroom.projector)
                return false
            end
        end
    end
    return true
end

"""
Calculate objectives related to meeting demand and classroom capacity for specific meeting  in specific classroom
"""
function calculateAllocationObjective(meeting::SolutionMeeting, classroom::Classroom)

    x = Objectives()

    demand = meeting.demand
    capacity = classroom.capacity

    if demand <= capacity
        if (capacity - demand) > round(capacity / 2, RoundDown)
            x.idleness += (capacity - demand) - round(capacity / 2, RoundDown)
        end
    else
        notAttended = demand - capacity
        percentage = (demand * 10) / 100
        percentage = round(percentage, RoundDown)
        if (notAttended <= percentage)
            x.lessThan10 += notAttended
        else
            x.lessThan10 += percentage
            x.moreThan10 += notAttended - percentage
        end
    end

    return x

end

"""
Calculate preference objective for specific meeting  in specific classroom
"""
function calculatePreferenceObjective(meeting::SolutionMeeting, classroom::Classroom)
    x = Objectives()
    if (classroom.ID != 0)
        for i in eachindex(meeting.preferences)
            if (meeting.preferences[i].building !== nothing)
                if (meeting.preferences[i].building != classroom.buildingID)
                    x.preferences += 1
                else
                    if x.preferences > 0
                        x.preferences -= 1
                    end
                end
            end
            if (meeting.preferences[i].floor !== nothing)
                if (meeting.preferences[i].floor != classroom.floor)
                    x.preferences += 1
                else
                    if x.preferences > 0
                        x.preferences -= 1
                    end
                end
            end
            if (meeting.preferences[i].board !== nothing)
                if (meeting.preferences[i].board != classroom.board)
                    x.preferences += 1
                else
                    if x.preferences > 0
                        x.preferences -= 1
                    end
                end
            end
            if (meeting.preferences[i].projector !== nothing)
                if (meeting.preferences[i].projector != classroom.projector)
                    x.preferences += 1
                else
                    if x.preferences > 0
                        x.preferences -= 1
                    end
                end
            end
        end
        return x
    else
        for i in eachindex(meeting.preferences)
            if (meeting.preferences[i].building !== nothing)
                x.preferences += 1
            end
            if (meeting.preferences[i].floor !== nothing)
                x.preferences += 1
            end
            if (meeting.preferences[i].board !== nothing)
                x.preferences += 1
            end
            if (meeting.preferences[i].projector !== nothing)
                x.preferences += 1
            end
        end
        return x
    end
end

"""
Calculate preference related to professors changing classrooms during the week
"""
function calculateProfessorObjective(meeting::SolutionMeeting, classroom::Classroom)
    x = Objectives()

    type = ""
    if meeting.classroomID == 0
        type = "allocate"
    else
        if meeting.classroomID == classroom.ID
            type = "deallocate"
        else
            type = "shift"
        end
    end

    # println(" - $type")

    if type == "allocate"
        for i in eachindex(meeting.professors)
            found = false
            position = 0
            for j in eachindex(meeting.professors[i].classrooms)
                if classroom.ID == meeting.professors[i].classrooms[j].classroomID
                    position = j
                    found = true
                    break
                end
            end
    
            if found
                x.professors += length(meeting.professors[i].classrooms) - 1
            else
                if length(meeting.professors[i].classrooms) > 0
                    x.professors += length(meeting.professors[i].classrooms)
                end
            end
        end
    elseif type == "deallocate"
        for i in eachindex(meeting.professors)
            found = false
            position = 0
            for j in eachindex(meeting.professors[i].classrooms)
                if classroom.ID == meeting.professors[i].classrooms[j].classroomID
                    position = j
                    found = true
                    break
                end
            end
    
            if found
                if meeting.professors[i].classrooms[position].quantity > 1
                    x.professors += length(meeting.professors[i].classrooms) - 1
                else
                    if length(meeting.professors[i].classrooms) > 2
                        x.professors += length(meeting.professors[i].classrooms) - 2
                    end
                end
            else
                println("ERROR: calculateProfessorObjective function - deallocate type can't find classroom in meeting's professors")
                exit(0)
            end
        end
    elseif type == "shift"
        for i in eachindex(meeting.professors)
            found_1 = false
            found_2 = false
            position_1 = 0
            position_2 = 0
            for j in eachindex(meeting.professors[i].classrooms)
                if meeting.classroomID == meeting.professors[i].classrooms[j].classroomID
                    position_1 = j
                    found_1 = true
                    break
                end
            end
            for j in eachindex(meeting.professors[i].classrooms)
                if classroom.ID == meeting.professors[i].classrooms[j].classroomID
                    position_2 = j
                    found_2 = true
                    break
                end
            end
    
            if !found_1
                println("ERROR: calculateProfessorObjective function - shift type can't find original classroom in meeting's professors")
                exit(0)
            end

            total = length(meeting.professors[i].classrooms)

            if meeting.professors[i].classrooms[position_1].quantity == 1
                if total > 0
                    total -= 1
                end
            end

            if !found_2
                total += 1
            end

            if total > 1
                x.professors += total - 1
            end
        end
    else
        println("ERROR: calculateProfessorObjective function - invalid type")
        exit(0)
    end

    return x
end

"""
Checks if meetings are correctly allocated in a classroom
"""
function checkAllocation(solution::Solution)
    for i in eachindex(solution.meetings)
        for j in eachindex(solution.meetings[i].schedules)
            classroomID = solution.meetings[i].classroomID
            if classroomID == 0
                continue
            end

            if solution.meetings[i].dayOfWeek == 2
                if solution.monday.matrix[solution.meetings[i].schedules[j].ID, classroomID].meetingID != solution.meetings[i].ID
                    println("Meeting with ID $(solution.meetings[i].ID) is allocated in the classroom with ID $(classroomID) but it isn't allocated in the monday solution matrix!")
                    exit(1)
                end
            elseif solution.meetings[i].dayOfWeek == 3
                if solution.thursday.matrix[solution.meetings[i].schedules[j].ID, classroomID].meetingID != solution.meetings[i].ID
                    println("Meeting with ID $(solution.meetings[i].ID) is allocated in the classroom with ID $(classroomID) but it isn't allocated in the thursday solution matrix!")
                    exit(1)
                end
            elseif solution.meetings[i].dayOfWeek == 4
                if solution.wednesday.matrix[solution.meetings[i].schedules[j].ID, classroomID].meetingID != solution.meetings[i].ID
                    println("Meeting with ID $(solution.meetings[i].ID) is allocated in the classroom with ID $(classroomID) but it isn't allocated in the wednesday solution matrix!")
                    exit(1)
                end
            elseif solution.meetings[i].dayOfWeek == 5
                if solution.tuesday.matrix[solution.meetings[i].schedules[j].ID, classroomID].meetingID != solution.meetings[i].ID
                    println("Meeting with ID $(solution.meetings[i].ID) is allocated in the classroom with ID $(classroomID) but it isn't allocated in the tuesday solution matrix!")
                    exit(1)
                end
            elseif solution.meetings[i].dayOfWeek == 6
                if solution.friday.matrix[solution.meetings[i].schedules[j].ID, classroomID].meetingID != solution.meetings[i].ID
                    println("Meeting with ID $(solution.meetings[i].ID) is allocated in the classroom with ID $(classroomID) but it isn't allocated in the friday solution matrix!")
                    exit(1)
                end
            elseif solution.meetings[i].dayOfWeek == 7
                if solution.saturday.matrix[solution.meetings[i].schedules[j].ID, classroomID].meetingID != solution.meetings[i].ID
                    println("Meeting with ID $(solution.meetings[i].ID) is allocated in the classroom with ID $(classroomID) but it isn't allocated in the saturday solution matrix!")
                    exit(1)
                end
            else
            end
        end
    end

    # monday check
    for row in eachrow(solution.monday.matrix)
        for col in eachindex(row)
            if row[col].meetingID != 0
                if row[col].meetingID != solution.meetings[row[col].meetingID].ID
                    println("ERROR: meetings ID's doesn't match!")
                    exit(1)
                end
                allocation = solution.meetings[row[col].meetingID].classroomID
                if allocation != col
                    println("Meeting with ID $(row[col].meetingID) is allocated in monday solution matrix at classroom $(col) but is registered at classroom with ID $(allocation)!")
                    exit(1)
                end
            end
        end
    end

    # thursday check
    for row in eachrow(solution.thursday.matrix)
        for col in eachindex(row)
            if row[col].meetingID != 0
                if row[col].meetingID != solution.meetings[row[col].meetingID].ID
                    println("ERROR: meetings ID's doesn't match!")
                    exit(1)
                end
                allocation = solution.meetings[row[col].meetingID].classroomID
                if allocation != col
                    println("Meeting with ID $(row[col].meetingID) is allocated in thursday solution matrix at classroom $(col) but is registered at classroom with ID $(allocation)!")
                    exit(1)
                end
            end
        end
    end

    # wednesday check
    for row in eachrow(solution.wednesday.matrix)
        for col in eachindex(row)
            if row[col].meetingID != 0
                if row[col].meetingID != solution.meetings[row[col].meetingID].ID
                    println("ERROR: meetings ID's doesn't match!")
                    exit(1)
                end
                allocation = solution.meetings[row[col].meetingID].classroomID
                if allocation != col
                    println("Meeting with ID $(row[col].meetingID) is allocated in wednesday solution matrix at classroom $(col) but is registered at classroom with ID $(allocation)!")
                    exit(1)
                end
            end
        end
    end

    # tuesday check
    for row in eachrow(solution.tuesday.matrix)
        for col in eachindex(row)
            if row[col].meetingID != 0
                if row[col].meetingID != solution.meetings[row[col].meetingID].ID
                    println("ERROR: meetings ID's doesn't match!")
                    exit(1)
                end
                allocation = solution.meetings[row[col].meetingID].classroomID
                if allocation != col
                    println("Meeting with ID $(row[col].meetingID) is allocated in tuesday solution matrix at classroom $(col) but is registered at classroom with ID $(allocation)!")
                    exit(1)
                end
            end
        end
    end

    # friday check
    for row in eachrow(solution.friday.matrix)
        for col in eachindex(row)
            if row[col].meetingID != 0
                if row[col].meetingID != solution.meetings[row[col].meetingID].ID
                    println("ERROR: meetings ID's doesn't match!")
                    exit(1)
                end
                allocation = solution.meetings[row[col].meetingID].classroomID
                if allocation != col
                    println("Meeting with ID $(row[col].meetingID) is allocated in friday solution matrix at classroom $(col) but is registered at classroom with ID $(allocation)!")
                    exit(1)
                end
            end
        end
    end

    # saturday check
    for row in eachrow(solution.saturday.matrix)
        for col in eachindex(row)
            if row[col].meetingID != 0
                if row[col].meetingID != solution.meetings[row[col].meetingID].ID
                    println("ERROR: meetings ID's doesn't match!")
                    exit(1)
                end
                allocation = solution.meetings[row[col].meetingID].classroomID
                if allocation != col
                    println("Meeting with ID $(row[col].meetingID) is allocated in saturday solution matrix at classroom $(col) but is registered at classroom with ID $(allocation)!")
                    exit(1)
                end
            end
        end
    end
end

"""
Print objectives in the terminal
"""
function printObjectives(objectives::Objectives)
    println("========================================================================")
    println("OBJECTIVES")
    println()
    println("- Deallocated  : $(objectives.deallocated)")
    println("- Idleness     : $(objectives.idleness)")
    println("- Less than 10%: $(objectives.lessThan10)")
    println("- More than 10%: $(objectives.moreThan10)")
    println("- Preferences  : $(objectives.preferences)")
    println("========================================================================")
end

"""
Test allocate movement. This function uses specific meetings from the fixed.json instance. It may not work with other instances
"""
function testAllocateMove(solution, problem)
    allocate = Allocate()

    println("--------------------------------------------------------------------------")
    printObjectives(solution.objectives)
    allocate.allowed = false
    allocate.classroom = problem.classrooms[1]
    allocate.day = solution.thursday
    allocate.meeting = solution.meetings[1]
    allocate.objectives = solution.objectives
    returnAllocate = doMove(allocate)
    acceptMove(allocate)
    solution.objectives = deepcopy(returnAllocate)
    
    println("- Meeting demand    : $(solution.meetings[1].demand)")
    println("- Classroom capacity: $(problem.classrooms[1].capacity)")
    
    println()
    printObjectives(solution.objectives)
    println("--------------------------------------------------------------------------")
end

"""
Test deallocate movement. This function uses specific meetings from the fixed.json instance. It may not work with other instances
"""
function testDeallocateMove(solution, problem)
    allocate = Allocate()
    deallocate = Deallocate()

    println("--------------------------------------------------------------------------")
    printObjectives(solution.objectives)
    allocate.allowed = false
    allocate.classroom = problem.classrooms[1]
    allocate.day = solution.thursday
    allocate.meeting = solution.meetings[1]
    allocate.objectives = solution.objectives
    returnAllocate = doMove(allocate)
    acceptMove(allocate)
    solution.objectives = deepcopy(returnAllocate)
    
    println("- Meeting demand    : $(solution.meetings[1].demand)")
    println("- Classroom capacity: $(problem.classrooms[1].capacity)")
    
    println()
    printObjectives(solution.objectives)

    deallocate.allowed = false
    deallocate.classroom = problem.classrooms[1]
    deallocate.day = solution.thursday
    deallocate.meeting = solution.meetings[1]
    deallocate.objectives = solution.objectives
    returnDeallocate = doMove(deallocate)
    acceptMove(deallocate)
    solution.objectives = deepcopy(returnDeallocate)

    println("- Meeting demand    : $(solution.meetings[1].demand)")
    println("- Classroom capacity: $(problem.classrooms[1].capacity)")

    println()
    printObjectives(solution.objectives)
    println("--------------------------------------------------------------------------")
end

"""
Test replace movement. This function uses specific meetings from the fixed.json instance. It may not work with other instances
"""
function testReplaceMove(solution, problem)
    allocate = Allocate()
    replace = Replace()

    println("--------------------------------------------------------------------------")
    printObjectives(solution.objectives)
    allocate.allowed = false
    allocate.classroom = problem.classrooms[1]
    allocate.day = solution.thursday
    allocate.meeting = solution.meetings[1]
    allocate.objectives = solution.objectives
    returnAllocate = doMove(allocate)
    acceptMove(allocate)
    solution.objectives = deepcopy(returnAllocate)
    
    println("- Meeting demand    : $(solution.meetings[1].demand)")
    println("- Classroom capacity: $(problem.classrooms[1].capacity)")
    
    println()
    printObjectives(solution.objectives)

    replace.allowed = false
    replace.classroom = problem.classrooms[1]
    replace.day = solution.thursday
    replace.meeting_1 = solution.meetings[1]
    replace.meeting_2 = solution.meetings[23]
    replace.objectives = solution.objectives
    returnReplace = doMove(replace)
    acceptMove(replace)
    solution.objectives = deepcopy(returnReplace)

    println("- Meeting 1 demand    : $(solution.meetings[1].demand)")
    println("- Meeting 2 demand    : $(solution.meetings[23].demand)")
    println("- Classroom capacity  : $(problem.classrooms[1].capacity)")

    println()
    printObjectives(solution.objectives)
    println("--------------------------------------------------------------------------")
end

"""
Test shift movement. This function uses specific meetings from the fixed.json instance. It may not work with other instances
"""
function testShiftMove(solution, problem)
    allocate = Allocate()
    shift = Shift()

    println("--------------------------------------------------------------------------")
    printObjectives(solution.objectives)
    allocate.allowed = false
    allocate.classroom = problem.classrooms[1]
    allocate.day = solution.thursday
    allocate.meeting = solution.meetings[1]
    allocate.objectives = solution.objectives
    returnAllocate = doMove(allocate)
    acceptMove(allocate)
    solution.objectives = deepcopy(returnAllocate)
    
    println("- Meeting demand    : $(solution.meetings[1].demand)")
    println("- Classroom capacity: $(problem.classrooms[1].capacity)")
    
    println()
    printObjectives(solution.objectives)

    shift.allowed = false
    shift.classroom_destination = problem.classrooms[11]
    shift.classroom_origin = problem.classrooms[1]
    shift.day = solution.thursday
    shift.meeting = solution.meetings[1]
    shift.objectives = solution.objectives
    returnShift = doMove(shift)
    acceptMove(shift)
    solution.objectives = deepcopy(returnShift)

    println("- Meeting demand        : $(solution.meetings[1].demand)")
    println("- Classroom 1 capacity  : $(problem.classrooms[1].capacity)")
    println("- Classroom 2 capacity  : $(problem.classrooms[11].capacity)")

    # id = shift.meeting.ID
    # pos = 0
    # for i in eachindex(shift.day.meetings)
    #     if shift.day.meetings[i].ID == id
    #         pos = i
    #         break
    #     end
    # end

    # s = shift.meeting.schedules
    # println("MOVE: $(shift.meeting.classroomID)")
    # println("MOVE.DAY: $(shift.day.meetings[pos].classroomID)")
    # println("SOLUTION.MEETINGS: $(solution.meetings[id].classroomID)")

    println()
    printObjectives(solution.objectives)
    println("--------------------------------------------------------------------------")
end

"""
Test swap movement. This function uses specific meetings from the fixed.json instance. It may not work with other instances
"""
function testSwapMove(solution, problem)
    allocate = Allocate()
    swap = Swap()

    println("--------------------------------------------------------------------------")
    printObjectives(solution.objectives)
    allocate.allowed = false
    allocate.classroom = problem.classrooms[1]
    allocate.day = solution.thursday
    allocate.meeting = solution.meetings[1]
    allocate.objectives = solution.objectives
    returnAllocate = doMove(allocate)
    acceptMove(allocate)
    solution.objectives = deepcopy(returnAllocate)
    
    println("- Meeting demand    : $(solution.meetings[1].demand)")
    println("- Classroom capacity: $(problem.classrooms[1].capacity)")
    
    println()
    printObjectives(solution.objectives)

    allocate.allowed = false
    allocate.classroom = problem.classrooms[11]
    allocate.day = solution.thursday
    allocate.meeting = solution.meetings[23]
    allocate.objectives = solution.objectives
    returnAllocate = doMove(allocate)
    acceptMove(allocate)
    solution.objectives = deepcopy(returnAllocate)

    println("- Meeting demand    : $(solution.meetings[23].demand)")
    println("- Classroom capacity: $(problem.classrooms[11].capacity)")
    
    println()
    printObjectives(solution.objectives)

    swap.allowed = false
    swap.classroom_1 = problem.classrooms[1]
    swap.classroom_2 = problem.classrooms[11]
    swap.day = solution.thursday
    swap.meeting_1 = solution.meetings[1]
    swap.meeting_2 = solution.meetings[23]
    swap.objectives = solution.objectives
    returnSwap = doMove(swap)
    acceptMove(swap)
    solution.objectives = deepcopy(returnSwap)

    println("- Meeting 1 demand      : $(solution.meetings[1].demand)")
    println("- Meeting 2 demand      : $(solution.meetings[23].demand)")
    println("- Classroom 1 capacity  : $(problem.classrooms[1].capacity)")
    println("- Classroom 2 capacity  : $(problem.classrooms[11].capacity)")

    println()
    printObjectives(solution.objectives)
    println("--------------------------------------------------------------------------")
end

"""
Calculate solution value
"""
function calculateSolutionValue(objectives::Objectives)
    return (objectives.idleness * 1) + (objectives.deallocated * 1) + (objectives.lessThan10 * 1) + (objectives.moreThan10 * 1) + (objectives.preferences * 1) + (objectives.professors * 1)
end

"""
Copy one Objectives variable into another
"""
function copyObjectives(source::Objectives, destiny::Objectives)
    destiny.deallocated = source.deallocated
    destiny.idleness = source.idleness
    destiny.lessThan10 = source.lessThan10
    destiny.moreThan10 = source.moreThan10
    destiny.preferences = source.preferences
    destiny.professors = source.professors
end

"""
Verify if meetings schedules are equal
"""
function equalSchedules(schedule_1::Array{Schedule, 1}, schedule_2::Array{Schedule, 1})
    if length(schedule_1) != length(schedule_2)
        return false
    end

    for i in eachindex(schedule_1)
        have = false

        for j in eachindex(schedule_2)
            if schedule_1[i].ID == schedule_2[j].ID
                have = true
                break
            end
        end

        if !have
            return false
        end
    end

    return true
end

"""
Add values to objectives graphics
"""
function addObjectivesGraphicValues(objectivesGraphic::ObjectivesGraphic, objectives::Objectives, time::Float64)

    if objectivesGraphic.deallocated[length(objectivesGraphic.deallocated)][1] != objectives.deallocated
        push!(objectivesGraphic.deallocated, (objectives.deallocated, time))
    end
    if objectivesGraphic.idleness[length(objectivesGraphic.idleness)][1] != objectives.idleness
        push!(objectivesGraphic.idleness, (objectives.idleness, time))
    end
    if objectivesGraphic.lessThan10[length(objectivesGraphic.lessThan10)][1] != objectives.lessThan10
        push!(objectivesGraphic.lessThan10, (objectives.lessThan10, time))
    end
    if objectivesGraphic.moreThan10[length(objectivesGraphic.moreThan10)][1] != objectives.moreThan10
        push!(objectivesGraphic.moreThan10, (objectives.moreThan10, time))
    end
    if objectivesGraphic.preferences[length(objectivesGraphic.preferences)][1] != objectives.preferences
        push!(objectivesGraphic.preferences, (objectives.preferences, time))
    end
    if objectivesGraphic.professors[length(objectivesGraphic.professors)][1] != objectives.professors
        push!(objectivesGraphic.professors, (objectives.professors, time))
    end

end

"""
Create output files
"""
function outputSolution(solution::Solution, costGraphic::Array{CostGraphic, 1}, objectivesGraphic::ObjectivesGraphic, maxTime::Int64, seed::Int64, instanceName::String)

    directoryName = split(instanceName, ".")[1]
    try
        mkdir("../output/$(directoryName)")
    catch
    end

    output = open("../output/$(directoryName)/solution_seed-$(seed)_maxTime-$(maxTime).json", "w")
    final_dict = OrderedDict("objectives" => solution.objectives, "meetings" => solution.meetings)
    data = JSON.json(final_dict)
    write(output, data)
    close(output)

    output = open("../output/$(directoryName)/costGraphic_seed-$(seed)_maxTime-$(maxTime).json", "w")
    final_dict = OrderedDict("points" => costGraphic)
    data = JSON.json(final_dict)
    write(output, data)
    close(output)

    output = open("../output/$(directoryName)/objectivesGraphic_seed-$(seed)_maxTime-$(maxTime).json", "w")
    final_dict = OrderedDict("idleness" => objectivesGraphic.idleness, "deallocated" => objectivesGraphic.deallocated, "lessThan10" => objectivesGraphic.lessThan10, "moreThan10" => objectivesGraphic.moreThan10,"preferences" => objectivesGraphic.preferences)
    data = JSON.json(final_dict)
    write(output, data)
    close(output)
end