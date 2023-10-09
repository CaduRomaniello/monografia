using JSON
using OrderedCollections
include("structs.jl")

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
        codigosTurma = [String(split(dados["encontros"][i]["codTurma"], "-")[2])]
        horarios = []
        for j = 1:length(dados["encontros"][i]["horarios"])
            push!(horarios, dados["encontros"][i]["horarios"][j]["codigo"])
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
    push!(restrictions, Restriction("turma", "MED011-11", 1, nothing, nothing, nothing))
    
    # =====================================================================================
    # Reservas
    # =====================================================================================
    reservations = Array{Reservation, 1}()
    push!(reservations, Reservation(2, 3, 4))
    push!(reservations, Reservation(5, 6, 6))
    push!(reservations, Reservation(5, 6, 7))
    push!(reservations, Reservation(10, 4, 10))

    # =====================================================================================
    # Escrevendo os dados no novo JSON
    # =====================================================================================

    output = open("../../JSON/newInstance.json", "w")

    final_dict = OrderedDict("schedules" => schedules, "buildings" => buildings, "classrooms" => classrooms, "professors" => professors, "subjects" => subjects, "classes" => classes, "meetings" => meetings, "preferences" => preferences, "restrictions" => restrictions, "reservations" => reservations)
    data = JSON.json(final_dict)
    write(output, data)
    close(output)
    
end

main()