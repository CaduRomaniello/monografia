function verifier(solution::Solution, problem::Problem)
    x = Objectives()

    for i in eachindex(solution.meetings)
        if solution.meetings[i].classroomID == 0
            x.deallocated += solution.meetings[i].demand

            for j in eachindex(solution.meetings[i].preferences)
                if (solution.meetings[i].preferences[j].building !== nothing)
                    x.preferences += 1
                end
                if (solution.meetings[i].preferences[j].floor !== nothing)
                    x.preferences += 1
                end
                if (solution.meetings[i].preferences[j].board !== nothing)
                    x.preferences += 1
                end
                if (solution.meetings[i].preferences[j].projector !== nothing)
                    x.preferences += 1
                end
            end
        else
            demand = solution.meetings[i].demand
            capacity = problem.classrooms[solution.meetings[i].classroomID].capacity

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

            for j in eachindex(solution.meetings[i].preferences)
                if (solution.meetings[i].preferences[j].building !== nothing)
                    if (solution.meetings[i].preferences[j].building != problem.classrooms[solution.meetings[i].classroomID].buildingID)
                        x.preferences += 1
                    end
                end
                if (solution.meetings[i].preferences[j].floor !== nothing)
                    if (solution.meetings[i].preferences[j].floor != problem.classrooms[solution.meetings[i].classroomID].floor)
                        x.preferences += 1
                    end
                end
                if (solution.meetings[i].preferences[j].board !== nothing)
                    if (solution.meetings[i].preferences[j].board != problem.classrooms[solution.meetings[i].classroomID].board)
                        x.preferences += 1
                    end
                end
                if (solution.meetings[i].preferences[j].projector !== nothing)
                    if (solution.meetings[i].preferences[j].projector != problem.classrooms[solution.meetings[i].classroomID].projector)
                        x.preferences += 1
                    end
                end
            end
        end
    end

    for i in eachindex(problem.professors)
        if length(problem.professors[i].classrooms) > 1
            x.professors += length(problem.professors[i].classrooms) - 1
        end
    end

    verifyObjectivesEquality(solution.objectives, x)
    println("Verificado")
end

function verifyObjectivesEquality(s::Objectives, x::Objectives)
    if s.deallocated != x.deallocated
        println("DEALLOCATED")
        println("$(s.deallocated) - $(x.deallocated)")
    end

    if s.idleness != x.idleness
        println("IDLENESS")
        println("$(s.idleness) - $(x.idleness)")
    end

    if s.lessThan10 != x.lessThan10
        println("LESSTHAN10")
        println("$(s.lessThan10) - $(x.lessThan10)")
    end

    if s.moreThan10 != x.moreThan10
        println("MORETHAN10")
        println("$(s.moreThan10) - $(x.moreThan10)")
    end

    if s.preferences != x.preferences
        println("PREFERENCES")
        println("$(s.preferences) - $(x.preferences)")
    end

    if s.professors != x.professors
        println("PROFESSORS")
        println("$(s.professors) - $(x.professors)")
    end
end