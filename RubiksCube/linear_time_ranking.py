"""
Implementation of a linear time ranking function, based on the algorithm described in the paper:
"Ranking and Unranking Permutations in Linear Time" by A. Ruskey and J. Sawada.
It is noted that the ranking function is inspired by the random permutation generator from the paper:
"Generating Random Permutations in Linear Time" by R. Durstenfeld.
"""


def swap(i, j, array):
    temp = array[i]
    array[i] = array[j]
    array[j] = temp


def unrank(n, r, pi):
    if n > 0:
        swap(pi[n - 1], pi[r % n], pi)
        unrank(n - 1, r // n, pi)


def rank(n, pi, pi_dual):
    if n == 1:
        return 0
    s = pi[n - 1]
    swap(pi[n - 1], pi[pi_dual[n - 1]], pi)
    swap(pi_dual[s], pi_dual[n - 1], pi_dual)
    return s + n * rank(n - 1, pi, pi_dual)


