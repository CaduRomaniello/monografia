#Esse arquivo contem os includes dos arquivos do programa e as bibliotecas utilizadas

# Julia Base Modules
using Base
using Base
using Random
using Printf
using JSON
using Dates
# using DataStructures
using Crayons
using OrderedCollections
# using LaTeXStrings
using XLSX
using PyCall

# Local Modules

include("lib/problemStructs.jl")
include("lib/solutionStructs.jl")
include("movements/deallocate.jl")
include("movements/replace.jl")
include("movements/swap.jl")
include("movements/shift.jl")
include("movements/allocate.jl")
include("functions/mip.jl")
include("functions/verifier.jl")
include("functions/learningAutomaton.jl")
include("functions/auxiliarFunctions.jl")
include("functions/readFunctions.jl")
include("functions/heuristics.jl")
include("pas.jl")