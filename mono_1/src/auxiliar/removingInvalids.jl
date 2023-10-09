using JSON
using OrderedCollections
using Random
include("structs.jl")

function main()
    dir = pwd()
    dados = JSON.parse(open("$(dir)/../../JSON/newInstance_2.json"))

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

        codigo = dados["professors"][i]["ID"]
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

        codigo = dados["subjects"][i]["ID"]
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

        codigoDisciplina = dados["classes"][i]["subjectID"]
        codigoTurma = dados["classes"][i]["classID"]
        vagas = dados["classes"][i]["vacancies"]
        demanda = dados["classes"][i]["demand"]
        professores = []
        for j = 1:length(dados["classes"][i]["professors"])
            push!(professores, dados["classes"][i]["professors"][j])
        end
        
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
        codigoDisciplina = dados["meetings"][i]["subjectID"]
        codigosTurma = []
        for j = 1:length(dados["meetings"][i]["classesIDs"])
            push!(codigosTurma, dados["meetings"][i]["classesIDs"][j])
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
    # Retirando encontros sem turmas cadastradas
    # =====================================================================================

    positions = []
    for i in eachindex(meetings)
        temTurma = false
        codMeeting = string(meetings[i].subjectID, "-", meetings[i].classesIDs[1])
        for j in eachindex(classes)
            codClass = string(classes[j].subjectID, "-", classes[j].classID)
            if codMeeting == codClass
                temTurma = true
                break
            end
        end
        if !temTurma
            push!(positions, i)
        end
    end

    for i in eachindex(positions)
        splice!(meetings, positions[i] - (i - 1))
    end

    # =====================================================================================
    # Sorteando professores pra nao ter conflito de horarios
    # =====================================================================================

    matriz = Array{Cell, 1}(undef, length(schedules))
    for i in eachindex(schedules)
        aux = Cell(false, [])
        matriz[i] = deepcopy(aux)
    end

    pwt = Array{ProfessorWorkTime, 1}()
    for i in eachindex(professors)
        x = ProfessorWorkTime(professors[i].ID, deepcopy(matriz), deepcopy(matriz), deepcopy(matriz), deepcopy(matriz), deepcopy(matriz), deepcopy(matriz))
        push!(pwt, x)
    end

    posTurma = []
    for i in eachindex(meetings)
        codMeeting = string(meetings[i].subjectID, "-", meetings[i].classesIDs[1])
        for j in eachindex(classes)
            codClass = string(classes[j].subjectID, "-", classes[j].classID)
            if codMeeting == codClass
                push!(posTurma, j)
            end
        end
    end

    objectives = Array{Objective, 1}()
    for i in eachindex(meetings)
        x = Objective(meetings[i].isPractical, meetings[i].dayOfWeek, meetings[i].subjectID, meetings[i].classesIDs, meetings[i].schedules, classes[posTurma[i]].vacancies, classes[posTurma[i]].demand, [])
        push!(objectives, x)
    end

    for i in eachindex(objectives)
        horarios = objectives[i].schedules
        dia = objectives[i].dayOfWeek
        
        alocou = false
        for j in eachindex(pwt)
            x = 0
            if dia == 2
                x = pwt[j].monday
            elseif dia == 3
                x = pwt[j].tuesday
            elseif dia == 4
                x = pwt[j].wednesday
            elseif dia == 5
                x = pwt[j].thursday
            elseif dia == 6
                x = pwt[j].friday
            else
                x = pwt[j].saturday
            end

            ocupado = false
            for k in horarios
                if x[k].working
                    ocupado = true
                end
            end

            if !ocupado
                alocou = true
                for k in horarios
                    x[k].working = true
                    push!(x[k].meetings, i)
                end
                push!(objectives[i].professors, pwt[j].ID)
                break
            end
        end

        if !alocou
            println("Nao alocou")
        end
    end

    for i in eachindex(objectives)
        if length(objectives[i].professors) != 1
            println("ERRO")
        end
    end

    for i in eachindex(objectives)
        if objectives[i].professors[1] == "0"
            println("DEU MERDA")
        end
        # print(classes[posTurma[i]].professors, " - ")
        classes[posTurma[i]].professors = objectives[i].professors
        # println(classes[posTurma[i]].professors)
    end
    
    for i in eachindex(classes)
        if classes[i].professors[1] == "0"
            x = rand(1:length(professors))
            classes[i].professors[1] = professors[x].ID
        end
    end

    # =====================================================================================
    # Escrevendo os dados no novo JSON
    # =====================================================================================

    output = open("../../JSON/newInstance_3.json", "w")

    final_dict = OrderedDict("schedules" => schedules, "buildings" => buildings, "classrooms" => classrooms, "professors" => professors, "subjects" => subjects, "classes" => classes, "meetings" => meetings, "preferences" => preferences, "restrictions" => restrictions, "reservations" => reservations)
    data = JSON.json(final_dict)
    write(output, data)
    close(output)

end

main()