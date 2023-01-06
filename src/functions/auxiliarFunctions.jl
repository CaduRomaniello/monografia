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
                            if problem.classes[k].professors[m] == problem.professors[n].ID
                                push!(x[i].professors, problem.professors[n])

                                # finding all professor preferences for this meeting
                                for t in eachindex(problem.preferences)
                                    if problem.professors[n].ID == problem.preferences[t].categoryCode
                                        push!(x[i].preferences, problem.preferences[t])
                                        break
                                    end
                                end
                    
                                # finding all professor restrictions for this meeting
                                for t in eachindex(problem.restrictions)
                                    if problem.professors[n].ID == problem.restrictions[t].categoryCode
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
                    x.preferences -= 1
                end
            end
            if (meeting.preferences[i].floor !== nothing)
                if (meeting.preferences[i].floor != classroom.floor)
                    x.preferences += 1
                else
                    x.preferences -= 1
                end
            end
            if (meeting.preferences[i].board !== nothing)
                if (meeting.preferences[i].board != classroom.board)
                    x.preferences += 1
                else
                    x.preferences -= 1
                end
            end
            if (meeting.preferences[i].projector !== nothing)
                if (meeting.preferences[i].projector != classroom.projector)
                    x.preferences += 1
                else
                    x.preferences -= 1
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