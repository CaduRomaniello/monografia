function greedy(solution::Solution, problem::Problem)
    
    move::Allocate = Allocate()
    move.objectives = solution.objectives

    # Copy parameters to avoid changing their values

    copyClassrooms = deepcopy(problem.classrooms)
    sizeClassrooms = length(copyClassrooms)
    sort!(copyClassrooms, rev = true, alg = MergeSort, by = x -> x.capacity)
    # println(copyClassrooms[1])
    # println()
    
    copyMeetings = deepcopy(solution.meetings)
    sizeMeetings = length(copyMeetings)
    sort!(copyMeetings, rev = true, alg = MergeSort, by = x -> x.demand)
    # println(copyMeetings[1].demand)
    # println(copyMeetings[2].demand)
    # println()

    for i in eachindex(copyMeetings)
        move.allowed = false
        move.meeting = copyMeetings[i]

        if (copyMeetings[i].dayOfWeek == 2)
            move.day = solution.monday
        elseif (copyMeetings[i].dayOfWeek == 3)
            move.day = solution.thursday
        elseif (copyMeetings[i].dayOfWeek == 4)
            move.day = solution.wednesday
        elseif (copyMeetings[i].dayOfWeek == 5)
            move.day = solution.tuesday
        elseif (copyMeetings[i].dayOfWeek == 6)
            move.day = solution.friday
        elseif (copyMeetings[i].dayOfWeek == 7)
            move.day = solution.saturday
        else
        end

        for j in eachindex(copyClassrooms)
            if (verifyClassroomAvailability(move.day, copyClassrooms[j].ID, copyMeetings[i].schedules))
                if (checkRestrictions(copyMeetings[i].restrictions, copyClassrooms[j]))
                    move.classroom = copyClassrooms[j]
                    move.allowed = true
        
                    break
                end
            end
        end

        if move.allowed
            x = doMove(move)
            acceptMove(move)

            solution.objectives = deepcopy(x)
            move.objectives = solution.objectives
        end
    end

    for i in eachindex(copyMeetings)
        id = copyMeetings[i].ID
        solution.meetings[id] = deepcopy(copyMeetings[i])
    end

end