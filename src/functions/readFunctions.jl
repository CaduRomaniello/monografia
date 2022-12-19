function readSchedules(data, schedules::Array{Schedule, 1})
    
    for i = 1:length(data["schedules"])

        ID = data["schedules"][i]["ID"]
        startTimeDescription = data["schedules"][i]["startTime"]
        endTimeDescription = data["schedules"][i]["endTime"]

        startTime = stringToTime(startTimeDescription)
        endTime = stringToTime(endTimeDescription)

        schedule = Schedule(i, ID, startTimeDescription, endTimeDescription, startTime, endTime)

        push!(schedules, schedule)

    end

end

function readBuidings(problemData, buildings::Array{Building, 1})
    
    for i = 1:length(problemData["buildings"])

        ID = problemData["buildings"][i]["ID"]
        name = problemData["buildings"][i]["name"]

        building = Building(i, ID, name)

        push!(buildings, building)

    end

end

function readClassrooms(problemData, classrooms::Array{Classroom, 1})
    
    for i = 1:length(problemData["classrooms"])

        ID = problemData["classrooms"][i]["ID"]
        isLab = problemData["classrooms"][i]["isLab"]
        capacity = problemData["classrooms"][i]["capacity"]
        buildingID = problemData["classrooms"][i]["buildingID"]
        description = problemData["classrooms"][i]["description"]
        floor = problemData["classrooms"][i]["floor"]
        board = problemData["classrooms"][i]["board"]
        projector = problemData["classrooms"][i]["projector"]

        classroom = Classroom(i, ID, isLab, capacity, buildingID, description, floor, board, projector)

        push!(classrooms, classroom)

    end

end

function readProfessors(problemData, professors::Array{Professor, 1})

    for i = 1:length(problemData["professors"])

        ID = problemData["professors"][i]["ID"]
        name = problemData["professors"][i]["name"]

        professor = Professor(i, ID, name)

        push!(professors, professor)

    end

end

function readSubjects(problemData, subjects::Array{Subject, 1})

    for i = 1:length(problemData["subjects"])

        ID = problemData["subjects"][i]["ID"]
        name = problemData["subjects"][i]["name"]

        subject = Subject(i, ID, name)

        push!(subjects, subject)

    end

end

function readClasses(problemData, classes::Array{Class, 1})

    for i = 1:length(problemData["classes"])

        subjectID = problemData["classes"][i]["subjectID"]
        classID = problemData["classes"][i]["classID"]
        vacancies = problemData["classes"][i]["vacancies"]
        demand = problemData["classes"][i]["demand"]
        professors = []
        for j = 1:length(problemData["classes"][i]["professors"])
            push!(professors, problemData["classes"][i]["professors"][j])
        end

        class = Class(i, subjectID, classID, vacancies, demand, professors)

        push!(classes, class)

    end

end

function readMeetings(problemData, meetings::Array{Meeting, 1})

    for i = 1:length(problemData["meetings"])

        isPractical = problemData["meetings"][i]["isPractical"]
        dayOfWeek = problemData["meetings"][i]["dayOfWeek"]
        subjectID = problemData["meetings"][i]["subjectID"]
        classesIDs = []
        for j = 1:length(problemData["meetings"][i]["classesIDs"])
            push!(classesIDs, problemData["meetings"][i]["classesIDs"][j])
        end
        schedules = []
        for j = 1:length(problemData["meetings"][i]["schedules"])
            push!(schedules, problemData["meetings"][i]["schedules"][j])
        end

        meeting = Meeting(i, isPractical, dayOfWeek, subjectID, classesIDs, schedules)

        push!(meetings, meeting)

    end

end

function readPreferences(problemData, preferences::Array{Preference, 1})

    for i = 1:length(problemData["preferences"])

        category = problemData["preferences"][i]["category"]
        categoryCode = problemData["preferences"][i]["categoryCode"]
        building = problemData["preferences"][i]["building"]
        floor = problemData["preferences"][i]["floor"]
        board = problemData["preferences"][i]["board"]
        projector = problemData["preferences"][i]["projector"]

        preference = Preference(i, category, categoryCode, building, floor, board, projector)

        push!(preferences, preference)

    end

end

function readRestrictions(problemData, restrictions::Array{Restriction, 1})

    for i = 1:length(problemData["restrictions"])

        category = problemData["restrictions"][i]["category"]
        categoryCode = problemData["restrictions"][i]["categoryCode"]
        building = problemData["restrictions"][i]["building"]
        floor = problemData["restrictions"][i]["floor"]
        board = problemData["restrictions"][i]["board"]
        projector = problemData["restrictions"][i]["projector"]

        restriction = Restriction(i, category, categoryCode, building, floor, board, projector)

        push!(restrictions, restriction)

    end

end

function readReservations(problemData, reservations::Array{Reservation, 1})

    for i = 1:length(problemData["reservations"])

        classroomID = problemData["reservations"][i]["classroomID"]
        dayOfWeek = problemData["reservations"][i]["dayOfWeek"]
        scheduleID = problemData["reservations"][i]["scheduleID"]

        reservation = Reservation(i, classroomID, dayOfWeek, scheduleID)

        push!(reservations, reservation)

    end

end