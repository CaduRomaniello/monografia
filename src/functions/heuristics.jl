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
    probabilities = [sum(movementsProbabilities[1:1]), sum(movementsProbabilities[1:2]), sum(movementsProbabilities[1:3]), sum(movementsProbabilities[1:4]), 1]

    # learning automaton constant
    alpha = 10^-2

    # data to generate the graphics
    costGraphic = Array{CostGraphic, 1}()
    objectivesGraphic = ObjectivesGraphic([(solution.objectives.idleness, Dates.value(startTime)/1000)], 
    [(solution.objectives.deallocated, Dates.value(startTime)/1000)], 
    [(solution.objectives.lessThan10, Dates.value(startTime)/1000)], 
    [(solution.objectives.moreThan10, Dates.value(startTime)/1000)], 
    [(solution.objectives.preferences, Dates.value(startTime)/1000)],
    [(solution.objectives.professors, Dates.value(startTime)/1000)])

    # represents the list item that will be used in the specific iteration
    listPosition = 1

    # initializing variables that will be used in the while loop
    # atualCost = 0
    # newCost = 0
    # objectives = 0
    # randomMove = 0
    
    while (endTime - startTime <= limitTime)

        # redefining the probabilities
        probabilities = [sum(movementsProbabilities[1:1]), sum(movementsProbabilities[1:2]), sum(movementsProbabilities[1:3]), sum(movementsProbabilities[1:4])]

        # getting the solutions that will be used in the comparisons in this iteration
        atualCost = list[listPosition]

        randomMove = rand(Float64)
        # println(randomMove)
        # randomMove = 0.9

        if randomMove <= 0 && randomMove < probabilities[1]                    # allocate movement
            # println("Allocate")
            chosenMovement = 1
            startMove(allocate, solution, problem)

            if !allocate.allowed
                endTime = Dates.now()
                continue
            end

            objectives = doMove(allocate)
            newCost = calculateSolutionValue(objectives)

            if newCost <= atualCost
                # println("Best")
                acceptMove(allocate)
                copyObjectives(objectives, solution.objectives)

                acceptTime = Dates.value(Dates.now() - startTime) / 1000
                addObjectivesGraphicValues(objectivesGraphic, solution.objectives, acceptTime)
                
                checkAllocate(allocate, solution)
                
                list[listPosition] = newCost
            else
                # println("Worse")
                # call learning automaton
                automaton_F1(movementsProbabilities, alpha, 0, chosenMovement)

                for i = 1:length(movementsProbabilities)
                    if (i != chosenMovement)
                        automaton_F2(movementsProbabilities, alpha, 0, i)
                    end
                end
            end
        elseif randomMove <= probabilities[1] && randomMove < probabilities[2] # deallocate movement
            # println("Deallocate")
            chosenMovement = 2
            startMove(deallocate, solution, problem)

            if deallocate.allowed
                endTime = Dates.now()
                continue
            end

            objectives = doMove(deallocate)
            newCost = calculateSolutionValue(objectives)

            if newCost <= atualCost
                # println("Best")
                acceptMove(deallocate)
                copyObjectives(objectives, solution.objectives)

                acceptTime = Dates.value(Dates.now() - startTime) / 1000
                addObjectivesGraphicValues(objectivesGraphic, solution.objectives, acceptTime)

                checkDeallocate(deallocate, solution)

                list[listPosition] = newCost
            else
                # println("Worse")
                # call learning automaton
                automaton_F1(movementsProbabilities, alpha, 0, chosenMovement)

                for i = 1:length(movementsProbabilities)
                    if (i != chosenMovement)
                        automaton_F2(movementsProbabilities, alpha, 0, i)
                    end
                end
            end
        elseif randomMove <= probabilities[2] && randomMove < probabilities[3] # replace movement
            # println("Replace")
            chosenMovement = 3
            startMove(replace, solution, problem)

            if !replace.allowed
                endTime = Dates.now()
                continue
            end

            objectives = doMove(replace)
            newCost = calculateSolutionValue(objectives)

            if newCost <= atualCost
                # println("Best")
                acceptMove(replace)
                copyObjectives(objectives, solution.objectives)

                acceptTime = Dates.value(Dates.now() - startTime) / 1000
                addObjectivesGraphicValues(objectivesGraphic, solution.objectives, acceptTime)

                checkReplace(replace, solution)

                list[listPosition] = newCost
            else
                # println("Worse")
                # call learning automaton
                automaton_F1(movementsProbabilities, alpha, 0, chosenMovement)

                for i = 1:length(movementsProbabilities)
                    if (i != chosenMovement)
                        automaton_F2(movementsProbabilities, alpha, 0, i)
                    end
                end
            end
        elseif randomMove <= probabilities[3] && randomMove < probabilities[4] # shift movement
            # println("Shift")
            chosenMovement = 4
            startMove(shift, solution, problem)

            if !shift.allowed
                endTime = Dates.now()
                continue
            end

            objectives = doMove(shift)
            newCost = calculateSolutionValue(objectives)

            if newCost <= atualCost
                # println("Best")
                acceptMove(shift)
                copyObjectives(objectives, solution.objectives)

                acceptTime = Dates.value(Dates.now() - startTime) / 1000
                addObjectivesGraphicValues(objectivesGraphic, solution.objectives, acceptTime)

                checkShift(shift, solution)

                list[listPosition] = newCost
            else
                # println("Worse")
                # call learning automaton
                automaton_F1(movementsProbabilities, alpha, 0, chosenMovement)

                for i = 1:length(movementsProbabilities)
                    if (i != chosenMovement)
                        automaton_F2(movementsProbabilities, alpha, 0, i)
                    end
                end
            end
        else                                                                   # swap movement
            # println("Swap")
            chosenMovement = 5
            startMove(swap, solution, problem)

            if !swap.allowed
                endTime = Dates.now()
                continue
            end

            objectives = doMove(swap)
            newCost = calculateSolutionValue(objectives)

            if newCost <= atualCost
                # println("Best")
                acceptMove(swap)
                copyObjectives(objectives, solution.objectives)

                acceptTime = Dates.value(Dates.now() - startTime) / 1000
                addObjectivesGraphicValues(objectivesGraphic, solution.objectives, acceptTime)

                checkSwap(swap, solution)

                list[listPosition] = newCost
            else
                # println("Worse")
                # call learning automaton
                automaton_F1(movementsProbabilities, alpha, 0, chosenMovement)

                for i = 1:length(movementsProbabilities)
                    if (i != chosenMovement)
                        automaton_F2(movementsProbabilities, alpha, 0, i)
                    end
                end
            end
        end

        # updating best solution
        # println(calculateSolutionValue(solution.objectives), ", ", calculateSolutionValue(solution.objectives))
        if calculateSolutionValue(solution.objectives) < calculateSolutionValue(bestSolution.objectives)
            bestSolution = deepcopy(solution)
            improvementTime = Dates.now()

            # getting data for the cost graphic
            time = improvementTime - startTime
            time = Dates.value(time) / 1000
            costData = CostGraphic(calculateSolutionValue(bestSolution.objectives), time)
            push!(costGraphic, costData)

            # call learning automaton
            automaton_F1(movementsProbabilities, alpha, 1, chosenMovement)

            for i = 1:length(movementsProbabilities)
                if (i != chosenMovement)
                    automaton_F2(movementsProbabilities, alpha, 1, i)
                end
            end

        end

        # println(sum(movementsProbabilities))
        # println(movementsProbabilities)
        # println(probabilities)
        # println("----------------------------------------------")

        # disturb
        
        # incrementing values
        if listPosition == length(list)
            listPosition = 1
        else
            listPosition += 1
        end

        endTime = Dates.now()

        checkAllocation(solution)

        a = []
        for i in eachindex(problem.professors)
            push!(a, (problem.professors[i].code, []))
        end

        for i in eachindex(solution.meetings)
            if solution.meetings[i].classroomID == 0
                continue
            end
            for j in eachindex(solution.meetings[i].professors)
                for k in eachindex(a)
                    if a[k][1] == solution.meetings[i].professors[j].code
                        achou = false
                        pos = 0
                        for m in eachindex(a[k][2])
                            if a[k][2][m].classroomID == solution.meetings[i].classroomID
                                achou = true
                                pos = m
                                break
                            end
                        end

                        if achou
                            a[k][2][pos].quantity += 1
                        else
                            push!(a[k][2], TaughtClassrooms(solution.meetings[i].classroomID, 1))
                        end
                    end
                end
            end
        end

        total = 0
        for i in eachindex(a)
            if length(a[i][2]) > 1
                total += length(a[i][2]) - 1
            end
        end
        # println(total, " - ", solution.objectives.professors)
        if total != solution.objectives.professors
            println(chosenMovement)
            println(swap.meeting_1)
            println()
            println(swap.meeting_2)
            println()
            println(swap.meeting_1)
            println(swap.meeting_2)
            println(swap.classroom_1)
            println(swap.classroom_2)
            println("----------------------------------------------------------")
            exit(0)
        end

    end

    return bestSolution, costGraphic, objectivesGraphic

end