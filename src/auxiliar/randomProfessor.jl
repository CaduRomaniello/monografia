using JSON
using OrderedCollections
using Random
include("structs.jl")

mutable struct PWT
    code::String
    monday::Array{Bool, 1}
    tuesday::Array{Bool, 1}
    wednesday::Array{Bool, 1}
    thursday::Array{Bool, 1}
    friday::Array{Bool, 1}
    saturday::Array{Bool, 1}
end

mutable struct Professor
    code::String
    name::String
end

mutable struct Subject
    code::String
    name::String
end

mutable struct Class
    subjectCode::String
    classCode::String
    vacancies::Int64
    demand::Int64
    professors::Array{String, 1}
end

mutable struct Meeting
    isPractical::Bool
    dayOfWeek::Int64
    subjectCode::String
    classesCodes::Array{String, 1}
    schedules::Array{Int, 1}
end

function main()
    dir = pwd()
    dados = JSON.parse(open("$(dir)/../../JSON/fixed.json"))

    # =====================================================================================
    # Horarios
    # =====================================================================================
    schedules = Array{Schedule, 1}()
    sizeSchedules = length(dados["schedules"])
    for i = 1:sizeSchedules

        codigo = dados["schedules"][i]["ID"]
        horaInicio = dados["schedules"][i]["startTime"]
        horaFim = dados["schedules"][i]["endTime"]

        horario = Schedule(codigo, horaInicio, horaFim)

        push!(schedules, horario)

    end

    # =====================================================================================
    # Predios
    # =====================================================================================
    buildings = Array{Building, 1}()
    sizeBuildings = length(dados["buildings"])
    for i = 1:sizeBuildings

        codigo = dados["buildings"][i]["ID"]
        descricao = dados["buildings"][i]["name"]

        predio = Building(codigo, descricao)

        push!(buildings, predio)

    end

    # =====================================================================================
    # Salas
    # =====================================================================================
    classrooms = Array{Classroom, 1}()
    sizeClassrooms = length(dados["classrooms"])
    for i = 1:sizeClassrooms

        codigo = dados["classrooms"][i]["ID"]
        isLab = dados["classrooms"][i]["isLab"]
        capacidade = dados["classrooms"][i]["capacity"]
        predioCodigo = dados["classrooms"][i]["buildingID"]
        descricao = dados["classrooms"][i]["description"]
        pavimento = dados["classrooms"][i]["floor"]
        quadro = dados["classrooms"][i]["board"]
        projetor = dados["classrooms"][i]["projector"]

        sala = Classroom(codigo, isLab, capacidade, predioCodigo, descricao, pavimento, quadro, projetor)

        push!(classrooms, sala)

    end

    # =====================================================================================
    # Professores
    # =====================================================================================
    professors = Array{Professor, 1}()
    sizeProfessors = length(dados["professors"])
    for i = 1:sizeProfessors

        codigo = dados["professors"][i]["code"]
        nome = dados["professors"][i]["name"]

        if codigo == "0"
            continue
        end

        professor = Professor(codigo, nome)

        push!(professors, professor)

    end

    # =====================================================================================
    # Disciplinas
    # =====================================================================================
    subjects = Array{Subject, 1}()
    sizeSubjects = length(dados["subjects"])
    for i = 1:sizeSubjects

        codigo = dados["subjects"][i]["code"]
        descricao = dados["subjects"][i]["name"]

        disciplina = Subject(codigo, descricao)

        push!(subjects, disciplina)

    end

    # =====================================================================================
    # Turmas
    # =====================================================================================
    classes = Array{Class, 1}()
    sizeClasses = length(dados["classes"])
    for i = 1:sizeClasses

        codigoDisciplina = dados["classes"][i]["subjectCode"]
        codigoTurma = dados["classes"][i]["classCode"]
        vagas = dados["classes"][i]["vacancies"]
        demanda = dados["classes"][i]["demand"]
        professores = []
        
        if startswith(codigoDisciplina, "MED") || vagas == 0 || demanda == 0
            continue
        end

        turma = Class(codigoDisciplina, codigoTurma, vagas, demanda, professores)

        push!(classes, turma)

    end

    # =====================================================================================
    # Encontros
    # =====================================================================================
    meetings = Array{Meeting, 1}()
    sizeMeetings = length(dados["meetings"])
    for i = 1:sizeMeetings

        pratica = dados["meetings"][i]["isPractical"]
        dia = dados["meetings"][i]["dayOfWeek"]
        codigoDisciplina = dados["meetings"][i]["subjectCode"]
        codigosTurma = []
        for j = 1:length(dados["meetings"][i]["classesCodes"])
            push!(codigosTurma, dados["meetings"][i]["classesCodes"][j])
        end
        horarios = []
        for j = 1:length(dados["meetings"][i]["schedules"])
            if !(dados["meetings"][i]["schedules"][j] in horarios)
                push!(horarios, dados["meetings"][i]["schedules"][j])
            end
        end
        sort!(horarios)

        if startswith(codigoDisciplina, "MED")
            continue
        end

        encontro = Meeting(pratica, dia, codigoDisciplina, codigosTurma, horarios)

        push!(meetings, encontro)

    end

    # =====================================================================================
    # Preferencias
    # =====================================================================================
    preferences = Array{Preference, 1}()
    sizePreferences = length(dados["preferences"])
    for i = 1:sizePreferences

        tipo = dados["preferences"][i]["category"]
        codigoObjeto = dados["preferences"][i]["categoryCode"]
        predio = dados["preferences"][i]["building"]
        pavimento = dados["preferences"][i]["floor"]
        quadro = dados["preferences"][i]["board"]
        datashow = dados["preferences"][i]["projector"]

        if startswith(codigoObjeto, "MED")
            continue
        end

        preferencia = Preference(tipo, codigoObjeto, predio, pavimento, quadro, datashow)

        push!(preferences, preferencia)

    end

    # =====================================================================================
    # Restricoes
    # =====================================================================================
    restrictions = Array{Restriction, 1}()
    sizeRestrictions = length(dados["restrictions"])
    for i = 1:sizeRestrictions

        tipo = dados["restrictions"][i]["category"]
        codigoObjeto = dados["restrictions"][i]["categoryCode"]
        predio = dados["restrictions"][i]["building"]
        pavimento = dados["restrictions"][i]["floor"]
        quadro = dados["restrictions"][i]["board"]
        datashow = dados["restrictions"][i]["projector"]

        if startswith(codigoObjeto, "MED")
            continue
        end

        restricao = Restriction(tipo, codigoObjeto, predio, pavimento, quadro, datashow)

        push!(restrictions, restricao)

    end
    
    # =====================================================================================
    # Reservas
    # =====================================================================================
    reservations = Array{Reservation, 1}()
    sizePreferences = length(dados["reservations"])
    for i = 1:sizePreferences

        sala = dados["reservations"][i]["classroomID"]
        dia = dados["reservations"][i]["dayOfWeek"]
        horario = dados["reservations"][i]["scheduleID"]

        reserva = Reservation(sala, dia, horario)

        push!(reservations, reserva)

    end

    # =====================================================================================
    # Sorteando professores pra nao ter conflito de horarios
    # =====================================================================================

    matriz = Array{Bool, 1}(undef, length(schedules))
    for i in eachindex(schedules)
        matriz[i] = false
    end

    pwt = Array{PWT, 1}()
    for i in eachindex(professors)
        x = PWT(professors[i].code, deepcopy(matriz), deepcopy(matriz), deepcopy(matriz), deepcopy(matriz), deepcopy(matriz), deepcopy(matriz))
        push!(pwt, x)
    end

    posTurma = []
    for i in eachindex(meetings)
        codMeeting = string(meetings[i].subjectCode, "-", meetings[i].classesCodes[1])
        for j in eachindex(classes)
            codClass = string(classes[j].subjectCode, "-", classes[j].classCode)
            if codMeeting == codClass
                push!(posTurma, j)
            end
        end
    end

    for i in eachindex(meetings)
        if length(classes[posTurma[i]].professors) > 0
            continue
        end
        horarios = meetings[i].schedules
        alocou = false
        while alocou == false
            x = rand(1:sizeProfessors)
    
            day = ""
            if meetings[i].dayOfWeek == 2
                day = pwt[x].monday
            elseif meetings[i].dayOfWeek == 3
                day = pwt[x].thursday
            elseif meetings[i].dayOfWeek == 4
                day = pwt[x].wednesday
            elseif meetings[i].dayOfWeek == 5
                day = pwt[x].tuesday
            elseif meetings[i].dayOfWeek == 6
                day = pwt[x].friday
            elseif meetings[i].dayOfWeek == 7
                day = pwt[x].saturday
            else
                println("ERRO")
            end
    
            ocupado = false
            for k in horarios
                if day[k]
                    ocupado = true
                    break
                end
            end
    
            if !ocupado
                alocou = true
                for k in horarios
                    day[k] = true
                end
                push!(classes[posTurma[i]].professors, pwt[x].code)
                break
            end
    
            if length(meetings[i].classesCodes) > 1
                println("ERRO")
            end
        end
    end

    for i in eachindex(classes)
        if length(classes[i].professors) == 0
            if i in posTurma
                println("Sem prof")
            end
        end
    end
    println("ACABOU")

    # =====================================================================================
    # Escrevendo os dados no novo JSON
    # =====================================================================================

    output = open("../../JSON/fixed2.json", "w")

    final_dict = OrderedDict("schedules" => schedules, "buildings" => buildings, "classrooms" => classrooms, "professors" => professors, "subjects" => subjects, "classes" => classes, "meetings" => meetings, "preferences" => preferences, "restrictions" => restrictions, "reservations" => reservations)
    data = JSON.json(final_dict)
    write(output, data)
    close(output)

end

main()