def automaton_F1(prob, alpha, beta, pos):

    nova_prob = prob[pos] + (alpha * beta * (1 - prob[pos])) - (alpha * (1 - beta) * prob[pos])
    prob[pos] = nova_prob

def automaton_F2(prob, alpha, beta, pos):

    nova_prob = prob[pos] - (alpha * beta * prob[pos]) + (alpha * (1 - beta) * ((1 / (len(prob) - 1)) - prob[pos]))
    prob[pos] = nova_prob