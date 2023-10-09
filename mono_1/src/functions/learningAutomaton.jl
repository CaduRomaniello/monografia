function automaton_F1(prob::Array, alpha::Float64, beta::Int64, pos::Int64)

    nova_prob = prob[pos] + (alpha * beta * (1 - prob[pos])) - (alpha * (1 - beta) * prob[pos])
    prob[pos] = nova_prob

end

function automaton_F2(prob::Array, alpha::Float64, beta::Int64, pos::Int64)

    nova_prob = prob[pos] - (alpha * beta * prob[pos]) + (alpha * (1 - beta) * ((1 / (length(prob) - 1)) - prob[pos]))
    prob[pos] = nova_prob

end