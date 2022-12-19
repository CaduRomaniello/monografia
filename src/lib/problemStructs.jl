intOrNothing = Union{Int64, Nothing}
stringOrNothing = Union{String, Nothing}
boolOrNothing = Union{Bool, Nothing}

mutable struct Schedule
    position::Int64

    ID::Int64
    startTimeDescription::String
    endTimeDescription::String

    startTime::Time
    endTime::Time

    Schedule(position::Int64, ID::Int64, startTimeDescription::String, endTimeDescription::String) = new(position, ID, startTimeDescription, endTimeDescription)
    Schedule(position::Int64, ID::Int64, startTimeDescription::String, endTimeDescription::String, startTime::Time, endTime::Time) = new(position, ID, startTimeDescription, endTimeDescription, startTime, endTime)
end

mutable struct Building
    position::Int64

    ID::Int64
    name::String
end

mutable struct Classroom
    position::Int64
    
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
    position::Int64

    ID::String
    name::String
end

mutable struct Subject
    position::Int64

    ID::String
    name::String
end

mutable struct Class
    position::Int64

    subjectID::String
    classID::String
    vacancies::Int64
    demand::Int64
    professors::Array{String, 1}
end

mutable struct Meeting
    position::Int64

    isPractical::Bool
    dayOfWeek::Int64
    subjectID::String
    classesIDs::Array{String, 1}
    schedules::Array{Int, 1}
end

mutable struct Preference
    position::Int64

    category::String
    categoryCode::String
    building::intOrNothing
    floor::intOrNothing
    board::stringOrNothing
    projector::boolOrNothing
end

mutable struct Restriction
    position::Int64

    category::String
    categoryCode::String
    building::intOrNothing
    floor::intOrNothing
    board::stringOrNothing
    projector::boolOrNothing
end

mutable struct Reservation
    position::Int64

    classroomID::Int64
    dayOfWeek::Int64
    scheduleID::Int64
end