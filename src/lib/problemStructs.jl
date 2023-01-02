intOrNothing = Union{Int64, Nothing}
stringOrNothing = Union{String, Nothing}
boolOrNothing = Union{Bool, Nothing}

mutable struct Schedule
    ID::Int64
    startTimeDescription::String
    endTimeDescription::String

    startTime::Time
    endTime::Time

    Schedule(ID::Int64, startTimeDescription::String, endTimeDescription::String) = new(ID, startTimeDescription, endTimeDescription)
    Schedule(ID::Int64, startTimeDescription::String, endTimeDescription::String, startTime::Time, endTime::Time) = new(ID, startTimeDescription, endTimeDescription, startTime, endTime)
end

mutable struct Building
    ID::Int64
    name::String
end

mutable struct Classroom
    ID::Int64
    isLab::Bool
    capacity::Int64
    buildingID::Int64
    description::String
    floor::Int64
    board::String
    projector::Bool
end

mutable struct Professor
    ID::Int64

    code::String
    name::String
end

mutable struct Subject
    ID::Int64

    code::String
    name::String
end

mutable struct Class
    ID::Int64

    subjectCode::String
    classCode::String
    vacancies::Int64
    demand::Int64
    professors::Array{String, 1}
end

mutable struct Meeting
    ID::Int64

    isPractical::Bool
    dayOfWeek::Int64
    subjectCode::String
    classesCodes::Array{String, 1}
    schedules::Array{Int, 1}
end

mutable struct Preference
    ID::Int64

    category::String
    categoryCode::String
    building::intOrNothing
    floor::intOrNothing
    board::stringOrNothing
    projector::boolOrNothing
end

mutable struct Restriction
    ID::Int64

    category::String
    categoryCode::String
    building::intOrNothing
    floor::intOrNothing
    board::stringOrNothing
    projector::boolOrNothing
end

mutable struct Reservation
    ID::Int64

    classroomID::Int64
    dayOfWeek::Int64
    scheduleID::Int64
end

mutable struct Problem

    schedules::Array{Schedule, 1}
    buildings::Array{Building, 1}
    classrooms::Array{Classroom, 1}
    professors::Array{Professor, 1}
    subjects::Array{Subject, 1}
    classes::Array{Class, 1}
    meetings::Array{Meeting, 1}
    preferences::Array{Preference, 1}
    restrictions::Array{Restriction, 1}
    reservations::Array{Reservation, 1}

    instanceName::String
    maxTime::Int64
    seed::Int64

end