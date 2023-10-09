function custoPreferencia(meeting::SolutionMeeting, classroom::Classroom)
    x = 0
    if (classroom.ID != 0)
        for i in eachindex(meeting.preferences)
            if (meeting.preferences[i].building !== nothing)
                if (meeting.preferences[i].building != classroom.buildingID)
                    x += 10
                end
            end
            if (meeting.preferences[i].floor !== nothing)
                if (meeting.preferences[i].floor != classroom.floor)
                    x += 10
                end
            end
            if (meeting.preferences[i].board !== nothing)
                if (meeting.preferences[i].board != classroom.board)
                    x += 10
                end
            end
            if (meeting.preferences[i].projector !== nothing)
                if (meeting.preferences[i].projector != classroom.projector)
                    x += 10
                end
            end
        end
        return x
    else
        for i in eachindex(meeting.preferences)
            if (meeting.preferences[i].building !== nothing)
                x += 10
            end
            if (meeting.preferences[i].floor !== nothing)
                x += 10
            end
            if (meeting.preferences[i].board !== nothing)
                x += 10
            end
            if (meeting.preferences[i].projector !== nothing)
                x += 10
            end
        end
        return x
    end
end

function calculaCusto(encontros, salas, prefs)
    
    custo = zeros(Int64, length(encontros), length(salas) + 1)

    for i = 1:length(encontros)
        for j = 1:length(salas)
            x = 0

            demand = encontros[i].demand
            capacity = salas[j].capacity

            if demand <= capacity
                if (capacity - demand) > round(capacity / 2, RoundDown)
                    x = ((capacity - demand) - round(capacity / 2, RoundDown))
                end
            else
                notAttended = demand - capacity
                percentage = (demand * 10) / 100
                percentage = round(percentage, RoundDown)
                if (notAttended <= percentage)
                    x = notAttended * 10
                else
                    x = ((notAttended - percentage) * 100) + (percentage * 10)
                end
            end

            x += custoPreferencia(encontros[i], salas[j])
            custo[i, j] = x
            
        end
        custo[i, length(salas) + 1] = Int(encontros[i].demand) * 100
    end

    return custo

end

function restricao_horario(ehs, salas, horarios_agrupados, posicao)
    
    cont = 0

    if (length(horarios_agrupados) == 0)
        return cont
    end

    for i = 1:length(horarios_agrupados)

        for j = 1:length(salas)

            if (ehs[posicao + 1, j, horarios_agrupados[i][1]] != ehs[posicao + 1, j, horarios_agrupados[i][2]])
                cont += 1
                return cont
            end

        end

    end

    return cont

end

function reservado(reservas, sala, horario, dia)

    for i = 1:length(reservas)
        if (dia == reservas[i].dayOfWeek)
            if (reservas[i].classroomID == sala)
                if (horario == reservas[i].scheduleID)
                    return true
                end
            end
        end
    end

    return false

end

