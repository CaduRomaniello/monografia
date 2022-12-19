# Personal module lib
include("modules.jl")

# Main functions
function main(ARGS)

    local args = ARGS

    # println(length(args))
    # mycommand = `echo hello`
    # println(typeof(mycommand))
    # sys(mycommand)
    
    if length(args) != 3
        println("ERROR: Too few arguments")
        println("To run the program type: ")
        println("julia [--color=yes] main.jl <instance.json> <seed> <time>")
        println("[ ] => optional parameters")
        println("< > => required parameters")
        println()
    else
        input1 = split(args[1], '.')
        seed = parse(Int, args[2])
        Random.seed!(seed)
        time = parse(Int, args[3])
        if (input1[2] != "json")
            println("Erro: Instance file must be a JSON file!.")
        else
            pas(args[1], time, seed)
        end
    end

end

if abspath(PROGRAM_FILE) == @__FILE__
    main(ARGS)
end