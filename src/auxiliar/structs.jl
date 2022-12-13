intOrNothing = Union{Int64, Nothing}
stringOrNothing = Union{String, Nothing}
boolOrNothing = Union{Bool, Nothing}

mutable struct Schedule
    ID::Int64
    startTime::String
    endTime::String
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
    desciption::String
    floor::Int64
    board::String
    projector::Bool
end

mutable struct Professor
    ID::String
    name::String
end

mutable struct Subject
    ID::String
    name::String
end

mutable struct Class
    subjectID::String
    classID::String
    vacancies::Int64
    demand::Int64
    professors::Array{String, 1}
end

mutable struct Meeting
    isPractical::Bool
    dayOfWeek::Int64
    subjectID::String
    classesIDs::Array{String, 1}
    schedules::Array{Int, 1}
end

mutable struct Preference
    category::String
    categoryCode::String
    building::intOrNothing
    floor::intOrNothing
    board::stringOrNothing
    projector::boolOrNothing
end

mutable struct Restriction
    category::String
    categoryCode::String
    building::intOrNothing
    floor::intOrNothing
    board::stringOrNothing
    projector::boolOrNothing
end

mutable struct Reservation
    classroomID::Int64
    dayOfWeek::Int64
    scheduleID::Int64
end