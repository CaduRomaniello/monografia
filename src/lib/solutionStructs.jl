mutable struct SolutionMeeting

    ID::Int64

    isPractical::Bool
    dayOfWeek::Int64
    subjectID::String
    classesIDs::Array{String, 1}
    schedules::Array{Schedule, 1}

    vacancies::Int64
    demand::Int64
    professors::Array{Professor, 1}

    subjectName::String

    classroomID::Int64
    buildingID::Int64

    preferences::Array{Preference, 1}
    restrictions::Array{Restriction, 1}

end

mutable struct Cell

    status::Int64 # 0 -> deallocated, 1 -> allocated, 2 -> reserved
    meetingID::Int64

end

mutable struct Day

    day::String
    dayofWeek::Int64
    meetings::Array{SolutionMeeting, 1}
    matrix::Array{Cell, 2}

end

mutable struct Objectives
    instanceName::String

    idleness::Int64
    deallocated::Int64
    lessThan10::Int64
    moreThan10::Int64
    preferences::Int64
    professors::Int64

    Objectives(instanceName::String) = new(instanceName, 0, 0, 0, 0, 0, 0)
    Objectives() = new("", 0, 0, 0, 0, 0, 0)
end

mutable struct Solution

    meetings::Array{SolutionMeeting, 1}

    monday::Day
    thursday::Day
    wednesday::Day
    tuesday::Day
    friday::Day
    saturday::Day
    cost::Int128

    objectives::Objectives

    Solution() = new()
    Solution(sub_encontros, segunda, terca, quarta, quinta, sexta, sabado, custo_inicial, aval) = new(sub_encontros, segunda, terca, quarta, quinta, sexta, sabado, custo_inicial, aval)

end

mutable struct CostGraphic

    cost::Int128
    time::Float64

    CostGraphic() = new()
    CostGraphic(cost, time) = new(cost, time)

end

mutable struct ObjectivesGraphic

    idleness::Array{Tuple{Int64, Float64}}
    deallocated::Array{Tuple{Int64, Float64}}
    lessThan10::Array{Tuple{Int64, Float64}}
    moreThan10::Array{Tuple{Int64, Float64}}
    preferences::Array{Tuple{Int64, Float64}}
    professors::Array{Tuple{Int64, Float64}}

end