export pas

"""
General function that rules the program
"""
function pas(FILE1::String, max_time::Int64, seed::Int64)
    start_reading = Dates.now()

    printstyled("Algorithm start time: ", bold = true, color = :yellow)
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
    meetings = Array{Meeting, 1}()
    meetingsSize = length(problemData["meetings"])
    readMeetings(problemData, meetings)

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

end