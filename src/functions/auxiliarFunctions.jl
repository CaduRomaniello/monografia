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
        push!(x, SolutionMeeting(i, problem.meetings[i].isPractical, problem.meetings[i].dayOfWeek, problem.meetings[i].subjectID, problem.meetings[i].classesIDs, [], 0, 0, [], "", 0, 0, [], []))

        # push each schedule into SolutionMeeting
        for j in eachindex(problem.meetings[i].schedules)
            push!(x[i].schedules, problem.schedules[problem.meetings[i].schedules[j]])
        end

        # finding all the classes tha t this meeting have
        for j in eachindex(problem.meetings[i].classesIDs)
            meetingCode = string(problem.meetings[i].subjectID, "-", problem.meetings[i].classesIDs[j])
            for k in eachindex(problem.classes)
                classCode = string(problem.classes[k].subjectID, "-", problem.classes[k].classID)

                if meetingCode == classCode
                    # println(meetingCode, " / ", classCode)
                    x[i].vacancies += problem.classes[k].vacancies
                    x[i].demand += problem.classes[k].demand

                    for m in eachindex(problem.classes[k].professors)
                        for n in eachindex(problem.professors)
                            if problem.classes[k].professors[m] == problem.professors[n].ID
                                push!(x[i].professors, problem.professors[n])

                                for t in eachindex(problem.preferences)
                                    if problem.professors[n].ID == problem.preferences[t].categoryCode
                                        push!(x[i].preferences, problem.preferences[t])
                                        break
                                    end
                                end
                    
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

            for k in eachindex(problem.preferences)
                if meetingCode == problem.preferences[k].categoryCode
                    push!(x[i].preferences, problem.preferences[k])
                    break
                end
            end

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
function calculateAllocationObjective(move::Allocate)

    x = Objectives()

    demand = move.meeting.demand
    capacity = move.classroom.capacity

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
function calculatePreferenceObjective(move::Allocate)
    x = Objectives()
    if (move.classroom.ID != 0)
        for i in eachindex(move.meeting.preferences)
            if (move.meeting.preferences[i].building !== nothing)
                if (move.meeting.preferences[i].building != move.classroom.buildingID)
                    x.preferences += 1
                else
                    x.preferences -= 1
                end
            end
            if (move.meeting.preferences[i].floor !== nothing)
                if (move.meeting.preferences[i].floor != move.classroom.floor)
                    x.preferences += 1
                else
                    x.preferences -= 1
                end
            end
            if (move.meeting.preferences[i].board !== nothing)
                if (move.meeting.preferences[i].board != move.classroom.board)
                    x.preferences += 1
                else
                    x.preferences -= 1
                end
            end
            if (move.meeting.preferences[i].projector !== nothing)
                if (move.meeting.preferences[i].projector != move.classroom.projector)
                    x.preferences += 1
                else
                    x.preferences -= 1
                end
            end
        end
        return x
    else
        for i in eachindex(move.meeting.preferences)
            if (move.meeting.preferences[i].building !== nothing)
                x.preferences += 1
            end
            if (move.meeting.preferences[i].floor !== nothing)
                x.preferences += 1
            end
            if (move.meeting.preferences[i].board !== nothing)
                x.preferences += 1
            end
            if (move.meeting.preferences[i].projector !== nothing)
                x.preferences += 1
            end
        end
        return x
    end
end