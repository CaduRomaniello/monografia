using JSON
using OrderedCollections

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
    description::String
    floor::Int64
    board::String
    projector::Bool
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
    schedules::Array{Int64, 1}
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

mutable struct MeetingOutput
    isPractical::Bool
    dayOfWeek::Int64
    vacancies::Int64
    demand::Int64
    subjectID::String
    classes::Array{String, 1}
    schedules::Array{Int64, 1}
    professors::Array{String, 1}
end

mutable struct Cell
    working::Bool
    meetings::Array{Int64, 1}
end

mutable struct ProfessorWorkTime
    ID::String
    monday::Array{Cell, 1}
    tuesday::Array{Cell, 1}
    wednesday::Array{Cell, 1}
    thursday::Array{Cell, 1}
    friday::Array{Cell, 1}
    saturday::Array{Cell, 1}
end

function main()
    dir = pwd()
    dados = JSON.parse(open("$(dir)/../../JSON/original.json"))

    # =====================================================================================
    # Horarios
    # =====================================================================================
    schedules = Array{Schedule, 1}()
    sizeSchedules = length(dados["horarios"])
    for i = 1:sizeSchedules

        codigo = dados["horarios"][i]["codigo"]
        horaInicio = dados["horarios"][i]["horaInicio"]
        horaFim = dados["horarios"][i]["horaFim"]

        horario = Schedule(codigo, horaInicio, horaFim)

        push!(schedules, horario)

    end

    # =====================================================================================
    # Predios
    # =====================================================================================
    buildings = Array{Building, 1}()
    sizeBuildings = length(dados["predios"])
    for i = 1:sizeBuildings

        codigo = dados["predios"][i]["codigo"]
        descricao = dados["predios"][i]["descricao"]

        predio = Building(codigo, descricao)

        push!(buildings, predio)

    end

    # =====================================================================================
    # Salas
    # =====================================================================================
    classrooms = Array{Classroom, 1}()
    sizeClassrooms = length(dados["salas"])
    for i = 1:sizeClassrooms

        codigo = dados["salas"][i]["codigo"]
        isLab = false
        if dados["salas"][i]["tipo"] == "P"
            isLab = true
        end
        capacidade = dados["salas"][i]["capacidade"]
        predioCodigo = dados["salas"][i]["predioCodigo"]
        descricao = dados["salas"][i]["descricao"]
        pavimento = dados["salas"][i]["pavimento"]
        quadro = dados["salas"][i]["quadro"]
        projetor = false
        if dados["salas"][i]["datashow"] == "S"
            projetor = true
        end

        sala = Classroom(codigo, isLab, capacidade, predioCodigo, descricao, pavimento, quadro, projetor)

        push!(classrooms, sala)

    end

    # =====================================================================================
    # Professores
    # =====================================================================================
    professors = Array{Professor, 1}()
    sizeProfessors = length(dados["professores"])
    for i = 1:sizeProfessors

        codigo = dados["professores"][i]["codigo"]
        nome = dados["professores"][i]["nome"]

        professor = Professor(codigo, nome)

        push!(professors, professor)

    end

    # =====================================================================================
    # Disciplinas
    # =====================================================================================
    subjects = Array{Subject, 1}()
    sizeSubjects = length(dados["disciplinas"])
    for i = 1:sizeSubjects

        codigo = dados["disciplinas"][i]["codigo"]
        descricao = dados["disciplinas"][i]["descricao"]

        disciplina = Subject(codigo, descricao)

        push!(subjects, disciplina)

    end

    # =====================================================================================
    # Turmas
    # =====================================================================================
    classes = Array{Class, 1}()
    sizeClasses = length(dados["turmas"])
    for i = 1:sizeClasses

        codigo = dados["turmas"][i]["codigo"]
        codigoDisciplina = split(codigo, "-")[1]
        codigoTurma = split(codigo, "-")[2]
        vagas = dados["turmas"][i]["vagasOfertadas"]
        demanda = dados["turmas"][i]["demanda"]
        if startswith(codigoDisciplina, "MED")
            continue
        end
        if vagas == 0 || demanda == 0
            continue
        end
        professores = []
        for j = 1:length(dados["turmas"][i]["professores"])
            push!(professores, dados["turmas"][i]["professores"][j]["codigo"])
        end

        turma = Class(codigoDisciplina, codigoTurma, vagas, demanda, professores)

        push!(classes, turma)

    end

    # =====================================================================================
    # Encontros
    # =====================================================================================
    meetings = Array{Meeting, 1}()
    sizeMeetings = length(dados["encontros"])
    for i = 1:sizeMeetings

        pratica = false 
        if dados["encontros"][i]["tipo"] == "P"
            pratica = true
        end
        dia = dados["encontros"][i]["diaSemana"]
        codigoDisciplina = String(split(dados["encontros"][i]["codTurma"], "-")[1])
        if startswith(codigoDisciplina, "MED")
            continue
        end
        codigosTurma = [String(split(dados["encontros"][i]["codTurma"], "-")[2])]
        horarios = []
        for j = 1:length(dados["encontros"][i]["horarios"])
            if !(dados["encontros"][i]["horarios"][j]["codigo"] in horarios)
                push!(horarios, dados["encontros"][i]["horarios"][j]["codigo"])
            end
        end

        encontro = Meeting(pratica, dia, codigoDisciplina, codigosTurma, horarios)

        push!(meetings, encontro)

    end

    # =====================================================================================
    # Preferencias
    # =====================================================================================
    preferences = Array{Preference, 1}()
    sizePreferences = length(dados["preferencias"])
    for i = 1:sizePreferences

        tipo = dados["preferencias"][i]["tipo"]
        if tipo == "curso"
            continue
        end
        codigoObjeto = dados["preferencias"][i]["codigoObjeto"]
        predio = dados["preferencias"][i]["predio"]
        pavimento = dados["preferencias"][i]["pavimento"]
        quadro = dados["preferencias"][i]["quadro"]
        datashow = false
        if dados["preferencias"][i]["datashow"] == "S"
            datashow = true
        end

        preferencia = Preference(tipo, codigoObjeto, predio, pavimento, quadro, datashow)

        push!(preferences, preferencia)

    end

    # =====================================================================================
    # Restricoes
    # =====================================================================================
    restrictions = Array{Restriction, 1}()
    push!(restrictions, Restriction("professor", "1.068.874", nothing, nothing, "W", nothing))
    push!(restrictions, Restriction("turma", "FIS835-11", 1, nothing, nothing, nothing))
    
    # =====================================================================================
    # Reservas
    # =====================================================================================
    reservations = Array{Reservation, 1}()
    push!(reservations, Reservation(2, 3, 4))
    push!(reservations, Reservation(5, 6, 6))
    push!(reservations, Reservation(5, 6, 7))
    push!(reservations, Reservation(10, 4, 10))

    # =====================================================================================
    # Output Meeting
    # =====================================================================================
    m = Array{MeetingOutput, 1}()
    count = 0
    for i in eachindex(meetings)
        pratica = meetings[i].isPractical
        dia = meetings[i].dayOfWeek
        codigoDisciplina = meetings[i].subjectID
        codigosTurma = meetings[i].classesIDs
        horarios = meetings[i].schedules

        pos = 0
        for j in eachindex(classes)
            if string(codigoDisciplina, "-", codigosTurma[1]) == string(classes[j].subjectID, "-", classes[j].classID)
                pos = j
                break
            end
        end

        if pos == 0
            continue
        end

        x = MeetingOutput(pratica, dia, classes[pos].vacancies, classes[pos].demand, codigoDisciplina, codigosTurma, horarios, [])
        push!(m, x)
    end

    matriz = Array{Cell, 1}(undef, length(schedules))
    for i = 1:length(schedules)
        x = Cell(false, [])
        matriz[i] = deepcopy(x)
    end

    pwt = Array{ProfessorWorkTime, 1}()
    for i in eachindex(professors)
        x = ProfessorWorkTime(professors[i].code, deepcopy(matriz), deepcopy(matriz), deepcopy(matriz), deepcopy(matriz), deepcopy(matriz), deepcopy(matriz))
        push!(pwt, x)
    end

    for i in eachindex(m)
        h = meetings[i].schedules
        alocou = false
        while alocou == false
            x = rand(1:length(pwt))

            if m[i].dayOfWeek == 2
                day = pwt[x].monday
            elseif m[i].dayOfWeek == 3
                day = pwt[x].thursday
            elseif m[i].dayOfWeek == 4
                day = pwt[x].wednesday
            elseif m[i].dayOfWeek == 5
                day = pwt[x].tuesday
            elseif m[i].dayOfWeek == 6
                day = pwt[x].friday
            elseif m[i].dayOfWeek == 7
                day = pwt[x].saturday
            else
            end

            ocupado = false
            for j in eachindex(m[i].schedules)
                if day[m[i].schedules[j]].working == true
                    ocupado = true
                    break
                end
            end

            if ocupado == false
                push!(m[i].professors, pwt[x].ID)
                for j in eachindex(m[i].schedules)
                    day[m[i].schedules[j]].working = true
                    push!(day[m[i].schedules[j]].meetings, i)
                end
                alocou = true
            end

        end
    end

    pwt_2 = Array{ProfessorWorkTime, 1}()
    for i in eachindex(professors)
        x = ProfessorWorkTime(professors[i].code, deepcopy(matriz), deepcopy(matriz), deepcopy(matriz), deepcopy(matriz), deepcopy(matriz), deepcopy(matriz))
        push!(pwt_2, x)
    end

    for i in eachindex(m)
        pos = 0
        for j in eachindex(pwt_2)
            if m[i].professors[1] == pwt_2[j].ID
                pos = j
                break
            end
        end

        if m[i].dayOfWeek == 2
            day = pwt_2[pos].monday
        elseif m[i].dayOfWeek == 3
            day = pwt_2[pos].thursday
        elseif m[i].dayOfWeek == 4
            day = pwt_2[pos].wednesday
        elseif m[i].dayOfWeek == 5
            day = pwt_2[pos].tuesday
        elseif m[i].dayOfWeek == 6
            day = pwt_2[pos].friday
        elseif m[i].dayOfWeek == 7
            day = pwt_2[pos].saturday
        else
        end

        for j in eachindex(m[i].schedules)
            if day[m[i].schedules[j]].working == true
                println(length(day[m[i].schedules[j]].meetings))
                for k in eachindex(day[m[i].schedules[j]].meetings)
                    println(m[day[m[i].schedules[j]].meetings[k]])
                    println(m[i])
                end
                println("AAAAAAAAAAAAAAAAAAA")
            end
            day[m[i].schedules[j]].working = true
            push!(day[m[i].schedules[j]].meetings, i)
        end

        # for j in eachindex(m[i].schedules)
        #     if m[i].dayOfWeek == 2

        #         if pwt_2[pos].monday[m[i].schedules[j]].working == true
        #             println(length(pwt_2[pos].monday[m[i].schedules[j]].meetings))
        #             for k in eachindex(pwt_2[pos].monday[m[i].schedules[j]].meetings)
        #                 println(m[pwt_2[pos].monday[m[i].schedules[j]].meetings[k]])
        #                 println(m[i])
        #             end
        #             println("AAAAAAAAAAAAAAAAAAA")
        #         end
        #         pwt_2[pos].monday[m[i].schedules[j]].working = true
        #         push!(pwt_2[pos].monday[m[i].schedules[j]].meetings, i)

        #     elseif m[i].dayOfWeek == 3

        #         if pwt_2[pos].thursday[m[i].schedules[j]].working == true
        #             println(length(pwt_2[pos].thursday[m[i].schedules[j]].meetings))
        #             for k in eachindex(pwt_2[pos].thursday[m[i].schedules[j]].meetings)
        #                 println(m[pwt_2[pos].thursday[m[i].schedules[j]].meetings[k]])
        #                 println(m[i])
        #             end
        #             println("AAAAAAAAAAAAAAAAAAA")
        #         end
        #         pwt_2[pos].thursday[m[i].schedules[j]].working = true
        #         push!(pwt_2[pos].thursday[m[i].schedules[j]].meetings, i)

        #     elseif m[i].dayOfWeek == 4

        #         if pwt_2[pos].wednesday[m[i].schedules[j]].working == true
        #             println(length(pwt_2[pos].wednesday[m[i].schedules[j]].meetings))
        #             for k in eachindex(pwt_2[pos].wednesday[m[i].schedules[j]].meetings)
        #                 println(m[pwt_2[pos].wednesday[m[i].schedules[j]].meetings[k]])
        #                 println(m[i])
        #             end
        #             println("AAAAAAAAAAAAAAAAAAA")
        #         end
        #         pwt_2[pos].wednesday[m[i].schedules[j]].working = true
        #         push!(pwt_2[pos].wednesday[m[i].schedules[j]].meetings, i)

        #     elseif m[i].dayOfWeek == 5

        #         if pwt_2[pos].tuesday[m[i].schedules[j]].working == true
        #             println(length(pwt_2[pos].tuesday[m[i].schedules[j]].meetings))
        #             for k in eachindex(pwt_2[pos].tuesday[m[i].schedules[j]].meetings)
        #                 println(m[pwt_2[pos].tuesday[m[i].schedules[j]].meetings[k]])
        #                 println(m[i])
        #             end
        #             println("AAAAAAAAAAAAAAAAAAA")
        #         end
        #         pwt_2[pos].tuesday[m[i].schedules[j]].working = true
        #         push!(pwt_2[pos].tuesday[m[i].schedules[j]].meetings, i)

        #     elseif m[i].dayOfWeek == 6

        #         if pwt_2[pos].friday[m[i].schedules[j]].working == true
        #             println(length(pwt_2[pos].friday[m[i].schedules[j]].meetings))
        #             for k in eachindex(pwt_2[pos].friday[m[i].schedules[j]].meetings)
        #                 println(m[pwt_2[pos].friday[m[i].schedules[j]].meetings[k]])
        #                 println(m[i])
        #             end
        #             println("AAAAAAAAAAAAAAAAAAA")
        #         end
        #         pwt_2[pos].friday[m[i].schedules[j]].working = true
        #         push!(pwt_2[pos].friday[m[i].schedules[j]].meetings, i)

        #     elseif m[i].dayOfWeek == 7

        #         if pwt_2[pos].saturday[m[i].schedules[j]].working == true
        #             println(length(pwt_2[pos].saturday[m[i].schedules[j]].meetings))
        #             for k in eachindex(pwt_2[pos].saturday[m[i].schedules[j]].meetings)
        #                 println(m[pwt_2[pos].saturday[m[i].schedules[j]].meetings[k]])
        #                 println(m[i])
        #             end
        #             println("AAAAAAAAAAAAAAAAAAA")
        #         end
        #         pwt_2[pos].saturday[m[i].schedules[j]].working = true
        #         push!(pwt_2[pos].saturday[m[i].schedules[j]].meetings, i)

        #     else
        #     end
        # end
    end

    # =====================================================================================
    # Escrevendo os dados no novo JSON
    # =====================================================================================

    output = open("../../JSON/newModel.json", "w")

    final_dict = OrderedDict("schedules" => schedules, "buildings" => buildings, "classrooms" => classrooms, "professors" => professors, "subjects" => subjects, "meetings" => m, "preferences" => preferences, "restrictions" => restrictions, "reservations" => reservations)
    # final_dict = OrderedDict("schedules" => schedules, "buildings" => buildings, "classrooms" => classrooms, "professors" => professors, "subjects" => subjects, "classes" => classes, "meetings" => meetings, "preferences" => preferences, "restrictions" => restrictions, "reservations" => reservations)
    data = JSON.json(final_dict)
    write(output, data)
    close(output)
    
end

main()