function mipFunction(encontros, salas, horarios, prefs, reservas)
    
    py"""
    import numpy
    from mip import *
    def mipPy(encontros, salas, horarios, calculaCusto, restricao_horario, prefs, horarios_agrupados, reservas, reservado):
        
        m = Model()
        m.verbose = 0

        E = len(encontros)
        S = len(salas) + 1
        H = len(horarios)

        # encontros = vetor da estrutura encontros
        # salas = vetor da estrutura salas
        # horarios = vetor de horarios
        # calculaCusto = funcao que calcula o custo da alocacao do encontro 'e' na sala 's'
        # ehs = encontros X salas x horarios
        # custo = encontros X salas

        codigos_horarios = []
        for e in range(E):
            codigos_horarios.append([])
            for i in range(len(encontros[e].schedules)):
                codigos_horarios[e].append(encontros[e].schedules[i].ID)
                # print(encontros[e].schedules[i].ID, " ")

        ehs = []
        for e in range(E):
            ehs.append([])
            for s in range(S):
                ehs[e].append([])
                for h in range(H):
                    estaReservado = reservado(reservas, s + 1, h + 1, encontros[0].dayOfWeek)
                    if ((h + 1 in codigos_horarios[e]) and not estaReservado):
                        ehs[e][s].append(m.add_var(var_type=BINARY, name=f"x({e},{s},{h})"))
                    else:
                        ehs[e][s].append(0)


        # for e in range(E):
        #     c = 0
        #     codHorario = encontros[e].schedules[0].ID
        #     for s in range(S):
        #         if type(ehs[e][s][codHorario]) != int:
        #             c += 1
        #     print(c, end=', ')
        # print()

        # for e in range(E):
        #     for h in encontros[e].horarios:
        #         if encontros[e].cod_sala == 0:
        #             ehs[e][S - 1][h - 1].lb = 1.0
        #         else:
        #             ehs[e][encontros[e].cod_sala - 1][h - 1].lb = 1.0

        custo = calculaCusto(encontros, salas, prefs)
        # for e in range(E):
        #     print(encontros[e].ID, end=' - ')
        #     print(custo[e])
        # ehs = [[[m.add_var(var_type=BINARY) for h in range(H)] for s in range(S)] for e in range(E)]

        cod_horarios = []
        for e in range(E):
            aux = []
            for x in range(len(encontros[e].schedules)):
               aux.append(encontros[e].schedules[x].ID) 
            cod_horarios.append(aux)

        # m.objective = xsum(custo[e][s] * ehs[e][s][h - 1]  for e in range(E) for s in range(S) for h in cod_horarios[e])
        m.objective = xsum(custo[e][s] * ehs[e][s][cod_horarios[e][0] - 1]  for e in range(E) for s in range(S))
            
        for e in range(E):
            for h in cod_horarios[e]:
                m += xsum(ehs[e][s][h - 1] for s in range(S)) == 1


        # for e in range(E):
        #     for h in encontros[e].horarios:
        #         m += xsum(ehs[e][s][h - 1] for s in range(S)) <= 1

        for s in range(S - 1):
            for h in range(H):
                m += xsum(ehs[e][s][h] for e in range(E)) <= 1
                
        for e in range(E):
            for s in range(S):
                for h in range(len(horarios_agrupados[e])):
                    restricao = ehs[e][s][horarios_agrupados[e][h][0] - 1] == ehs[e][s][horarios_agrupados[e][h][1] - 1]
                    if not isinstance(restricao, bool):
                        m += ehs[e][s][horarios_agrupados[e][h][0] - 1] == ehs[e][s][horarios_agrupados[e][h][1] - 1]
                

        m.optimize()  
        m.write("mip_lb.lp")
        return m.objective_value
        # print("VALOR:")
        # print(m.objective_value)

        retorno = []

        # for e in range(E):
        #     aux = [encontros[e].cod, 0]
        #     for s in range(S - 1):
        #         if (ehs[e][s][encontros[e].horarios[0] - 1].x > 0.5):
        #             aux[1] = s + 1
        #     retorno.append(aux)

        aloc = []

        print(numpy.shape(ehs))
        print(E)
        for i in range(E):
            codHorario = encontros[i].schedules[0].ID - 1
            aux = [encontros[i].ID, 0]
            for j in range(S - 1):
                # print(ehs[e][j][codHorario])
                if type(ehs[e][j][codHorario]) != int and ehs[e][j][codHorario].x > 0.5:
                    print(ehs[e][j][codHorario].x)
                    aux[1] = j + 1
                    print(aux)
                    break
                    # if j == S - 1:
                    #     aloc.append((encontros[i].ID, 0))
                    # else:
                    #     aloc.append((encontros[i].ID, j))
            aloc.append(aux)
            
        # print(aloc)
        return aloc
    """
    
    horarios_agrupados = []
    for i = 1:length(encontros)
        aux = []
        for j = 1:length(encontros[i].schedules) - 1
            for k = j + 1:length(encontros[i].schedules)
                push!(aux, [encontros[i].schedules[j].ID, encontros[i].schedules[k].ID])
            end
        end
        push!(horarios_agrupados, aux)
    end

    # x = py"mipPy"(encontros, salas, horarios, calculaCusto, restricao_horario, prefs, horarios_agrupados, reservas, reservado)
    # return x
    return py"mipPy"(encontros, salas, horarios, calculaCusto, restricao_horario, prefs, horarios_agrupados, reservas, reservado)
end