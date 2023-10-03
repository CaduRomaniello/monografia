using JSON

function toCSV()

    idleness::Array = []
    deallocated = []
    lessThan10 = []
    moreThan10 = []
    preferences = []
    professors = []
    
    
    maxIdleness = -1000000
    minIdleness = 1000000
    maxdeallocated = -1000000
    mindeallocated = 1000000
    maxlessThan10 = -1000000
    minlessThan10 = 1000000
    maxmoreThan10 = -1000000
    minmoreThan10 = 1000000
    maxpreferences = -1000000
    minpreferences = 1000000
    maxprofessors = -1000000
    minprofessors = 1000000

    

    for i = 1 : 150

        data = nothing
        try
            data = JSON.parse(open("./newModel/solution_seed-$(i)_maxTime-600.json"))
        catch
            println("Cannot open file")
            exit(1)
        end

        push!(idleness, data["objectives"]["idleness"])
        push!(deallocated, data["objectives"]["deallocated"])
        push!(lessThan10, data["objectives"]["lessThan10"])
        push!(moreThan10, data["objectives"]["moreThan10"])
        push!(preferences, data["objectives"]["preferences"])
        push!(professors, data["objectives"]["professors"])

        if data["objectives"]["idleness"] > maxIdleness
            maxIdleness = data["objectives"]["idleness"]
        end
        if data["objectives"]["idleness"] < minIdleness
            minIdleness = data["objectives"]["idleness"]
        end

        if data["objectives"]["deallocated"] > maxdeallocated
            maxdeallocated = data["objectives"]["deallocated"]
        end
        if data["objectives"]["deallocated"] < mindeallocated
            mindeallocated = data["objectives"]["deallocated"]
        end

        if data["objectives"]["lessThan10"] > maxlessThan10
            maxlessThan10 = data["objectives"]["lessThan10"]
        end
        if data["objectives"]["lessThan10"] < minlessThan10
            minlessThan10 = data["objectives"]["lessThan10"]
        end

        if data["objectives"]["moreThan10"] > maxmoreThan10
            maxmoreThan10 = data["objectives"]["moreThan10"]
        end
        if data["objectives"]["moreThan10"] < minmoreThan10
            minmoreThan10 = data["objectives"]["moreThan10"]
        end

        if data["objectives"]["preferences"] > maxpreferences
            maxpreferences = data["objectives"]["preferences"]
        end
        if data["objectives"]["preferences"] < minpreferences
            minpreferences = data["objectives"]["preferences"]
        end

        if data["objectives"]["professors"] > maxprofessors
            maxprofessors = data["objectives"]["professors"]
        end
        if data["objectives"]["professors"] < minprofessors
            minprofessors = data["objectives"]["professors"]
        end
    end

    # if less
    #     println("less tem valor maior que 0")
    # end
    # if more
    #     println("more tem valor maior que 0")
    # end

    # exit()

    # Abrindo o arquivo CSV que irá armazenar os dados para analise
    arqCSV = open("geral.csv", create=true, write=true)
    write(arqCSV, "position,idleness,deallocated,lessThan10,moreThan10,preferences,professors\n")

    for i in eachindex(idleness)
        write(arqCSV, "$(i),$((idleness[i] - minIdleness)/(maxIdleness - minIdleness)),$((deallocated[i] - mindeallocated)/(maxdeallocated - mindeallocated)),$((lessThan10[i] - minlessThan10)/(maxlessThan10 - minlessThan10)),$((moreThan10[i] - minmoreThan10)/(maxmoreThan10 - minmoreThan10)),$((preferences[i] - minpreferences)/(maxpreferences - minpreferences)),$((professors[i] - minprofessors)/(maxprofessors - minprofessors))\n")
    end

    close(arqCSV)
end

toCSV()