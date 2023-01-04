export pas

"""
General function that rules the program
"""
function pas(FILE1::String, maxTime::Int64, seed::Int64)
    start_reading = Dates.now()

    printstyled("Algorithm starts at: ", bold = true, color = :yellow)
    print(Dates.day(start_reading), "/", Dates.month(start_reading), "/", Dates.year(start_reading), " ")
    println(Dates.hour(start_reading), ":", Dates.minute(start_reading), ":", Dates.second(start_reading))
    println("----------------------------------------------------------------------------------")

    #=================================================================================================
    Reading instance
    =================================================================================================#

    # opening file
    dir = pwd()
    problemData = nothing
    try
        problemData = JSON.parse(open("../JSON/$(FILE1)"))
    catch
        println("Cannot open file $(FILE1)")
        exit(1)
    end

    # Reading schedules
    schedules = Array{Schedule, 1}()
    schedulesSize = length(problemData["schedules"])
    readSchedules(problemData, schedules)
    
    # Reading buildings
    buildings = Array{Building, 1}()
    buildingsSize = length(problemData["buildings"])
    readBuidings(problemData, buildings)

    # Reading classrooms
    classrooms = Array{Classroom, 1}()
    classroomsSize = length(problemData["classrooms"])
    readClassrooms(problemData, classrooms)

    # Reading professors
    professors = Array{Professor, 1}()
    professorsSize = length(problemData["professors"])
    readProfessors(problemData, professors)

    # Reading subjects
    subjects = Array{Subject, 1}()
    subjectsSize = length(problemData["subjects"])
    readSubjects(problemData, subjects)

    # Reading classes
    classes = Array{Class, 1}()
    classesSize = length(problemData["classes"])
    readClasses(problemData, classes)

    # Reading meetings
    instanceMeetings = Array{Meeting, 1}()
    meetingsSize = length(problemData["meetings"])
    readMeetings(problemData, instanceMeetings)

    # Reading preferences
    preferences = Array{Preference, 1}()
    preferencesSize = length(problemData["preferences"])
    readPreferences(problemData, preferences)

    # Reading restrictions
    restrictions = Array{Restriction, 1}()
    restrictionsSize = length(problemData["restrictions"])
    readRestrictions(problemData, restrictions)

    # Reading reservations
    reservations = Array{Reservation, 1}()
    reservationsSize = length(problemData["reservations"])
    readReservations(problemData, reservations)

    # Creating problems variable
    problem = Problem(schedules, buildings, classrooms, professors, subjects, classes, instanceMeetings, preferences, restrictions, reservations, FILE1, maxTime, seed)

    #=================================================================================================
    Initializing the variables that will be manipulated during the algorithm
    =================================================================================================#

    # Creating the Day variables to manipulate the timetable
    monday = createDay(2, schedulesSize, classroomsSize)
    thursday = createDay(3, schedulesSize, classroomsSize)
    wednesday = createDay(4, schedulesSize, classroomsSize)
    tuesday = createDay(5, schedulesSize, classroomsSize)
    friday = createDay(6, schedulesSize, classroomsSize)
    saturday = createDay(7, schedulesSize, classroomsSize)

    meetings = Array{SolutionMeeting, 1}()
    meetings = createSolutionMeetings(problem)
    for i in eachindex(meetings)

        if (meetings[i].dayOfWeek == 2)
            push!(monday.meetings, meetings[i])
        elseif (meetings[i].dayOfWeek == 3)
            push!(thursday.meetings, meetings[i])
        elseif (meetings[i].dayOfWeek == 4)
            push!(wednesday.meetings, meetings[i])
        elseif (meetings[i].dayOfWeek == 5)
            push!(tuesday.meetings, meetings[i])
        elseif (meetings[i].dayOfWeek == 6)
            push!(friday.meetings, meetings[i])
        elseif (meetings[i].dayOfWeek == 7)
            push!(saturday.meetings, meetings[i])
        else
        end

    end

    # allocating reservations
    allocateReservations(reservations, monday, thursday, wednesday, tuesday, friday, saturday)

    # Initializing Solution variable
    solution = Solution(meetings, monday, thursday, wednesday, tuesday, friday, saturday, 0, Objectives())

    # Calculating initial objectives with all meetings deallocated
    initialObjectives(solution)

    # Printing info about execution time
    end_reading = Dates.now()

    printstyled("Finish reading instance at: ", bold = true, color = :yellow)
    print(Dates.day(end_reading), "/", Dates.month(end_reading), "/", Dates.year(end_reading), " ")
    println(Dates.hour(end_reading), ":", Dates.minute(end_reading), ":", Dates.second(end_reading))
    println("----------------------------------------------------------------------------------")

    # x::Allocate = Allocate()
    # x.allowed = false
    # startMove(x, solution, problem)
    # println(x.meeting)
    # println(x.classroom)
    # println()
    # println(x.objectives)
    # println(doMove(x))

    #=================================================================================================
    Greedy algorithm
    =================================================================================================#

    greedy(solution, problem)
    # testMovements(solution, problem)

    end_greedy = Dates.now()

    printstyled("Finish greedy algorithm at: ", bold = true, color = :yellow)
    print(Dates.day(end_greedy), "/", Dates.month(end_greedy), "/", Dates.year(end_greedy), " ")
    println(Dates.hour(end_greedy), ":", Dates.minute(end_greedy), ":", Dates.second(end_greedy))
    println("----------------------------------------------------------------------------------")

    # checks allocations made by the greedy algorithm
    checkAllocation(solution)

    # output = open("../output/result.json", "w")

    # final_dict = OrderedDict("objectives" => solution.objectives, "meetings" => solution.meetings)
    # data = JSON.json(final_dict)
    # write(output, data)
    # close(output)

end