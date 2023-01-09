function greedy(solution::Solution, problem::Problem)
    
    move::Allocate = Allocate()
    move.objectives = solution.objectives

    # Copy parameters to avoid changing their values

    # copyClassrooms = deepcopy(problem.classrooms)
    # sort!(copyClassrooms, rev = true, alg = MergeSort, by = x -> x.capacity)
    copyClassrooms = sort(problem.classrooms, rev = true, alg = MergeSort, by = x -> x.capacity)
    # println(copyClassrooms[1])
    # println()
    
    # copyMeetings = deepcopy(solution.meetings)
    # sort!(copyMeetings, rev = true, alg = MergeSort, by = x -> x.demand)
    copyMeetings = sort(solution.meetings, rev = true, alg = MergeSort, by = x -> x.demand)
    # println(copyMeetings[1].demand)
    # println(copyMeetings[2].demand)
    # println()

    for i in eachindex(copyMeetings)
        move.allowed = false
        move.meeting = solution.meetings[copyMeetings[i].ID]

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

            checkAllocate(move, solution)

            solution.objectives = deepcopy(x)
            move.objectives = solution.objectives
        end

    end

    # for i in eachindex(copyMeetings)
    #     id = copyMeetings[i].ID
    #     solution.meetings[id] = deepcopy(copyMeetings[i])
    # end

end

function LAHC(solution::Solution, problem::Problem, listSize::Int64, maxTime::Int64)
    
    # populating the LAHC list
    list = Array{Int64, 1}()
    costSolution = calculateSolutionValue(solution.objectives)
    for i = 1 : listSize
        push!(list, costSolution)
    end

    # initializing movements variables
    allocate = Allocate()
    deallocate = Deallocate()
    replace = Replace()
    shift = Shift()
    swap = Swap()

    # initializing best solution variable
    bestSolution = deepcopy(solution)

    # control time of execution
    startTime = Dates.now() 
    endTime = Dates.now()
    limitTime = Millisecond(maxTime * 1000)
    improvementTime = Dates.now()

    # variables that control which movement is going to be executed
    movementsProbabilities = [0.2, 0.2, 0.2, 0.2, 0.2]
    probabilities = [0, sum(movementsProbabilities[1:2]), sum(movementsProbabilities[1:3]), sum(movementsProbabilities[1:4]), 1]

    # represents the list item that will be used in the specific iteration
    listPosition = 1

    # initializing variables that will be used in the while loop
    # atualCost = 0
    # newCost = 0
    # objectives = 0
    # randomMove = 0

    # for i in eachindex(solution.meetings)
    #     if solution.meetings[i].classroomID == 0
    #         println("MERDA")
    #     end
    # end
    
    while (endTime - startTime <= limitTime)

        atualCost = list[listPosition]

        randomMove = rand(Float64)
        # randomMove = 0.9

        if randomMove <= 0 && randomMove < probabilities[1]                    # allocate movement
            startMove(allocate, solution, problem)

            if !allocate.allowed
                endTime = Dates.now()
                continue
            end

            objectives = doMove(allocate)
            newCost = calculateSolutionValue(objectives)

            if newCost <= atualCost
                acceptMove(allocate)
                copyObjectives(objectives, solution.objectives)

                checkAllocate(allocate, solution)

                list[listPosition] = newCost
            else
                # call learning automaton
            end
        elseif randomMove <= probabilities[1] && randomMove < probabilities[2] # deallocate movement
            startMove(deallocate, solution, problem)

            if deallocate.allowed
                endTime = Dates.now()
                continue
            end

            objectives = doMove(deallocate)
            newCost = calculateSolutionValue(objectives)

            if newCost <= atualCost
                acceptMove(deallocate)
                copyObjectives(objectives, solution.objectives)

                checkDeallocate(deallocate, solution)

                list[listPosition] = newCost
            else
                # call learning automaton
            end
        elseif randomMove <= probabilities[2] && randomMove < probabilities[3] # replace movement
            startMove(replace, solution, problem)

            if !replace.allowed
                endTime = Dates.now()
                continue
            end

            objectives = doMove(replace)
            newCost = calculateSolutionValue(objectives)

            if newCost <= atualCost
                acceptMove(replace)
                copyObjectives(objectives, solution.objectives)

                checkReplace(replace, solution)

                list[listPosition] = newCost
            else
                # call learning automaton
            end
        elseif randomMove <= probabilities[3] && randomMove < probabilities[4] # shift movement
            startMove(shift, solution, problem)

            if !shift.allowed
                endTime = Dates.now()
                continue
            end

            objectives = doMove(shift)
            newCost = calculateSolutionValue(objectives)

            if newCost <= atualCost
                acceptMove(shift)
                copyObjectives(objectives, solution.objectives)

                checkShift(shift, solution)

                list[listPosition] = newCost
            else
                # call learning automaton
            end
        else                                                                   # swap movement
            startMove(swap, solution, problem)

            if !swap.allowed
                endTime = Dates.now()
                continue
            end

            objectives = doMove(swap)
            newCost = calculateSolutionValue(objectives)

            if newCost <= atualCost
                acceptMove(swap)
                copyObjectives(objectives, solution.objectives)

                checkSwap(swap, solution)

                list[listPosition] = newCost
            else
                # call learning automaton
            end
        end

        # updating best solution
        # println(calculateSolutionValue(solution.objectives), ", ", calculateSolutionValue(solution.objectives))
        if calculateSolutionValue(solution.objectives) < calculateSolutionValue(bestSolution.objectives)
            bestSolution = deepcopy(solution)
            improvementTime = Dates.now()

            # call learning automaton
            # graphics code
        end

        # disturb
        
        # incrementing values
        if listPosition == length(list)
            listPosition = 1
        else
            listPosition += 1
        end

        endTime = Dates.now()

        checkAllocation(solution)

    end

    return bestSolution

end